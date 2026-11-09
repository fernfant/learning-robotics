"""Lesson 17 (Week 9): inference engineering, part 2. Making brains cheaper and faster.

Three tricks every AI company uses:

  CACHING       don't think twice about the same question. Remember answers, and reuse them.
                The catch: the answer must still be right. "where is the red block" has a
                different answer after the red block moves, so the WORLD must be part of the key.
  QUANTISING    store each weight with fewer bits. 32-bit floats -> 8-bit or 4-bit integers.
                4x to 8x smaller and faster, slightly less precise. Does the robot notice?
  DISTILLING    a big slow "teacher" model labels lots of examples; a small fast "student"
                learns from them. You keep (some of) the teacher's smarts at the student's speed.
                Lesson 13's LoRA is the cheap way to do the student's training on a big model.
"""

import copy
import json
from pathlib import Path

from lesson08_words import tokenize
from lesson15_tiny_lm import train_tiny_lm, accuracy, test_data, make_targets


# ---------------- YOUR HOMEWORK, part 1: caching ----------------

def cache_key(command, world):
    """Commands that mean the same must share a key, in the SAME world:
    lower-case words from tokenize(command), joined with single spaces, then "|" then the world text.
    cache_key("Put the RED block!", "w1") == "put the red block|w1" """
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 17: write this function")


class Cache:
    """Wraps any slow function think(command, world) -> answer, and remembers its answers."""

    def __init__(self, think):
        self.think, self.store, self.hits, self.misses = think, {}, 0, 0

    def ask(self, command, world):
        """If cache_key(command, world) is stored, count a hit and return the stored answer.
        Otherwise count a miss, call self.think(command, world), store the answer, and return it."""
        # TODO: write this part. Read the docstring above carefully.
        raise NotImplementedError("Lesson 17: write this function")

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


# ---------------- YOUR HOMEWORK, part 2: quantising ----------------

def quantize(values, bits):
    """Squash a list of floats into whole numbers between -(2**(bits-1) - 1) and +(2**(bits-1) - 1).
    scale = (biggest absolute value) / that top number   (use 1.0 if all values are 0)
    each q = round(v / scale).   Return (list_of_ints, scale)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 17: write this function")


def dequantize(qs, scale):
    """Back to floats: each q * scale."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 17: write this function")


# ---------------- provided: applying it to the Lesson 15 model ----------------

def weight_lists(model):
    """Every list of numbers inside a TinyLM (the rows of each table)."""
    return (list(model.word_emb.values()) + list(model.out_emb.values()) + model.W1 + [model.b1] + model.W2 + [model.b2])


def count_weights(model):
    return sum(len(row) for row in weight_lists(model))


def quantized_copy(model, bits):
    """A copy of the model where every row was quantised and dequantised (so it keeps working as floats,
    but only holds the values a `bits`-bit number can represent)."""
    m = copy.deepcopy(model)
    for row in weight_lists(m):
        row[:] = dequantize(*quantize(row, bits))
    return m


def size_bytes(n_weights, bits):
    return n_weights * bits / 8


# ---------------- YOUR HOMEWORK, part 3: distilling ----------------

def distill_examples(commands, teacher):
    """Ask the teacher about each command. teacher(command) returns an intent ("put", "go", "find", "stop")
    or None if it would refuse or ask a question. Keep only the commands with an intent.
    Return a list of (command, intent) pairs, ready for train_tiny_lm."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 17: write this function")


# New commands nobody labelled by hand. A teacher model labels them.
UNLABELLED = [
    "where's the red one", "where's the blue one", "locate the green block", "can you see the red block",
    "where did the blue block go", "find me the green one", "show me where the red block is",
    "is the green block still there", "chuck the blue block in the bin", "get rid of the red block",
    "bin the green one", "put away the red block", "head over to the green block", "move next to the red block",
    "come to the blue block", "visit the green block", "freeze", "wait stop", "hold it right there",
    "stop moving please", "pick up the blue block and bin it", "put the green one away",
    "where can i find the blue block", "take me to the red block",
]

# What a careful human would say. Used to show what a GOOD teacher does.
CAREFUL_HUMAN = dict(zip(UNLABELLED, ["find"] * 8 + ["put"] * 4 + ["go"] * 4 + ["stop"] * 4 + ["put", "put", "find", "go"]))

RECORDINGS = Path(__file__).resolve().parent / "recordings"


def recorded_teacher():
    """Claude's labels for UNLABELLED, recorded by `python3 brains.py record`. None if not recorded."""
    path = RECORDINGS / "teacher_labels.json"
    if not path.exists():
        return None
    labels = json.loads(path.read_text())["labels"]
    return lambda c: labels.get(c)


def best_student(extra=()):
    """The attention model (Lesson 15 stretch) if you built it, otherwise the plain tiny LM."""
    from lesson15_attention import train_attn_lm
    try:
        return train_attn_lm(extra)[0]
    except NotImplementedError:
        return train_tiny_lm(extra)[0]


def best_teacher():
    """Claude's recorded labels if you have them, otherwise the careful human's."""
    return recorded_teacher() or CAREFUL_HUMAN.get


if __name__ == "__main__":
    from lesson09_commands import TRAIN, train_intent_model, predict_intent

    print("1) CACHING. 6 commands in a world where nothing changes, then the red block moves.")
    calls = []
    slow = lambda c, w: calls.append(c) or f"answer to {c!r}"
    cache = Cache(slow)
    for c in ["put the red block in the bin", "Put the RED block in the bin!", "where is the blue block",
              "where is the blue block?", "stop", "STOP"]:
        cache.ask(c, "red at (2,1)")
    cache.ask("where is the red block", "red at (2,1)")
    cache.ask("where is the red block", "red in the bin")
    print(f"   real thinking calls: {len(calls)}, hit rate {cache.hit_rate():.0%}")

    print("\n2) QUANTISING the Lesson 15 attention model (the best small brain so far), and driving the robot with it.")
    from brains import TinyLMBrain
    from sim import run_brain, CAT
    from lesson19_bakeoff import TASKS, score_task

    def robot_score(model):
        brain = TinyLMBrain(model, "x")
        try:
            return sum(score_task(t, *run_brain(brain, t["command"], surprises=t.get("surprises", (CAT,))))[0] for t in TASKS)
        except NotImplementedError:
            return "?"   # needs Lesson 19's score_task (week 11): run ../progress.py for the robot score now

    model = best_student()
    n = count_weights(model)
    for bits in (32, 8, 4, 3, 2):
        m = model if bits == 32 else quantized_copy(model, bits)
        print(f"   {bits:2}-bit: {size_bytes(n, bits):7.0f} bytes   held-out plans {accuracy(m, test_data()):4.0%}"
              f"   robot bake-off {robot_score(m):2}/12")

    print("\n3) DISTILLING: the student learns from a teacher's labels on 24 new commands.")
    teachers = [("word counter (Lesson 9)", (lambda wm: lambda c: predict_intent(wm, c))(train_intent_model(TRAIN))),
                ("a careful human", CAREFUL_HUMAN.get)]
    claude = recorded_teacher()
    if claude:
        teachers.append(("Claude (recorded)", claude))
    else:
        print("   (no recorded Claude labels yet: run `python3 brains.py record` with an API key)")
    hard = make_targets([("where's the green one?", "find"), ("where's the red block", "find"), ("find the green block", "find"),
                         ("locate the blue block", "find"), ("bin the red one", "put"), ("halt", "stop")])
    print(f"   {'student (attention model) trained on':42} plans  hard-6  robot")
    print(f"   {'the usual data only':42} {accuracy(model, test_data()):4.0%}  {accuracy(model, hard):5.0%}  {robot_score(model):2}/12")
    for name, teacher in teachers:
        extra = distill_examples(UNLABELLED, teacher)
        student = best_student(extra)
        print(f"   {'+ ' + str(len(extra)) + ' labels from ' + name:42} {accuracy(student, test_data()):4.0%}  "
              f"{accuracy(student, hard):5.0%}  {robot_score(student):2}/12")
