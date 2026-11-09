"""Lesson 8: words as numbers. A tiny next-word model, the great-great-grandparent of an LLM.

Its first real job on the robot: fixing typos. "put teh red blok in the bin" -> "put the red block in the bin".
For a misspelt word, try every word one typo away, and keep the one the next-word model thinks is most
likely to come after the previous word. That's exactly how your phone's keyboard guesses.
"""

import random
import re

STORY = """
the robot picks up the red block . the robot puts the red block in the bin .
the robot sees a cat . the robot stops . the cat walks away . the robot moves on .
the robot picks up the blue block . the robot puts the blue block in the bin .
the robot is happy . the room is tidy .
"""


def tokenize(text):
    """Lowercase the text and split it into tokens: words, plus "." as its own token.
    tokenize("The cat. Sat") -> ["the", "cat", ".", "sat"]
    Tip: re.findall(r"[a-z']+|\\.", text.lower())"""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


def count_bigrams(tokens):
    """Count which token follows which. Return a dict of dicts:
    counts[word][next_word] = how many times next_word came right after word."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


def next_word_probs(counts, word):
    """Turn counts[word] into probabilities that add up to 1. Return {} if word was never seen."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


def generate(counts, start, n, rng):
    """Start with [start] and repeatedly sample the next word using next_word_probs
    (use rng.choices(words, weights=probs)). Stop after n new words or if there are no options.
    Return the words joined with spaces."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


# ---------------- the robot's first use for it: fixing typos ----------------

LETTERS = "abcdefghijklmnopqrstuvwxyz"

# Typos people really make, and what they meant. Used to test the fixer.
TYPO_COMMANDS = [
    ("put teh red blok in the bin", "put the red block in the bin"), ("go to the bleu block", "go to the blue block"),
    ("whre is the green block", "where is the green block"), ("fnd the red block", "find the red block"),
    ("stpo", "stop"), ("put the gren block away", "put the green block away"),
    ("thorw away the blue block", "throw away the blue block"), ("head to the red blokc", "head to the red block"),
    ("put the red bclok away", "put the red block away"),   # TWO typos in one word: one edit can't reach it
]


def edits1(word):
    """Every string ONE typo away from word: delete one letter, swap two neighbouring letters,
    replace one letter (with any of LETTERS), or insert one letter (anywhere). Return a set."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


def known_words(counts):
    """Every word the bigram counts have seen, either before or after another word."""
    return set(counts) | {w for nxt in counts.values() for w in nxt}


def fix_word(word, prev, counts, known):
    """Keep word if it's in known. Otherwise look at the known words in edits1(word):
      - if any of them has been seen right after prev, pick the one with the highest next_word_probs(counts, prev)
      - otherwise pick the one that starts the most bigrams (sum(counts.get(w, {}).values()), ties -> alphabetical first)
      - if there are none, keep word as it is."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


def fix_typos(text, counts):
    """Fix each token of tokenize(text) with fix_word, using the previously FIXED word as prev
    (start with prev = "."). Return the fixed tokens joined with spaces."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 8: write this function")


if __name__ == "__main__":
    tokens = tokenize(STORY)
    counts = count_bigrams(tokens)
    print("after 'robot':", {w: round(p, 2) for w, p in next_word_probs(counts, "robot").items()})
    rng = random.Random(4)
    for _ in range(3):
        print("->", generate(counts, "the", 12, rng))

    print("\nFixing typos with the robot's command words (from Lesson 9's examples):")
    from lesson09_commands import TRAIN
    cmd_counts = count_bigrams(tokenize(" . ".join(t for t, _ in TRAIN)))
    fixed = 0
    for typo, meant in TYPO_COMMANDS:
        f = fix_typos(typo, cmd_counts)
        fixed += f == meant
        print(f"  {typo!r:32} -> {f!r}{'' if f == meant else '   (wanted ' + repr(meant) + ')'}")
    print(f"fixed {fixed} of {len(TYPO_COMMANDS)}")
