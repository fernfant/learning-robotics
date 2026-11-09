"""Lesson 19 stretch: an AI model as the judge.

Our bake-off checks are EXACT: we look at what's in the bin, where the robot is, what it said.
That works because our world is tiny. For most real AI work (an essay, a chat reply, a summary)
there's no exact check, so companies ask another AI model to grade the answer: "LLM-as-a-judge".

Judges are useful AND dangerous. Before you trust one, measure it against checks you DO trust:
how often does it agree with our exact checks? Where does it disagree, and why?

The big lesson: a judge that only READS THE REPLY can be fooled by a confident robot.
"The blue block is in the bin!" sounds like success, even when you asked for the purple block.
Give the judge the EVIDENCE (what actually happened), and it can do much better.

Then two honesty tools (from Module 19, "Evals"):
  kappa: agreement beyond what a lazy judge gets for free. A judge that says "pass" to everything
         agrees often when most runs pass, and gets kappa 0.
  bootstrap_ci: an error bar. With only 12 tasks, "5/12" could easily have been 3/12 or 8/12.

    python3 lesson19_judge.py            offline: a reply-only rule judge vs the exact checks
    python3 lesson19_judge.py record     with an API key: Claude judges every run, two ways
"""

import json
import random
import sys
import time
from pathlib import Path

from world import ROBOT_START
from lesson19_bakeoff import TASKS, run_bakeoff

MODEL = "claude-opus-5-5"
RECORDINGS = Path(__file__).resolve().parent / "recordings"
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"verdict": {"type": "string", "enum": ["pass", "fail"]}, "reason": {"type": "string"}},
    "required": ["verdict", "reason"],
    "additionalProperties": False,
}


# ---------------- YOUR HOMEWORK ----------------

def evidence_text(frames):
    """Describe what ACTUALLY happened, from a run's recorded frames (first and last):
    "Robot started at (1, 1) and ended at (x, y). In the bin at the end: A, B (or nothing). It moved: yes/no."
    Positions are lists in frames; print them as tuples, e.g. (1, 1). Bin contents sorted, joined with ", "."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 19: write this function")


def judge_prompt(command, reply, evidence=None):
    """The text we send to the judge. It must contain the command and the reply, and, ONLY if evidence
    is given, a line starting "What actually happened: " followed by the evidence. End with the question:
    "Did the robot do the right thing? A correct robot does exactly what was asked, refuses impossible or
    unrelated requests without moving, and asks a question when the request is ambiguous." """
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 19: write this function")


def agreement(exact, judged):
    """exact and judged are equal-length lists of True/False verdicts.
    Return (fraction that agree, list of indices where they disagree)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 19: write this function")


def kappa(exact, judged):
    """Cohen's kappa: how much better than chance the judge agrees with the exact checks.
      observed = fraction that agree
      chance   = p_exact * p_judged + (1 - p_exact) * (1 - p_judged), where p_ = fraction marked True (pass)
      kappa    = (observed - chance) / (1 - chance), or 0.0 if chance is 1 (nothing to beat)
    0 means no better than guessing with the same pass rate; 1 means perfect."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 19: write this function")


def catch_rate(exact, judged):
    """Of the runs that really FAILED (exact is False), how many did the judge also fail?
    Return (caught, total_bad)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 19: write this function")


def bootstrap_ci(results, rounds=2000, seed=0):
    """A 95% error bar for the average of `results` (True/False, or numbers like -1/0/1).
    Repeat `rounds` times: pick len(results) items AT RANDOM WITH REPLACEMENT (rng.choice), take their average.
    Sort the averages; return (averages[int(0.025 * rounds)], averages[int(0.975 * rounds) - 1]).
    Use rng = random.Random(seed) so the answer is the same every run."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 19: write this function")


# ---------------- provided ----------------

def rule_judge(reply):
    """A cheap offline 'judge' that only reads the reply: pass if it sounds like success or a sensible question."""
    r = reply.lower()
    return not any(w in r for w in ("sorry", "can't", "cannot", "couldn't", "won't", "no recording", "not available"))


def ask_judge(client, prompt):
    """Ask Claude for a verdict, as checkable JSON. Returns (passed, reason, tokens_in, tokens_out)."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system="You are a strict, fair judge of a household robot's behaviour. Give a verdict and a one-sentence reason.",
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        return None, "judge refused", response.usage.input_tokens, response.usage.output_tokens
    out = json.loads(next(b.text for b in response.content if b.type == "text"))
    return out["verdict"] == "pass", out["reason"], response.usage.input_tokens, response.usage.output_tokens


def record(brain_names):
    import anthropic
    client = anthropic.Anthropic()
    _, traces = run_bakeoff(brain_names)
    out, tin, tout = {}, 0, 0
    for brain, runs in traces.items():
        for i, run in enumerate(runs):
            for mode in ("reply-only", "with-evidence"):
                ev = evidence_text(run["frames"]) if mode == "with-evidence" else None
                passed, reason, a, b = ask_judge(client, judge_prompt(run["command"], run["reply"], ev))
                tin, tout = tin + a, tout + b
                out.setdefault(brain, {}).setdefault(mode, []).append({"task": i, "passed": passed, "reason": reason})
                print(f"[{mode:13}] {brain.split(' (')[0]:8} task {i + 1:2}: {passed}  {reason[:70]}")
    RECORDINGS.mkdir(exist_ok=True)
    (RECORDINGS / "judge.json").write_text(json.dumps({"model": MODEL, "recorded": time.strftime("%Y-%m-%d"),
                                                       "tokens_in": tin, "tokens_out": tout, "verdicts": out}, indent=1))


if __name__ == "__main__":
    brains = ["words", "tinylm", "distilled", "planner-replay", "agent-replay"]
    if sys.argv[1:2] == ["record"]:
        record(brains)
        sys.exit()
    _, traces = run_bakeoff(brains)
    path = RECORDINGS / "judge.json"
    claude = json.loads(path.read_text())["verdicts"] if path.exists() else {}
    for brain, runs in traces.items():
        exact = [r["passed"] for r in runs]
        print(f"\n{brain}: exact checks pass {sum(exact)}/{len(exact)}")
        judges = [("rule judge, reply only", [rule_judge(r["reply"]) for r in runs])]
        for mode in ("reply-only", "with-evidence"):
            if brain in claude:
                judges.append((f"Claude judge, {mode}", [v["passed"] for v in claude[brain][mode]]))
        for name, verdicts in judges:
            rate, diff = agreement(exact, verdicts)
            caught, bad = catch_rate(exact, verdicts)
            print(f"  {name:28} agrees {rate:4.0%}  kappa {kappa(exact, verdicts):5.2f}  caught {caught}/{bad} failures"
                  f"   disagrees on tasks {[i + 1 for i in diff] or '-'}")
        print(f"  {'(lazy judge: always pass)':28} agrees {sum(exact) / len(exact):4.0%}  kappa  0.00")
    if not claude:
        print("\n(no Claude judge recordings yet: run `python3 lesson19_judge.py record` with an API key)")
    print("\nHonest numbers: each score with a 95% error bar (bootstrap over the 12 tasks)")
    for brain, runs in traces.items():
        lo, hi = bootstrap_ci([r["passed"] for r in runs])
        print(f"  {brain:28} {sum(r['passed'] for r in runs):2}/{len(runs)}   somewhere between {lo:4.0%} and {hi:4.0%}")
    (a, ra), *others = list(traces.items())
    for b, rb in others:
        d = [int(y["passed"]) - int(x["passed"]) for x, y in zip(ra, rb)]
        lo, hi = bootstrap_ci(d)
        print(f"  paired: {b.split(' (')[0]} minus {a.split(' (')[0]} = {sum(d) / len(d):+.0%} [{lo:+.0%}, {hi:+.0%}]  "
              f"(they differ on {sum(x != 0 for x in d)} task(s); {'too close to call' if lo <= 0 <= hi else 'a real difference'})")
    run = traces[next(iter(traces))][1]
    print("\nExample judge prompt WITH evidence:\n" + judge_prompt(run["command"], run["reply"], evidence_text(run["frames"])))
