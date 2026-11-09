"""Lesson 4: the artificial neuron. Should the robot stop?

Inputs (what the sensor tells us):
    x1 = distance to the thing ahead (metres)
    x2 = how fast it's getting closer (metres per second)
Output: probability that we must STOP (1 = stop, 0 = keep going).
"""

import math
import random


def make_obstacle_data(n, rng):
    """Simulated sensor examples: ((distance, closing_speed), label).
    The label comes from the TRUE situation: stop if distance - 1.0 * closing_speed < 1.0.
    But the sensor only sees noisy versions of distance and speed, as real sensors do,
    so examples near the boundary are genuinely uncertain."""
    data = []
    for _ in range(n):
        d = rng.uniform(0.0, 8.0)
        v = rng.uniform(0.0, 2.0)
        label = 1 if d - 1.0 * v < 1.0 else 0
        seen_d = round(max(0.0, d + rng.gauss(0, 0.4)), 2)
        seen_v = round(max(0.0, v + rng.gauss(0, 0.25)), 2)
        data.append(((seen_d, seen_v), label))
    return data


def sigmoid(z):
    """Squash any number into 0..1:  1 / (1 + e^(-z)).
    Tip: for very negative z, math.exp(-z) can overflow, so handle z < 0 using e^z / (1 + e^z)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 4: write this function")


def neuron(weights, bias, x):
    """Weighted sum, then sigmoid:  sigmoid(w1*x1 + w2*x2 + bias)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 4: write this function")


def train_neuron(data, lr=0.05, epochs=200):
    """Learn weights and bias from data with gradient descent.
    Start with weights [0, 0] and bias 0. For each epoch, for each (x, label):
        p = neuron(weights, bias, x)
        error = p - label
        each weight w_i  -=  lr * error * x_i
        bias             -=  lr * error
    Return (weights, bias)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 4: write this function")


def should_stop(weights, bias, x, threshold=0.5):
    """True if the neuron's stop-probability is at least threshold."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 4: write this function")


if __name__ == "__main__":
    rng = random.Random(2)
    data = make_obstacle_data(450, rng)
    w, b = train_neuron(data)
    print("weights", [round(v, 2) for v in w], "bias", round(b, 2))
    for x in [(4.0, 0.2), (1.5, 1.0), (0.5, 0.0)]:
        print(x, "stop prob", round(neuron(w, b, x), 2))
