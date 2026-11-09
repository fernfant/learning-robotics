"""Lesson 18 (Week 10): a world-class brain over the internet.

Two ways to use a big model (Claude) as Robo-Helper's brain:

  PLANNER: send the command + a description of the room, get back ONE checked plan
           (a list of actions), or a clarifying question. Then the robot runs the plan.
  AGENT:   give the model the robot's TOOLS (look, go_to, pick_up, put_in_bin).
           It calls them one at a time, sees what happened, and decides the next step.
           It can react to surprises, like a cat blocking the way.

Either way, YOU stay in charge: every plan and every tool call is checked before the robot moves.
Your homework is that checking code (validate_plan, execute_tool). The API code is provided.
Without an API key, the bake-off (Lesson 19) replays recorded real runs instead.
"""

import json
import time

from lesson10_llm_safety import validate_action

MODEL = "claude-opus-5-5"
PRICE_PER_MTOK = {"input": 4.00, "output": 20.00}   # US dollars per million tokens (Nov 2026)
OBJECT_NAMES = ["red block", "blue block", "green block"]
MAX_PLAN = 6

SYSTEM = """You are the brain of Robo-Helper, a small cleaning robot in a room with three blocks and a bin.
You can only: put a block in the bin ("put"), drive to a block ("go"), report where a block is ("find"), or "stop".
Rules:
- Only use the blocks listed in the room description. Never invent objects.
- If the person's request is ambiguous (for example "put the block away" when there are several), ask ONE short clarifying question instead of guessing.
- If the request is impossible or unrelated to tidying (for example "make me a sandwich"), politely say so and do nothing.
- Prefer doing exactly what was asked: don't bin blocks the person didn't ask about."""

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "clarify": {"type": ["string", "null"]},
        "plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intent": {"type": "string", "enum": ["put", "go", "find", "stop"]},
                    "object": {"type": ["string", "null"], "enum": OBJECT_NAMES + [None]},
                },
                "required": ["intent", "object"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reply", "clarify", "plan"],
    "additionalProperties": False,
}

TOOLS = [
    {"name": "look", "description": "Describe the room: robot position, what it holds, where each block is, what's in the bin, obstacles seen.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "go_to", "description": "Drive to a block. Replans around obstacles automatically; may fail if blocked.",
     "input_schema": {"type": "object", "properties": {"object": {"type": "string", "enum": OBJECT_NAMES}},
                      "required": ["object"], "additionalProperties": False}},
    {"name": "pick_up", "description": "Pick up a block. The robot must already be at the block.",
     "input_schema": {"type": "object", "properties": {"object": {"type": "string", "enum": OBJECT_NAMES}},
                      "required": ["object"], "additionalProperties": False}},
    {"name": "put_in_bin", "description": "Drive to the bin and drop the block being held.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
]


# ---------------- YOUR HOMEWORK: the safety checks ----------------

def validate_plan(plan_obj, known_objects):
    """Check a planner reply before the robot acts on it. Return (True, "") or (False, reason).
      1. plan_obj must be a dict with exactly the keys "reply", "clarify", "plan"
      2. "plan" must be a list with at most MAX_PLAN actions
      3. every action must pass Lesson 10's validate_action(action, known_objects)
      4. if "clarify" is a non-empty string, the plan must be EMPTY (ask first, act later)"""
    # BEGIN SOLUTION
    if not isinstance(plan_obj, dict) or set(plan_obj) != {"reply", "clarify", "plan"}:
        return False, "reply must have exactly the keys reply, clarify and plan"
    plan = plan_obj["plan"]
    if not isinstance(plan, list):
        return False, "plan must be a list"
    if len(plan) > MAX_PLAN:
        return False, f"plan too long ({len(plan)} > {MAX_PLAN})"
    for i, action in enumerate(plan):
        ok, reason = validate_action(action, known_objects)
        if not ok:
            return False, f"step {i + 1}: {reason}"
    if plan_obj["clarify"] and plan:
        return False, "asked a question AND gave a plan: ask first, act later"
    return True, ""
    # END SOLUTION


def execute_tool(robot, name, args, known_objects):
    """Run ONE tool call from the agent on the simulated robot, safely. Never crash: return (ok, text).
      - unknown tool name -> (False, "Unknown tool ...")
      - args must be a dict; go_to and pick_up need args["object"] in known_objects
      - "look"       -> (True, robot.look())
      - "go_to"      -> robot.go_to(obj)
      - "pick_up"    -> robot.pick_up(obj)
      - "put_in_bin" -> robot.put_in_bin()"""
    # BEGIN SOLUTION
    if not isinstance(args, dict):
        return False, "Tool arguments must be an object."
    if name == "look":
        return True, robot.look()
    if name == "put_in_bin":
        return robot.put_in_bin()
    if name in ("go_to", "pick_up"):
        obj = args.get("object")
        if obj not in known_objects:
            return False, f"Unknown object {obj!r}. Known: {sorted(known_objects)}"
        return robot.go_to(obj) if name == "go_to" else robot.pick_up(obj)
    return False, f"Unknown tool {name!r}. Allowed: look, go_to, pick_up, put_in_bin."
    # END SOLUTION


def cost_usd(tokens_in, tokens_out):
    return tokens_in / 1e6 * PRICE_PER_MTOK["input"] + tokens_out / 1e6 * PRICE_PER_MTOK["output"]


# ---------------- provided: talking to the real model ----------------

def describe_world(robot):
    return robot.look()


def ask_planner(client, robot, command):
    """One request: room description + command in, a JSON plan out (structured outputs).
    Returns (plan_obj or None, info). info has seconds, tokens_in, tokens_out, raw."""
    start = time.perf_counter()
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": PLAN_SCHEMA}},
        betas=["server-side-fallback-2026-07-01"],   # if the model declines, retry on a fallback model
        fallbacks="default",
        messages=[{"role": "user", "content": f"Room: {describe_world(robot)}\nPerson says: {command}"}],
    )
    info = {"seconds": time.perf_counter() - start,
            "tokens_in": response.usage.input_tokens, "tokens_out": response.usage.output_tokens}
    if response.stop_reason == "refusal":
        info["raw"] = ""
        return None, info
    raw = next((b.text for b in response.content if b.type == "text"), "")
    info["raw"] = raw
    try:
        return json.loads(raw), info
    except json.JSONDecodeError:
        return None, info


def run_agent(client, robot, command, max_turns=12):
    """The agent loop: the model calls tools, we check + run each one, send back the results,
    until it stops calling tools. Returns (final_text, info). info["calls"] lists every tool call."""
    known = set(robot.objects)
    messages = [{"role": "user", "content": f"Person says: {command}\nUse the tools. Start with look."}]
    info = {"seconds": 0.0, "tokens_in": 0, "tokens_out": 0, "calls": [], "turns": 0}
    start = time.perf_counter()
    final_text = ""
    for _ in range(max_turns):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=SYSTEM + "\nYou act through tools. When the job is done (or impossible), reply to the person in one short sentence.",
            output_config={"effort": "low"},
            tools=[{**t, "strict": True} for t in TOOLS],
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=messages,
        )
        info["turns"] += 1
        info["tokens_in"] += response.usage.input_tokens
        info["tokens_out"] += response.usage.output_tokens
        texts = [b.text for b in response.content if b.type == "text"]
        if texts:
            final_text = texts[-1]
        if response.stop_reason == "refusal":
            break
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            break
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in tool_uses:
            ok, text = execute_tool(robot, block.name, block.input, known)
            info["calls"].append({"tool": block.name, "args": block.input, "ok": ok, "result": text})
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": text, "is_error": not ok})
        messages.append({"role": "user", "content": results})
    info["seconds"] = time.perf_counter() - start
    return final_text, info


if __name__ == "__main__":
    # Offline demo of your safety checks (no API key needed).
    from sim import SimRobot
    known = set(OBJECT_NAMES)
    good = {"reply": "On it!", "clarify": None, "plan": [{"intent": "put", "object": "red block"}, {"intent": "put", "object": "blue block"}]}
    sneaky = {"reply": "Sure", "clarify": None, "plan": [{"intent": "put", "object": "the cat"}]}
    both = {"reply": "Which one?", "clarify": "Which block?", "plan": [{"intent": "put", "object": "red block"}]}
    for name, p in [("good", good), ("sneaky", sneaky), ("asks AND acts", both)]:
        print(f"{name:14} -> {validate_plan(p, known)}")
    robot = SimRobot()
    for call in [("look", {}), ("pick_up", {"object": "red block"}), ("go_to", {"object": "red block"}),
                 ("pick_up", {"object": "red block"}), ("put_in_bin", {}), ("self_destruct", {})]:
        print(f"{call[0]:12} {str(call[1]):24} -> {execute_tool(robot, *call, known)}")
