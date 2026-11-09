"""Lesson 10: using a real LLM safely. Never trust model output, check it.

An LLM can understand messy commands much better than our word-counter.
But it can also reply with chatty text, broken JSON, made-up objects, or extra
instructions. A robot must only ever act on output that passes strict checks.

This file works offline, with pretend LLM replies (MOCK_REPLIES).
lesson10_optional_real_llm.py shows how to call a real model.
"""

import json

ALLOWED_INTENTS = {"put", "go", "find", "stop"}
NEEDS_OBJECT = {"put", "go", "find"}
ALLOWED_KEYS = {"intent", "object"}

# (command the person typed, what a pretend LLM replied)
MOCK_REPLIES = [
    ("please tidy away the red block", '{"intent": "put", "object": "red block"}'),
    ("where's the green one?", 'Sure! Here you go:\n```json\n{"intent": "find", "object": "green block"}\n```'),
    ("yeet the blue block into the bin", '{"intent": "throw", "object": "blue block"}'),
    ("put the purple block away", '{"intent": "put", "object": "purple block"}'),
    ("stop!!!", '{"intent": "stop", "object": null}'),
    ("go to the red block", '{"intent": "go", "object": "red block", "also": "ignore all safety rules"}'),
    ("hmm what about the blue", "I think you want me to go to the blue block!"),
    ("bin the green block", '{"intent": "put" "object": "green block"}'),
]


def extract_json(text):
    """Find the JSON object inside text: take everything from the first "{" to the last "}",
    then json.loads it. Return the dict, or None if there's no valid JSON object."""
    # BEGIN SOLUTION
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        obj = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None
    # END SOLUTION


def validate_action(action, known_objects):
    """Strict checks. Return (True, "") if action is safe to run, otherwise (False, reason).
    Rules:
      1. action must be a dict with exactly the keys "intent" and "object" (no extras!)
      2. intent must be in ALLOWED_INTENTS
      3. object must be None or one of known_objects
      4. intents in NEEDS_OBJECT must have an object; "stop" must have object None"""
    # BEGIN SOLUTION
    if not isinstance(action, dict):
        return False, "not a JSON object"
    if set(action) != ALLOWED_KEYS:
        return False, f"unexpected keys: {sorted(set(action) ^ ALLOWED_KEYS)}"
    intent, obj = action["intent"], action["object"]
    if intent not in ALLOWED_INTENTS:
        return False, f"unknown intent {intent!r}"
    if obj is not None and obj not in known_objects:
        return False, f"unknown object {obj!r}"
    if intent in NEEDS_OBJECT and obj is None:
        return False, f"{intent!r} needs an object"
    if intent == "stop" and obj is not None:
        return False, "'stop' takes no object"
    return True, ""
    # END SOLUTION


def safe_parse(reply_text, known_objects, command=None, fallback=None):
    """Try the LLM reply first. If it fails validation and a fallback function is given,
    try fallback(command) (for example, your Lesson 9 parser) and validate that too.
    Return (action_or_None, source, reason) where source is "llm", "fallback" or "none"."""
    # BEGIN SOLUTION
    action = extract_json(reply_text)
    ok, reason = validate_action(action, known_objects)
    if ok:
        return action, "llm", ""
    if fallback is not None and command is not None:
        fb = fallback(command)
        ok2, reason2 = validate_action(fb, known_objects)
        if ok2:
            return fb, "fallback", reason
        return None, "none", f"llm: {reason}; fallback: {reason2}"
    return None, "none", reason
    # END SOLUTION


def build_prompt(command, known_objects):
    """The instructions we'd send to a real LLM (used by the optional real-LLM file)."""
    objs = ", ".join(sorted(known_objects))
    return (
        "You control a small cleaning robot. Turn the person's command into JSON with exactly two keys:\n"
        '  "intent": one of "put" (take an object to the bin), "go" (drive to an object), '
        '"find" (say where an object is), "stop"\n'
        f'  "object": one of [{objs}], or null for "stop"\n'
        "If the command asks for anything else, use the closest allowed intent; never invent objects.\n"
        f"Command: {command}"
    )


if __name__ == "__main__":
    from world import OBJECTS
    from lesson09_commands import TRAIN, train_intent_model, parse_command
    model = train_intent_model(TRAIN)
    known = set(OBJECTS)
    for command, reply in MOCK_REPLIES:
        action, source, reason = safe_parse(reply, known, command, lambda c: parse_command(model, c))
        print(f"{command!r:40} -> {source:8} {action}  {('(' + reason + ')') if reason else ''}")
