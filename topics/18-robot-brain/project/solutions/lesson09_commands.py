"""Lesson 9: understanding commands. A word-counting classifier, plus "slots".

Intents (what the person wants):
    put   - take an object to the bin
    go    - drive to an object
    find  - say where an object is
    stop  - stop now
Slot: which object ("red block", "blue block", "green block"), or None.
"""

import math
import re

from lesson08_words import tokenize

TRAIN = [
    ("put the red block in the bin", "put"), ("throw the blue block away", "put"),
    ("tidy up the green block", "put"), ("put away the blue block", "put"),
    ("can you bin the red one", "put"), ("clean up the green block please", "put"),
    ("drop the blue block in the bin", "put"), ("get rid of the red block", "put"),
    ("move the green block into the bin", "put"), ("put the blue one in the trash", "put"),
    ("go to the red block", "go"), ("drive over to the blue block", "go"),
    ("head to the green block", "go"), ("go near the red one", "go"),
    ("move next to the blue block", "go"), ("travel to the green one", "go"),
    ("come to the red block", "go"), ("go over to the blue block please", "go"),
    ("where is the red block", "find"), ("find the blue block", "find"),
    ("can you tell me where the green block is", "find"), ("where did the blue one go", "find"),
    ("locate the red block", "find"), ("which square is the green block on", "find"),
    ("show me where the red one is", "find"), ("where is the blue block now", "find"),
    ("stop", "stop"), ("stop now", "stop"), ("halt", "stop"), ("freeze", "stop"),
    ("stop moving", "stop"), ("please stop right now", "stop"), ("emergency stop", "stop"),
    ("wait stop", "stop"),
]

TEST = [
    ("put the green block in the bin", "put"), ("bin the blue block", "put"),
    ("throw away the red block please", "put"), ("go to the green block", "go"),
    ("drive to the red one", "go"), ("head over to the blue block", "go"),
    ("where is the green one", "find"), ("find the red block for me", "find"),
    ("locate the blue block", "find"), ("stop please", "stop"), ("halt now", "stop"),
    ("freeze right there", "stop"),
]

COLOURS = ["red", "blue", "green"]


def train_intent_model(examples):
    """Count words per intent. Return a model dict:
        {"word_counts": {intent: {word: count}}, "intent_counts": {intent: n_examples}, "vocab": set_of_words}"""
    # BEGIN SOLUTION
    wc, ic, vocab = {}, {}, set()
    for text, intent in examples:
        ic[intent] = ic.get(intent, 0) + 1
        bucket = wc.setdefault(intent, {})
        for w in tokenize(text):
            bucket[w] = bucket.get(w, 0) + 1
            vocab.add(w)
    return {"word_counts": wc, "intent_counts": ic, "vocab": vocab}
    # END SOLUTION


def intent_scores(model, text):
    """Naive Bayes, in log space so tiny numbers don't vanish. For each intent:
        score = log(examples of intent / all examples)
              + sum over words in text of  log((count of word in intent + 1) / (total words in intent + vocab size))
    The "+1" means unseen words don't make the score -infinity. Return {intent: score}."""
    # BEGIN SOLUTION
    total = sum(model["intent_counts"].values())
    V = len(model["vocab"])
    scores = {}
    for intent, n in model["intent_counts"].items():
        words = model["word_counts"][intent]
        size = sum(words.values())
        s = math.log(n / total)
        for w in tokenize(text):
            s += math.log((words.get(w, 0) + 1) / (size + V))
        scores[intent] = s
    return scores
    # END SOLUTION


def predict_intent(model, text):
    """The intent with the highest score."""
    # BEGIN SOLUTION
    scores = intent_scores(model, text)
    return max(scores, key=scores.get)
    # END SOLUTION


def extract_object(text):
    """Find the object: look for a colour word from COLOURS. Return e.g. "red block", or None."""
    # BEGIN SOLUTION
    for w in tokenize(text):
        if w in COLOURS:
            return f"{w} block"
    return None
    # END SOLUTION


def parse_command(model, text):
    """Return {"intent": ..., "object": ...}. For "stop", object is always None."""
    # BEGIN SOLUTION
    intent = predict_intent(model, text)
    return {"intent": intent, "object": None if intent == "stop" else extract_object(text)}
    # END SOLUTION


def test_accuracy(model, examples):
    """Fraction of examples whose predicted intent matches the label."""
    # BEGIN SOLUTION
    return sum(predict_intent(model, t) == y for t, y in examples) / len(examples)
    # END SOLUTION


if __name__ == "__main__":
    model = train_intent_model(TRAIN)
    print("test accuracy:", round(test_accuracy(model, TEST), 2))
    for t in ["please put the red block in the bin", "where's the green one?", "STOP!"]:
        print(f"{t!r:42} -> {parse_command(model, t)}")
    wrong = [(t, y, predict_intent(model, t)) for t, y in TEST if predict_intent(model, t) != y]
    print("mistakes:", wrong or "none")
