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
    # BEGIN SOLUTION
    return re.findall(r"[a-z']+|\.", text.lower())
    # END SOLUTION


def count_bigrams(tokens):
    """Count which token follows which. Return a dict of dicts:
    counts[word][next_word] = how many times next_word came right after word."""
    # BEGIN SOLUTION
    counts = {}
    for a, b in zip(tokens, tokens[1:]):
        counts.setdefault(a, {})
        counts[a][b] = counts[a].get(b, 0) + 1
    return counts
    # END SOLUTION


def next_word_probs(counts, word):
    """Turn counts[word] into probabilities that add up to 1. Return {} if word was never seen."""
    # BEGIN SOLUTION
    nxt = counts.get(word, {})
    total = sum(nxt.values())
    return {w: c / total for w, c in nxt.items()} if total else {}
    # END SOLUTION


def generate(counts, start, n, rng):
    """Start with [start] and repeatedly sample the next word using next_word_probs
    (use rng.choices(words, weights=probs)). Stop after n new words or if there are no options.
    Return the words joined with spaces."""
    # BEGIN SOLUTION
    out = [start]
    for _ in range(n):
        probs = next_word_probs(counts, out[-1])
        if not probs:
            break
        words = list(probs)
        out.append(rng.choices(words, weights=[probs[w] for w in words])[0])
    return " ".join(out)
    # END SOLUTION


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
    # BEGIN SOLUTION
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    swaps = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits if b for c in LETTERS]
    inserts = [a + c + b for a, b in splits for c in LETTERS]
    return set(deletes + swaps + replaces + inserts)
    # END SOLUTION


def known_words(counts):
    """Every word the bigram counts have seen, either before or after another word."""
    return set(counts) | {w for nxt in counts.values() for w in nxt}


def fix_word(word, prev, counts, known):
    """Keep word if it's in known. Otherwise look at the known words in edits1(word):
      - if any of them has been seen right after prev, pick the one with the highest next_word_probs(counts, prev)
      - otherwise pick the one that starts the most bigrams (sum(counts.get(w, {}).values()), ties -> alphabetical first)
      - if there are none, keep word as it is."""
    # BEGIN SOLUTION
    if word in known:
        return word
    candidates = sorted(edits1(word) & known)
    if not candidates:
        return word
    probs = next_word_probs(counts, prev)
    after = [w for w in candidates if w in probs]
    if after:
        return max(after, key=lambda w: probs[w])
    return max(candidates, key=lambda w: sum(counts.get(w, {}).values()))
    # END SOLUTION


def fix_typos(text, counts):
    """Fix each token of tokenize(text) with fix_word, using the previously FIXED word as prev
    (start with prev = "."). Return the fixed tokens joined with spaces."""
    # BEGIN SOLUTION
    known = known_words(counts)
    out, prev = [], "."
    for w in tokenize(text):
        prev = fix_word(w, prev, counts, known)
        out.append(prev)
    return " ".join(out)
    # END SOLUTION


if __name__ == "__main__":
    tokens = tokenize(STORY)
    counts = count_bigrams(tokens)
    print("after 'robot':", {w: round(p, 2) for w, p in next_word_probs(counts, "robot").items()})
    rng = random.Random(4)
    for _ in range(3):
        print("->", generate(counts, "the", 12, rng))

    print("\nFixing typos with the robot's command words (from week 5's command examples):")
    from lesson09_commands import TRAIN
    cmd_counts = count_bigrams(tokenize(" . ".join(t for t, _ in TRAIN)))
    fixed = 0
    for typo, meant in TYPO_COMMANDS:
        f = fix_typos(typo, cmd_counts)
        fixed += f == meant
        print(f"  {typo!r:32} -> {f!r}{'' if f == meant else '   (wanted ' + repr(meant) + ')'}")
    print(f"fixed {fixed} of {len(TYPO_COMMANDS)}")
