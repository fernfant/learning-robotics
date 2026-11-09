"""All of Robo-Helper's possible brains, behind one interface. Provided for you.

    brain.act(robot, command) -> {"reply": str, "seconds": float, "tokens_in": int, "tokens_out": int}

Brains, in the order you build them (each one should make the robot better at something you can measure):
  words       Lesson 9's word counter: one action per command (week 5)
  tinylm      Lesson 15's tiny language model: writes whole plans, asks when unsure (week 6)
  attention   the same model with attention (week 6 stretch)
  distilled   the attention model re-trained with a teacher's labels on new phrasings (week 9)
  tinylm-4bit the distilled model squeezed to 4-bit numbers: 1/8 of the size (week 9)
  local     a small open model running on your own computer via Ollama (optional, illustrative)
  planner   a world-class model (Claude) that writes a whole checked plan        (needs an API key)
  agent     a world-class model (Claude) that uses robot tools step by step       (needs an API key)
  planner-replay / agent-replay   real recorded runs of the two above, replayed offline

Record real runs (needs a key):  python3 brains.py record
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

from lesson08_words import tokenize, count_bigrams, fix_typos
from lesson09_commands import TRAIN, train_intent_model, parse_command
from lesson10_llm_safety import extract_json, validate_action
from lesson15_tiny_lm import train_tiny_lm, words_to_plan
from lesson18_world_class import validate_plan, execute_tool, ask_planner, run_agent, SYSTEM, PLAN_SCHEMA

RECORDINGS = Path(__file__).resolve().parent / "recordings"
_counts = None


def clean(command):
    """Lesson 8's typo fixer, using every command the small brains were trained on. Runs in front of the small brains."""
    global _counts
    if _counts is None:
        from lesson15_tiny_lm import training_data
        _counts = count_bigrams(tokenize(" . ".join([t for t, _ in TRAIN] + [t for t, _ in training_data()])))
    try:
        return fix_typos(command, _counts)
    except NotImplementedError:
        return command


def run_plan(robot, plan_obj):
    """Run a validated plan step by step. Stops at the first failure. Returns the robot's messages."""
    messages = []
    for action in plan_obj["plan"]:
        result = robot.do_action(action)
        messages.append(result["message"])
        if not result["ok"]:
            break
    return messages


class WordsBrain:
    name = "words (Lesson 9)"

    def __init__(self):
        self.model = train_intent_model(TRAIN)

    def act(self, robot, command):
        action = parse_command(self.model, clean(command))
        ok, reason = validate_action(action, set(robot.objects))
        if not ok:
            robot.say(f"Sorry, I can't do that: {reason}")
            return {"reply": f"Sorry, I can't do that: {reason}"}
        return {"reply": robot.do_action(action)["message"]}


class TinyLMBrain:
    """Runs a plan-writing model (Lesson 15). Every action still goes through Lesson 10's safety check."""
    name = "tinylm (Lesson 15)"

    def __init__(self, model=None, name=None):
        self.model = model or train_tiny_lm()[0]
        self.name = name or self.name

    def act(self, robot, command):
        words = self.model.generate(clean(command))
        plan = words_to_plan(words)
        if plan is None:
            reply = f"Sorry, my answer made no sense ({' '.join(words) or 'nothing'})."
        elif plan == "none":
            reply = "Sorry, that's not something I can do."
        elif plan == "ask":
            reply = "Which block do you mean: red, blue or green?"
        else:
            known = set(robot.objects)
            bad = [r for ok, r in (validate_action(a, known) for a in plan) if not ok]
            if bad:
                reply = f"Sorry, I can't do that: {bad[0]}"
            else:
                return {"reply": " ".join(run_plan(robot, {"plan": plan}))}
        robot.say(reply)
        return {"reply": reply}


class PlannerBrain:
    name = "planner (Claude)"

    def __init__(self, client, recorder=None):
        self.client, self.recorder = client, recorder

    def act(self, robot, command):
        plan_obj, info = ask_planner(self.client, robot, command)
        if self.recorder is not None:
            self.recorder.append({"command": command, "raw": info.get("raw", ""), "seconds": info["seconds"],
                                  "tokens_in": info["tokens_in"], "tokens_out": info["tokens_out"]})
        return execute_plan_reply(robot, plan_obj, info)


def execute_plan_reply(robot, plan_obj, info):
    ok, reason = validate_plan(plan_obj, set(robot.objects))
    out = {"seconds": info["seconds"], "tokens_in": info["tokens_in"], "tokens_out": info["tokens_out"]}
    if not ok:
        robot.say(f"I won't run that plan: {reason}")
        out["reply"] = f"I won't run that plan: {reason}"
        return out
    if plan_obj["clarify"]:
        robot.say(plan_obj["clarify"])
        out["reply"] = plan_obj["clarify"]
        out["clarified"] = True
        return out
    robot.say(plan_obj["reply"])
    messages = run_plan(robot, plan_obj)
    out["reply"] = " ".join([plan_obj["reply"]] + messages)
    return out


class AgentBrain:
    name = "agent (Claude + tools)"

    def __init__(self, client, recorder=None):
        self.client, self.recorder = client, recorder

    def act(self, robot, command):
        text, info = run_agent(self.client, robot, command)
        robot.say(text)
        if self.recorder is not None:
            self.recorder.append({"command": command, "calls": [{"tool": c["tool"], "args": c["args"]} for c in info["calls"]],
                                  "final": text, "seconds": info["seconds"], "tokens_in": info["tokens_in"],
                                  "tokens_out": info["tokens_out"], "turns": info["turns"]})
        return {"reply": text, "seconds": info["seconds"], "tokens_in": info["tokens_in"], "tokens_out": info["tokens_out"]}


class ReplayBrain:
    """Replays a recorded real run: the same decisions, re-run through the same checks on a fresh robot.
    Because the simulator is deterministic, the robot behaves exactly as it did in the real run."""

    def __init__(self, kind):
        self.kind = kind
        self.name = f"{kind} (Claude, recorded)"
        path = RECORDINGS / f"{kind}.json"
        self.runs = {r["command"]: r for r in json.loads(path.read_text())["runs"]} if path.exists() else {}

    def act(self, robot, command):
        run = self.runs.get(command)
        if run is None:
            robot.say("(no recording for this command)")
            return {"reply": "(no recording for this command)", "missing": True}
        info = {k: run[k] for k in ("seconds", "tokens_in", "tokens_out")}
        if self.kind == "planner":
            return execute_plan_reply(robot, extract_json(run["raw"]) if run["raw"] else None, info)
        for call in run["calls"]:
            execute_tool(robot, call["tool"], call["args"], set(robot.objects))
        robot.say(run["final"])
        return {"reply": run["final"], **info}


class LocalBrain:
    """Illustrative: a small open model on your own computer via Ollama (https://ollama.com).
    Install Ollama, run `ollama pull llama3.2:1b`, keep Ollama running, then use --brain local."""
    name = "local (Ollama, small)"

    def __init__(self, model="llama3.2:1b", url="http://localhost:11434/api/chat"):
        self.model, self.url = model, url

    def act(self, robot, command):
        body = {"model": self.model, "stream": False, "format": PLAN_SCHEMA,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": f"Room: {robot.look()}\nPerson says: {command}"}]}
        start = time.perf_counter()
        try:
            req = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
        except OSError as e:
            robot.say(f"(local model not available: {e})")
            return {"reply": "(local model not available: is Ollama running?)", "missing": True}
        info = {"seconds": time.perf_counter() - start, "tokens_in": data.get("prompt_eval_count", 0),
                "tokens_out": data.get("eval_count", 0)}
        return execute_plan_reply(robot, extract_json(data.get("message", {}).get("content", "")), info)


def get_brain(name, recorder=None):
    if name == "words":
        return WordsBrain()
    if name == "tinylm":
        return TinyLMBrain()
    if name == "attention":
        from lesson15_attention import train_attn_lm
        return TinyLMBrain(train_attn_lm()[0], "attention (Lesson 15 stretch)")
    if name in ("distilled", "tinylm-4bit"):
        from lesson17_faster import distill_examples, UNLABELLED, best_teacher, best_student, quantized_copy
        model = best_student(distill_examples(UNLABELLED, best_teacher()))     # attention (if built) + a teacher's labels
        if name == "distilled":
            return TinyLMBrain(model, "distilled (Lesson 17)")
        return TinyLMBrain(quantized_copy(model, 4), "tinylm-4bit (Lesson 17)")
    if name == "local":
        return LocalBrain()
    if name in ("planner-replay", "agent-replay"):
        return ReplayBrain(name.split("-")[0])
    if name in ("planner", "agent"):
        import anthropic   # pip install anthropic, and set ANTHROPIC_API_KEY
        client = anthropic.Anthropic()
        return PlannerBrain(client, recorder) if name == "planner" else AgentBrain(client, recorder)
    raise ValueError(f"unknown brain {name!r}")


if __name__ == "__main__" and sys.argv[1:2] == ["record"]:
    from sim import run_brain
    from lesson19_bakeoff import TASKS
    RECORDINGS.mkdir(exist_ok=True)
    for kind in ("planner", "agent"):
        log = []
        brain = get_brain(kind, recorder=log)
        for task in TASKS:
            robot, result = run_brain(brain, task["command"], surprises=task.get("surprises", ((4, 1),)))
            print(f"[{kind}] {task['command']!r} -> {result['reply']!r}")
        (RECORDINGS / f"{kind}.json").write_text(json.dumps(
            {"model": "claude-opus-5-5", "recorded": time.strftime("%Y-%m-%d"), "runs": log}, indent=1))
    from sim import SimRobot
    from lesson17_faster import UNLABELLED
    planner, labels, spent = get_brain("planner"), {}, [0, 0]
    for c in UNLABELLED:
        plan_obj, info = ask_planner(planner.client, SimRobot(), c)
        spent[0] += info["tokens_in"]
        spent[1] += info["tokens_out"]
        ok = validate_plan(plan_obj, set(SimRobot().objects))[0]
        labels[c] = plan_obj["plan"][0]["intent"] if ok and plan_obj["plan"] and not plan_obj["clarify"] else None
        print(f"[teacher] {c!r} -> {labels[c]}")
    (RECORDINGS / "teacher_labels.json").write_text(json.dumps(
        {"model": "claude-opus-5-5", "recorded": time.strftime("%Y-%m-%d"), "tokens_in": spent[0],
         "tokens_out": spent[1], "labels": labels}, indent=1))
