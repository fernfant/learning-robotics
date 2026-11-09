"""Week 3: real sensor data from a phone. Smoothing it, finding which way is down, and counting steps.

Your phone has an ACCELEROMETER: it measures acceleration along 3 axes (x, y, z) in m/s^2, about 50 times a second.
Even lying still it reads about 9.8 m/s^2, because gravity pulls on it. So:
  - when it's still, the reading points straight DOWN, and tells you how the phone is tilted
  - when it moves, the reading wobbles, and the wobbles tell you about the motion (like steps)

data/phone_acc.csv is a real recording from a phone worn on someone's waist (standing, sitting, lying, walking).
Record your own with the free phyphox app ("Acceleration with g", then Export -> CSV) and it loads the same way.
"""

import math
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
G = 9.81


# ---------------- YOUR HOMEWORK ----------------

def read_phone_csv(path):
    """Read a phyphox-style CSV: one header line, then rows of "time,x,y,z" (numbers, separated by commas).
    Return four lists: (times, xs, ys, zs), all floats. Skip empty lines."""
    # BEGIN SOLUTION
    times, xs, ys, zs = [], [], [], []
    lines = Path(path).read_text().splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        t, x, y, z = (float(v) for v in line.split(",")[:4])
        times.append(t)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return times, xs, ys, zs
    # END SOLUTION


def magnitude(x, y, z):
    """How strong the acceleration is, whatever its direction: the square root of x*x + y*y + z*z."""
    # BEGIN SOLUTION
    return math.sqrt(x * x + y * y + z * z)
    # END SOLUTION


def moving_average(values, n):
    """Smooth a signal: each output is the average of the last n values (fewer at the very start).
    moving_average([2, 4, 6, 8], 2) -> [2.0, 3.0, 5.0, 7.0]"""
    # BEGIN SOLUTION
    out = []
    for i in range(len(values)):
        window = values[max(0, i - n + 1):i + 1]
        out.append(sum(window) / len(window))
    return out
    # END SOLUTION


def tilt_degrees(x, y, z):
    """When the phone is still, the reading points down (gravity). How far is the phone's x axis from pointing
    straight up? That's the angle between (x, y, z) and the x axis: acos(x / magnitude), in degrees.
    0 = x axis straight up (standing), 90 = x axis flat (lying down)."""
    # BEGIN SOLUTION
    return math.degrees(math.acos(max(-1.0, min(1.0, x / magnitude(x, y, z)))))
    # END SOLUTION


def count_steps(values, threshold, min_gap):
    """Count peaks: a sample counts as a step if it is above threshold, bigger than the sample before it,
    at least as big as the sample after it, and at least min_gap samples after the last step counted.
    (The first and last samples never count: they don't have two neighbours.)"""
    # BEGIN SOLUTION
    steps, last = 0, -min_gap
    for i in range(1, len(values) - 1):
        v = values[i]
        if v > threshold and v > values[i - 1] and v >= values[i + 1] and i - last >= min_gap:
            steps += 1
            last = i
    return steps
    # END SOLUTION


# ---------------- provided ----------------

def read_labels(path=DATA / "phone_labels.csv"):
    """[(start_s, end_s, activity), ...] for the shipped recording."""
    rows = Path(path).read_text().splitlines()[1:]
    return [(float(a), float(b), c) for a, b, c in (r.split(",") for r in rows if r.strip())]


def between(times, values, start, end):
    return [v for t, v in zip(times, values) if start <= t < end]


def describe(path):
    """What a recording says, in one sentence: average tilt while it's still, and steps while it's moving."""
    t, xs, ys, zs = read_phone_csv(path)
    mags = moving_average([magnitude(*r) for r in zip(xs, ys, zs)], 5)
    seconds = t[-1] - t[0] if len(t) > 1 else 0
    steps = count_steps(mags, 10.5, 15)
    tilt = tilt_degrees(sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs))
    return f"{seconds:.0f} s of data: average tilt {tilt:.0f} degrees, {steps} steps ({steps / max(seconds, 1e-9):.2f} a second)."


if __name__ == "__main__":
    t, xs, ys, zs = read_phone_csv(DATA / "phone_acc.csv")
    print(f"{len(t)} readings over {t[-1]:.0f} s ({len(t) / t[-1]:.0f} a second)")
    print("\nStill postures: which way is down?")
    for start, end, what in read_labels():
        if what in ("standing", "sitting", "laying"):
            mx, my, mz = (sum(between(t, v, start, end)) / len(between(t, v, start, end)) for v in (xs, ys, zs))
            print(f"  {what:9} {start:5.0f}-{end:3.0f} s   gravity {magnitude(mx, my, mz):5.2f} m/s^2   tilt {tilt_degrees(mx, my, mz):3.0f} degrees")
    print("\nWalking: counting steps (strength of the shake, smoothed over 5 readings)")
    mags = moving_average([magnitude(*r) for r in zip(xs, ys, zs)], 5)
    for start, end, what in read_labels():
        if what == "walking":
            seg = between(t, mags, start, end)
            n = count_steps(seg, 10.5, 15)
            print(f"  {start:5.0f}-{end:3.0f} s: {n} steps in {end - start:.1f} s = {n / (end - start):.2f} steps a second")
    raw = between(t, [magnitude(*r) for r in zip(xs, ys, zs)], 5, 24)
    print(f"\nNoise while standing still: raw readings vary by {max(raw) - min(raw):.2f} m/s^2, "
          f"smoothed by {max(moving_average(raw, 10)) - min(moving_average(raw, 10)):.2f}")
    print("\nYour own recording: put it in data/ and run describe(DATA / 'your_file.csv')")
    print("  " + describe(DATA / "phone_acc.csv"))
