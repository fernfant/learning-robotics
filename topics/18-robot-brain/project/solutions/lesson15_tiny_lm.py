"""Lesson 15 (Week 8): a tiny neural language model, built from zero, that writes PLANS.

Lesson 9's word counter picks ONE action. It can never do "put the red and blue blocks away",
"tidy up everything", "everything except the green one", or say "which block?" when you're vague.

This model WRITES its answer one word at a time, so the answer can be as long as it needs:
    "put the red and blue blocks away"  ->  put red blue <end>
    "clean up everything"               ->  put red blue green <end>
    "put the block away"                ->  ask <end>          (which block? it asks you)
    "make me a cup of tea"              ->  none <end>         (not a robot job)
Each step looks at the command AND the words it has already written. That's the core loop of every LLM:
read the context, predict the next word, repeat.

It needs far more examples than Lesson 9's 34, so we MAKE them: a few sentence templates times every
colour combination gives a few hundred (SYNTHETIC DATA, the trick real labs use too). Any of the bake-off's
12 commands that the templates happen to make are removed, so the bake-off score is honest.
Real LLMs (GPT, Claude) add attention (the stretch), billions of numbers and trillions of words.
Ours has about 2,000 numbers.
"""

import math
import random

from lesson08_words import tokenize
from lesson09_commands import TRAIN, TEST

OUT_WORDS = ["put", "go", "find", "stop", "ask", "none", "red", "blue", "green", "<end>"]
COLOURS = ["red", "blue", "green"]
START = "<start>"
E, H = 12, 32          # embedding size, hidden layer size
MAX_WORDS = 5          # the longest plan: put red blue green <end>

# ---------- the training data we make (templates) ----------
PUT_TEMPLATES = ["put {x} in the bin", "bin {x}", "throw away {x}", "get rid of {x}", "put {x} away",
                 "clear away {x}", "drop {x} in the bin", "tidy up {x}"]
ALL_PHRASES = ["everything", "all the blocks", "every block", "all of them"]
EXCEPT_TEMPLATES = ["everything except the {c} block", "all the blocks but the {c} one",
                    "every block apart from the {c} one", "everything but the {c}"]
ASK_COMMANDS = ["put the block in the bin", "move the block", "bin it", "put that one away", "throw the block out",
                "get rid of the block", "tidy up the block"]
NONE_COMMANDS = ["make me a cup of tea", "what is the weather like", "sing me a song", "tell me a joke", "open the window",
                 "do my homework", "cook dinner", "play some music", "turn on the lights"]
# held out: different templates, used only for testing
TEST_PUT_TEMPLATES = ["chuck {x} in the trash", "please put {x} in the bin"]
TEST_EXCEPT_TEMPLATES = ["all of them except the {c} one"]
TEST_ASK = ["put it in the bin", "drive to the block", "where is the block"]
TEST_NONE = ["make me some toast", "what time is it", "wash the dishes"]


def answer_words(intent, colour):
    """What the model should write for a Lesson 9 example: [intent, colour] (just [intent] for stop)."""
    return [intent] if intent == "stop" else [intent, colour]


def plan_examples(put_templates, except_templates, rng):
    """Make (command, plan words) examples. For EVERY template in put_templates, add:
      1. each colour c:            template with x = rng.choice(["the c block", "the c one"])        -> ["put", c]
      2. each ordered pair (a, b) of different colours (6 pairs), x = rng.choice(
            ["the a and b blocks", "the a block and the b block", "the a and the b one"])        -> ["put", a, b] in COLOURS order
      3. each phrase in ALL_PHRASES: x = the phrase                                               -> ["put", "red", "blue", "green"]
      4. each except template e and each colour c: x = e.format(c=c)                             -> ["put", the other two colours, in COLOURS order]
    Plans always list colours in COLOURS order, so "the green and red blocks" -> ["put", "red", "green"].
    Loop in this order (templates, then 1-4, colours in COLOURS order) so the rng choices match."""
    # BEGIN SOLUTION
    out = []
    for t in put_templates:
        for c in COLOURS:
            out.append((t.format(x=rng.choice([f"the {c} block", f"the {c} one"])), ["put", c]))
        for a in COLOURS:
            for b in COLOURS:
                if a != b:
                    x = rng.choice([f"the {a} and {b} blocks", f"the {a} block and the {b} block", f"the {a} and the {b} one"])
                    out.append((t.format(x=x), ["put"] + [k for k in COLOURS if k in (a, b)]))
        for phrase in ALL_PHRASES:
            out.append((t.format(x=phrase), ["put"] + COLOURS))
        for e in except_templates:
            for c in COLOURS:
                out.append((t.format(x=e.format(c=c)), ["put"] + [k for k in COLOURS if k != c]))
    return out
    # END SOLUTION


def softmax(scores):
    """Turn any list of scores into probabilities that add up to 1.
    Subtract the biggest score first so math.exp never overflows."""
    # BEGIN SOLUTION
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]
    # END SOLUTION


class TinyLM:
    def __init__(self, vocab, seed=0):
        rng = random.Random(seed)
        r = lambda n: [rng.uniform(-0.3, 0.3) for _ in range(n)]
        self.vocab = sorted(vocab)
        self.word_emb = {w: r(E) for w in self.vocab}                  # input words
        self.out_emb = {w: r(E) for w in OUT_WORDS + [START]}          # words it has written
        self.W1 = [r(3 * E) for _ in range(H)]                         # hidden layer
        self.b1 = [0.0] * H
        self.W2 = [r(H) for _ in range(len(OUT_WORDS))]               # output scores
        self.b2 = [0.0] * len(OUT_WORDS)

    def read(self, command):
        """The average embedding of the command's known words (all zeros if none are known)."""
        # BEGIN SOLUTION
        vecs = [self.word_emb[w] for w in tokenize(command) if w in self.word_emb]
        if not vecs:
            return [0.0] * E
        return [sum(v[i] for v in vecs) / len(vecs) for i in range(E)]
        # END SOLUTION

    def forward(self, ctx, prev2, prev1):
        """One prediction step. Input = ctx + embedding(prev2) + embedding(prev1) (joined into 3*E numbers).
        hidden = tanh(W1 . input + b1),  scores = W2 . hidden + b2,  probs = softmax(scores).
        Return (x, hidden, probs)."""
        # BEGIN SOLUTION
        x = ctx + self.out_emb[prev2] + self.out_emb[prev1]
        hidden = [math.tanh(sum(w * xi for w, xi in zip(row, x)) + b) for row, b in zip(self.W1, self.b1)]
        scores = [sum(w * h for w, h in zip(row, hidden)) + b for row, b in zip(self.W2, self.b2)]
        return x, hidden, softmax(scores)
        # END SOLUTION

    def generate(self, command, max_words=MAX_WORDS):
        """Greedy decoding: start with prev2 = prev1 = START, repeatedly pick the most likely
        next word, stop at "<end>". Return the list of words written (without "<end>")."""
        # BEGIN SOLUTION
        ctx = self.read(command)
        prev2, prev1, out = START, START, []
        for _ in range(max_words):
            _, _, probs = self.forward(ctx, prev2, prev1)
            word = OUT_WORDS[probs.index(max(probs))]
            if word == "<end>":
                break
            out.append(word)
            prev2, prev1 = prev1, word
        return out
        # END SOLUTION

    # ---- training: provided. It's Lesson 3's gradient descent, with the chain rule written out. ----
    def train_step(self, command, target_words, lr):
        """One example. Returns the total loss (how surprised the model was by the right words)."""
        words = tokenize(command)
        known = [w for w in words if w in self.word_emb]
        ctx = self.read(command)
        prev2, prev1, loss = START, START, 0.0
        for target in target_words:
            x, hidden, probs = self.forward(ctx, prev2, prev1)
            t = OUT_WORDS.index(target)
            loss -= math.log(probs[t] + 1e-12)
            d_scores = [p - (1.0 if i == t else 0.0) for i, p in enumerate(probs)]   # softmax + cross-entropy
            d_hidden = [sum(d_scores[k] * self.W2[k][j] for k in range(len(OUT_WORDS))) for j in range(H)]
            for k in range(len(OUT_WORDS)):
                for j in range(H):
                    self.W2[k][j] -= lr * d_scores[k] * hidden[j]
                self.b2[k] -= lr * d_scores[k]
            d_pre = [d_hidden[j] * (1 - hidden[j] ** 2) for j in range(H)]          # tanh'
            d_x = [sum(d_pre[j] * self.W1[j][i] for j in range(H)) for i in range(3 * E)]
            for j in range(H):
                for i in range(3 * E):
                    self.W1[j][i] -= lr * d_pre[j] * x[i]
                self.b1[j] -= lr * d_pre[j]
            for i in range(E):                                                       # embeddings learn too
                for w in known:
                    self.word_emb[w][i] -= lr * d_x[i] / len(known)
                self.out_emb[prev2][i] -= lr * d_x[E + i]
                self.out_emb[prev1][i] -= lr * d_x[2 * E + i]
            prev2, prev1 = prev1, target
        return loss


def make_targets(examples):
    """Turn Lesson 9 style (command, intent) pairs into (command, plan words) using Lesson 9's colour finder.
    Pairs whose colour can't be found are skipped."""
    from lesson09_commands import extract_object
    out = []
    for text, intent in examples:
        obj = extract_object(text)
        if intent != "stop" and not obj:
            continue
        out.append((text, answer_words(intent, obj.split()[0] if obj else None)))
    return out


def training_data(extra=()):
    """Everything the model learns from: Lesson 9's commands, the template plans, ask and none examples.
    The small groups are repeated 3 times so the big template group doesn't drown them out.
    extra: more (command, intent) pairs, e.g. labelled by a teacher (Lesson 17)."""
    from lesson19_bakeoff import TASKS
    exam = {t["command"] for t in TASKS}    # the bake-off is the robot's exam: never train on it
    rng = random.Random(0)
    data = (plan_examples(PUT_TEMPLATES, EXCEPT_TEMPLATES, rng) + make_targets(list(TRAIN) + list(extra)) * 3
            + [(c, ["ask"]) for c in ASK_COMMANDS] * 3 + [(c, ["none"]) for c in NONE_COMMANDS] * 3)
    return [(c, w) for c, w in data if c not in exam]


def test_data():
    """Held-out examples: new templates, Lesson 9's TEST, new ask and none commands."""
    return (plan_examples(TEST_PUT_TEMPLATES, TEST_EXCEPT_TEMPLATES, random.Random(1)) + make_targets(TEST)
            + [(c, ["ask"]) for c in TEST_ASK] + [(c, ["none"]) for c in TEST_NONE])


def train_tiny_lm(extra=(), epochs=25, lr=0.05, seed=0, cls=None):
    """Train on training_data(extra). Returns (model, loss_per_epoch). cls lets the attention stretch reuse this."""
    data = [(t, w + ["<end>"]) for t, w in training_data(extra)]
    vocab = {w for text, _ in data for w in tokenize(text)}
    model = (cls or TinyLM)(vocab, seed)
    rng = random.Random(seed)
    history = []
    for _ in range(epochs):
        rng.shuffle(data)
        history.append(sum(model.train_step(t, y, lr) for t, y in data) / len(data))
    return model, history


def words_to_plan(words):
    """Turn the model's words into something the robot can do:
      ["ask"] -> "ask"      ["none"] -> "none"      ["stop"] -> [{"intent": "stop", "object": None}]
      ["go", "red"] or ["find", "red"] -> one action, e.g. [{"intent": "go", "object": "red block"}]  (exactly one colour)
      ["put", c1, c2, ...] -> one put action per colour (at least one, no repeats)
    Anything else (no words, wrong order, unknown or repeated colour, extra words) -> None."""
    # BEGIN SOLUTION
    if words in (["ask"], ["none"]):
        return words[0]
    if words == ["stop"]:
        return [{"intent": "stop", "object": None}]
    if not words or words[0] not in ("put", "go", "find"):
        return None
    colours = words[1:]
    if not colours or any(c not in COLOURS for c in colours) or len(set(colours)) != len(colours):
        return None
    if words[0] != "put" and len(colours) != 1:
        return None
    return [{"intent": words[0], "object": f"{c} block"} for c in colours]
    # END SOLUTION


def accuracy(model, examples):
    """Fraction of (command, plan words) examples where the model writes exactly the right plan."""
    return sum(model.generate(t) == y for t, y in examples) / len(examples)


if __name__ == "__main__":
    import time
    t0 = time.perf_counter()
    model, hist = train_tiny_lm()
    data, test = training_data(), test_data()
    print(f"{len(data)} training examples (made from templates), {len(test)} held-out test examples")
    print(f"loss: first epoch {hist[0]:.2f} -> last epoch {hist[-1]:.3f}   ({time.perf_counter() - t0:.0f} s)")
    print(f"exact plan accuracy: train {accuracy(model, data):.0%}, held-out test {accuracy(model, test):.0%}")
    for c in ["put the green and red blocks away", "throw out all of them except the blue one", "put it in the bin",
              "what time is it", "where's the green one?"]:
        words = model.generate(c)
        print(f"  {c!r:44} -> {' '.join(words):18} -> {words_to_plan(words)}")
