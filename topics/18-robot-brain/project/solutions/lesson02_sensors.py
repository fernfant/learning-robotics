"""Lesson 2: noisy senses. Measuring distance, and why averaging helps."""

import random

from world import ROOM, is_free
from lesson01_moving import move


def distance_to_wall(room, pos, direction):
    """How many free squares are there between pos and the next wall in direction?
    The robot's own square doesn't count.

    Example: in the row "#.....#", a robot at x=1 facing "E" can step onto
    x = 2, 3, 4 and 5 before the wall at x = 6, so the answer is 4.
    """
    # BEGIN SOLUTION
    count = 0
    p = move(pos, direction)
    while is_free(room, p):
        count += 1
        p = move(p, direction)
    return count
    # END SOLUTION


def noisy_reading(true_distance, noise, rng):
    """A real sensor isn't perfect. Return true_distance plus random noise:
    add rng.uniform(-noise, noise). Never return less than 0."""
    # BEGIN SOLUTION
    return max(0.0, true_distance + rng.uniform(-noise, noise))
    # END SOLUTION


def average(values):
    """The mean: add them all up, divide by how many there are."""
    # BEGIN SOLUTION
    return sum(values) / len(values)
    # END SOLUTION


def smoothed_reading(true_distance, noise, n, rng):
    """Take n noisy readings and return their average."""
    # BEGIN SOLUTION
    return average([noisy_reading(true_distance, noise, rng) for _ in range(n)])
    # END SOLUTION


def average_error(true_distance, noise, n, trials, rng):
    """Repeat smoothed_reading `trials` times. Return the average of
    abs(reading - true_distance). This measures how wrong the sensor usually is."""
    # BEGIN SOLUTION
    errs = [abs(smoothed_reading(true_distance, noise, n, rng) - true_distance) for _ in range(trials)]
    return average(errs)
    # END SOLUTION


if __name__ == "__main__":
    rng = random.Random(0)
    d = distance_to_wall(ROOM, (1, 1), "E")
    print("True distance east from (1, 1):", d)
    for n in (1, 4, 16, 64):
        print(f"average of {n:2d} readings -> typical error {average_error(d, 1.0, n, 500, rng):.3f}")
