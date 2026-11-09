"""Lesson 5: is it any good? Honest testing of the stop-detector.

The rule: never judge a model on the same examples it learned from.
"""

import random

from lesson04_neuron import make_obstacle_data, train_neuron, neuron


def train_test_split(data, test_fraction, rng):
    """Shuffle a COPY of data, then put the first test_fraction of it in test,
    the rest in train. Return (train, test)."""
    # BEGIN SOLUTION
    items = list(data)
    rng.shuffle(items)
    k = int(len(items) * test_fraction)
    return items[k:], items[:k]
    # END SOLUTION


def confusion(predictions, labels):
    """Count (tp, fp, fn, tn) where 1 = "stop".
    tp: said stop, should stop.   fp: said stop, didn't need to.
    fn: said go, should have stopped (dangerous!).   tn: said go, correctly."""
    # BEGIN SOLUTION
    tp = sum(1 for p, y in zip(predictions, labels) if p == 1 and y == 1)
    fp = sum(1 for p, y in zip(predictions, labels) if p == 1 and y == 0)
    fn = sum(1 for p, y in zip(predictions, labels) if p == 0 and y == 1)
    tn = sum(1 for p, y in zip(predictions, labels) if p == 0 and y == 0)
    return tp, fp, fn, tn
    # END SOLUTION


def accuracy(tp, fp, fn, tn):
    # BEGIN SOLUTION
    return (tp + tn) / (tp + fp + fn + tn)
    # END SOLUTION


def precision(tp, fp, fn, tn):
    """Of all the times we said stop, how often were we right? (0 if we never said stop.)"""
    # BEGIN SOLUTION
    return tp / (tp + fp) if tp + fp else 0.0
    # END SOLUTION


def recall(tp, fp, fn, tn):
    """Of all the times we SHOULD have stopped, how often did we? (0 if there were none.)"""
    # BEGIN SOLUTION
    return tp / (tp + fn) if tp + fn else 0.0
    # END SOLUTION


def evaluate(weights, bias, data, threshold):
    """Run the neuron on every example in data with this threshold.
    Return a dict with keys accuracy, precision, recall (each 0..1)."""
    # BEGIN SOLUTION
    preds = [1 if neuron(weights, bias, x) >= threshold else 0 for x, _ in data]
    labels = [y for _, y in data]
    c = confusion(preds, labels)
    return {"accuracy": accuracy(*c), "precision": precision(*c), "recall": recall(*c)}
    # END SOLUTION


def safest_threshold(weights, bias, data, min_recall=0.97):
    """Safety first: missing a needed stop is worse than a false alarm.
    Try thresholds 0.99, 0.98, ... down to 0.01 and return the HIGHEST one
    whose recall on data is at least min_recall (fewest false alarms while staying safe)."""
    # BEGIN SOLUTION
    for i in range(99, 0, -1):
        t = i / 100
        if evaluate(weights, bias, data, t)["recall"] >= min_recall:
            return t
    return 0.01
    # END SOLUTION


if __name__ == "__main__":
    rng = random.Random(2)
    data = make_obstacle_data(600, rng)
    train, test = train_test_split(data, 0.25, rng)
    w, b = train_neuron(train)
    print("at 0.5 on TEST:", {k: round(v, 3) for k, v in evaluate(w, b, test, 0.5).items()})
    t = safest_threshold(w, b, train)
    print("safest threshold (chosen on TRAIN):", t)
    print("at that threshold on TEST:", {k: round(v, 3) for k, v in evaluate(w, b, test, t).items()})
