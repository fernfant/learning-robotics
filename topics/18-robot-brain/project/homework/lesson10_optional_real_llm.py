"""OPTIONAL: Lesson 10 with a real LLM. Not checked by check.py.

You need:
  1. pip install anthropic
  2. An Anthropic API key (ask a parent/guardian: it costs a little money per request),
     set as the environment variable ANTHROPIC_API_KEY.

The robot still only acts on output that passes validate_action(). The LLM is a helper,
not the boss.
"""

import json

import anthropic

from world import OBJECTS
from lesson09_commands import TRAIN, train_intent_model, parse_command
from lesson10_llm_safety import build_prompt, safe_parse

# Ask for JSON that matches this exact shape (structured outputs).
ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": ["put", "go", "find", "stop"]},
        "object": {"type": ["string", "null"]},
    },
    "required": ["intent", "object"],
    "additionalProperties": False,
}


def ask_llm(client, command):
    """Send one command to Claude and return its text reply ("" if it declined)."""
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=2000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": ACTION_SCHEMA}},
        # If the model declines a request, retry it on a fallback model automatically.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": build_prompt(command, set(OBJECTS))}],
    )
    if response.stop_reason == "refusal":
        return ""
    return next((b.text for b in response.content if b.type == "text"), "")


if __name__ == "__main__":
    client = anthropic.Anthropic()
    model = train_intent_model(TRAIN)
    known = set(OBJECTS)
    for command in ["please tidy away the red block", "where's the green one?",
                    "hmm, what about the blue one", "put the purple block away", "STOP!!"]:
        try:
            reply = ask_llm(client, command)
        except anthropic.APIConnectionError:
            print("Network error: check your internet connection.")
            break
        except anthropic.AuthenticationError:
            print("Your API key isn't working: check ANTHROPIC_API_KEY.")
            break
        except anthropic.APIStatusError as e:
            print(f"API error {e.status_code}: {e.message}")
            break
        action, source, reason = safe_parse(reply, known, command, lambda c: parse_command(model, c))
        print(f"{command!r:36} LLM said {reply!r}\n{'':36} -> {source}: {action} {reason}")
