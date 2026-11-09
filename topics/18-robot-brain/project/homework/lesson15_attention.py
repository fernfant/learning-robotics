"""Lesson 15 stretch: ATTENTION. Let the model choose which words to look at, at every step.

The Lesson 15 model reads a command by AVERAGING all its word embeddings, once, before it writes anything.
Every word counts the same, every step. "put the red block in the bin" and "put the block in the red bin"
average to EXACTLY the same numbers, and the colour gets diluted by "the", "in", "bin"...

Attention fixes that. At each step, the word the model just wrote asks a question (the QUERY):
  writing the 1st word (after <start>):  "which words tell me the action?"
  writing the 2nd word (after "put"):    "which words tell me the colour?"
Every command word gets a score = how well it matches the query (a dot product). Softmax turns the scores
into weights that add up to 1, and the context is the WEIGHTED average. Different step, different weights.
That is the core of the Transformer, the T in GPT (Course Module 06, Day 13).
"""

import math
import random

from lesson08_words import tokenize
from lesson15_tiny_lm import TinyLM, OUT_WORDS, START, E, H, MAX_WORDS, softmax, accuracy, train_tiny_lm, test_data


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def attend(query, keys):
    """query: a list of E numbers. keys: a list of word embeddings (each E numbers).
    score_i = dot(query, key_i) / sqrt(E)      (dividing by sqrt(E) keeps scores from getting huge)
    weights = softmax(scores)
    context = sum of weights_i * key_i         (a weighted average, E numbers)
    Return (context, weights)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 15: write this function")


class AttnTinyLM(TinyLM):
    """Same as TinyLM, but the context is recomputed at every step with attention.
    The query is the embedding of the word just written (prev1)."""

    def words(self, command):
        return [w for w in tokenize(command) if w in self.word_emb]

    def step(self, command, prev2, prev1):
        """One prediction step with attention. Returns (x, hidden, probs, weights, words)."""
        ws = self.words(command)
        if ws:
            ctx, weights = attend(self.out_emb[prev1], [self.word_emb[w] for w in ws])
        else:
            ctx, weights = [0.0] * E, []
        x, hidden, probs = self.forward(ctx, prev2, prev1)
        return x, hidden, probs, weights, ws

    def generate(self, command, max_words=MAX_WORDS, show=False):
        prev2, prev1, out = START, START, []
        for _ in range(max_words):
            _, _, probs, weights, ws = self.step(command, prev2, prev1)
            word = OUT_WORDS[probs.index(max(probs))]
            if show:
                focus = "  ".join(f"{w}:{a:.2f}" for w, a in sorted(zip(ws, weights), key=lambda t: -t[1])[:3])
                print(f"    after {prev1!r:9} looks at  {focus:36} -> writes {word!r} ({max(probs):.2f})")
            if word == "<end>":
                break
            out.append(word)
            prev2, prev1 = prev1, word
        return out

    # ---- training: provided. Same as Lesson 15, plus the chain rule through attention. ----
    def train_step(self, command, target_words, lr):
        ws = self.words(command)
        prev2, prev1, loss = START, START, 0.0
        for target in target_words:
            x, hidden, probs, a, _ = self.step(command, prev2, prev1)
            t = OUT_WORDS.index(target)
            loss -= math.log(probs[t] + 1e-12)
            d_scores = [p - (1.0 if i == t else 0.0) for i, p in enumerate(probs)]
            d_hidden = [sum(d_scores[k] * self.W2[k][j] for k in range(len(OUT_WORDS))) for j in range(H)]
            for k in range(len(OUT_WORDS)):
                for j in range(H):
                    self.W2[k][j] -= lr * d_scores[k] * hidden[j]
                self.b2[k] -= lr * d_scores[k]
            d_pre = [d_hidden[j] * (1 - hidden[j] ** 2) for j in range(H)]
            d_x = [sum(d_pre[j] * self.W1[j][i] for j in range(H)) for i in range(3 * E)]
            for j in range(H):
                for i in range(3 * E):
                    self.W1[j][i] -= lr * d_pre[j] * x[i]
                self.b1[j] -= lr * d_pre[j]
            d_q = [0.0] * E
            if ws:
                q = self.out_emb[prev1]
                keys = [self.word_emb[w][:] for w in ws]
                d_ctx = d_x[:E]
                d_a = [dot(d_ctx, k) for k in keys]                      # ctx = sum a_i k_i
                mean = sum(ai * dai for ai, dai in zip(a, d_a))
                d_s = [ai * (dai - mean) for ai, dai in zip(a, d_a)]     # through softmax
                for i in range(E):
                    d_q[i] = sum(ds * k[i] for ds, k in zip(d_s, keys)) / math.sqrt(E)
                for w, k, ai, ds in zip(ws, keys, a, d_s):
                    emb = self.word_emb[w]
                    for i in range(E):
                        emb[i] -= lr * (ai * d_ctx[i] + ds * q[i] / math.sqrt(E))
            for i in range(E):
                self.out_emb[prev2][i] -= lr * d_x[E + i]
                self.out_emb[prev1][i] -= lr * (d_x[2 * E + i] + d_q[i])
            prev2, prev1 = prev1, target
        return loss


def train_attn_lm(extra=(), epochs=25, lr=0.05, seed=0):
    """Same data and training loop as Lesson 15, with the attention model."""
    return train_tiny_lm(extra, epochs, lr, seed, cls=AttnTinyLM)


def padded_commands(extra):
    """9 commands with the colour buried among `extra` filler words, e.g. "put the red block the in bin block to"."""
    filler = (["the", "in", "bin", "block", "to"] * 10)[:extra]
    return [(f"{verb} {c} block " + " ".join(filler), c)
            for c in ("red", "blue", "green") for verb in ("put the", "go to the", "find the")]


def colour_accuracy(model, examples):
    return sum(model.generate(t)[1:2] == [c] for t, c in examples) / len(examples)


if __name__ == "__main__":
    print("Training both models on the same data, with 3 different random starts (seeds)...")
    test = test_data()
    pairs = [(train_tiny_lm(seed=s)[0], train_attn_lm(seed=s)[0]) for s in (0, 1, 2)]
    for s, (avg, att) in enumerate(pairs):
        print(f"  seed {s}: held-out plans  averaging {accuracy(avg, test):4.0%}   attention {accuracy(att, test):4.0%}")
    a = sum(accuracy(m, test) for m, _ in pairs) / 3
    b = sum(accuracy(m, test) for _, m in pairs) / 3
    print(f"  average:                 averaging {a:4.0%}   attention {b:4.0%}")
    att = pairs[0][1]
    print("\nWhere does it look? (the top 3 attention weights at each step)")
    for c in ["put the red and green blocks away", "throw out all of them except the blue one"]:
        print(f"  {c!r}")
        att.generate(c, show=True)
    print("\nWhat attention does NOT fix (it has no idea of word ORDER):")
    for c in ["put the block in the red bin", "go to the blue block not the red one"]:
        print(f"  {c!r:40} averaging {pairs[0][0].generate(c)}  attention {att.generate(c)}")
