"""Lesson 3: learning from data. Fit a straight line by making the error smaller.

We measured how far the robot slides after braking at different speeds.
Goal: learn the rule  distance = w * speed + b  from the data.
"""

# (speed in m/s, stopping distance in m), measured on the robot
STOP_DATA = [
    (0.2, 0.27), (0.4, 0.40), (0.5, 0.45), (0.6, 0.57), (0.8, 0.70),
    (1.0, 0.86), (1.1, 0.95), (1.2, 1.05), (1.4, 1.18), (1.5, 1.30),
    (1.6, 1.36), (1.8, 1.55), (2.0, 1.70),
]


def predict(w, b, speed):
    """The model: a straight line."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 3: write this function")


def mse(w, b, data):
    """Mean squared error: for each (x, y), square (predict - y), then average.
    Smaller = the line fits the data better."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 3: write this function")


def gradients(w, b, data):
    """Which way should w and b move to make the error smaller?
    For mean squared error these are:
        dw = average of 2 * (predict - y) * x
        db = average of 2 * (predict - y)
    Return (dw, db)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 3: write this function")


def fit_line(data, lr=0.1, steps=2000):
    """Gradient descent. Start at w = 0, b = 0. Repeat `steps` times:
        dw, db = gradients(...)
        w = w - lr * dw
        b = b - lr * db
    Return (w, b, history), where history is the list of mse values, one per step."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 3: write this function")


def max_safe_speed(w, b, free_distance, margin=0.2):
    """Fastest speed (to 0.05 m/s) whose predicted stopping distance + margin
    still fits in free_distance. Try speeds 0.00, 0.05, 0.10 ... up to 3.00."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 3: write this function")


if __name__ == "__main__":
    w, b, hist = fit_line(STOP_DATA)
    print(f"learned: distance = {w:.3f} * speed + {b:.3f}")
    print(f"error went from {hist[0]:.4f} to {hist[-1]:.5f}")
    print("max safe speed with 1.0 m free:", max_safe_speed(w, b, 1.0), "m/s")
