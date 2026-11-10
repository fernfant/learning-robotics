"""Week 12: "Where am I?" A particle filter.

Someone picks the robot up and puts it down somewhere else (robotics people call this KIDNAPPING). Its odometry is now
useless. But it has a map (week 11) and a laser scanner. So it guesses:
  1. SPREAD  scatter hundreds of guesses ("particles") all over the free floor, each with a random heading
  2. SCORE   for each guess, what WOULD the scanner read from there? The closer to the real scan, the higher its score
  3. PICK    keep guesses in proportion to their score (good ones get copied, bad ones vanish)
  4. MOVE    when the robot drives, move every guess the same way (plus a little randomness), then go back to 2
After a few rounds the guesses crowd together where the robot really is. Self-driving cars, vacuum robots and
warehouse robots all do this (it's also called Monte Carlo Localisation).
"""

import math
import random

from world import ROOM
from body import Body, SQUARE, centre, ray, is_wall

BEAMS = list(range(0, 360, 30))      # use 12 of the scanner's 36 beams: plenty, and 3 times faster
SIGMA = 0.3                          # how much one beam may differ from the guess's and still look right (metres)
SURPRISE = 0.05                      # a beam can always be a surprise (the cat, a bag): never score it exactly 0
FRESH = 0.05                         # each round, 5% of guesses are swapped for fresh random ones (kept at the end)


# ---------------- YOUR HOMEWORK ----------------

def score(expected, measured, sigma=SIGMA, surprise=SURPRISE):
    """How well does a guess explain the real scan? Both are lists of distances (same beams, same order).
    Score each beam: exp(-(e - m) ** 2 / (2 * sigma * sigma)) + surprise   (near 1 + surprise if it matches,
    just `surprise` if it's way off, because a beam can always hit something the map doesn't know, like the cat).
    Multiply the beam scores together: a guess must explain MOST beams to score well."""
    # BEGIN SOLUTION
    total = 1.0
    for e, m in zip(expected, measured):
        total *= math.exp(-(e - m) ** 2 / (2 * sigma * sigma)) + surprise
    return total
    # END SOLUTION


def normalise(weights):
    """Scale the weights so they add up to 1. If they're all 0, give every particle the same weight."""
    # BEGIN SOLUTION
    total = sum(weights)
    if total == 0:
        return [1 / len(weights)] * len(weights)
    return [w / total for w in weights]
    # END SOLUTION


def resample(particles, weights, rng):
    """Pick len(particles) new particles, each one chosen at random in proportion to its weight
    (rng.choices(particles, weights=weights, k=...)). Good guesses get copied; bad ones disappear."""
    # BEGIN SOLUTION
    return rng.choices(particles, weights=weights, k=len(particles))
    # END SOLUTION


def estimate(particles):
    """The filter's best guess: the average x, the average y, and the average heading. Headings are angles, so
    average them the safe way: atan2(average of sin(heading), average of cos(heading)). Return (x, y, heading)."""
    # BEGIN SOLUTION
    n = len(particles)
    x = sum(p[0] for p in particles) / n
    y = sum(p[1] for p in particles) / n
    h = math.atan2(sum(math.sin(p[2]) for p in particles) / n, sum(math.cos(p[2]) for p in particles) / n)
    return x, y, h
    # END SOLUTION


# ---------------- provided ----------------

def spread(n, rng, room=ROOM):
    """n random guesses on free floor (the map knows walls, not the cat), with random headings."""
    out = []
    while len(out) < n:
        x, y = rng.uniform(0, len(room[0]) * SQUARE), rng.uniform(0, len(room) * SQUARE)
        if not is_wall(x, y, room, cat=False):
            out.append((x, y, rng.uniform(-math.pi, math.pi)))
    return out


def expected_scan(p, room=ROOM):
    """What the scanner WOULD read from guess p, using only the map (so the cat is a surprise)."""
    return [ray(p[0], p[1], p[2] + math.radians(b), room, cat=False, step=0.04) for b in BEAMS]


def move_all(particles, d_left, d_right, rng, noise=0.03):
    """Move every guess the way the encoders say the robot moved, plus a little randomness (wheels slip)."""
    from lesson23_wheels import move_pose
    out = []
    for p in particles:
        x, y, h = move_pose(p, d_left + rng.gauss(0, noise), d_right + rng.gauss(0, noise))
        out.append((x, y, h))
    return out


def update(particles, real_scan, rng):
    """Score, pick, and swap the last 5% of the guesses for fresh random ones, in case every guess is wrong."""
    weights = normalise([score(expected_scan(p), real_scan) for p in particles])
    kept = resample(particles, weights, rng)
    k = int(len(kept) * FRESH)
    return kept[:len(kept) - k] + spread(k, rng)


def best_guess(particles):
    """Your estimate(), leaving out the fresh random guesses at the end."""
    return estimate(particles[:len(particles) - int(len(particles) * FRESH)])


def localise(body, rng, n=400, moves=None, report=None):
    """Kidnapped robot: spread guesses, then scan, score, pick, move... Returns the final estimate."""
    from lesson23_wheels import ticks_to_metres
    moves = moves or [(0.25, 0.25)] * 6 + [(0.1, -0.1)] * 4 + [(0.25, 0.25)] * 6
    particles = spread(n, rng)
    last = body.encoders()
    for i, (vl, vr) in enumerate(moves):
        scan = [d for a, d in body.scan() if round(a) in BEAMS]
        particles = update(particles, scan, rng)
        if report:
            report(i, best_guess(particles), particles)
        for _ in range(10):
            body.drive(vl, vr, 0.05)
        now = body.encoders()
        dl, dr = (ticks_to_metres(a - b) for a, b in zip(now, last))
        last = now
        particles = move_all(particles, dl, dr, rng)
    scan = [d for a, d in body.scan() if round(a) in BEAMS]
    return best_guess(update(particles, scan, rng))


def error(body, est):
    x, y, _ = body.true_pose()
    return math.hypot(est[0] - x, est[1] - y)


if __name__ == "__main__":
    print("A kidnapped robot: dropped at square (6, 3) facing west. It has no idea where it is.")
    print("400 guesses, spread over the whole room. After each scan, how far is the best guess from the truth?\n")
    body = Body(start=(6, 3), heading_deg=180, seed=5)
    rng = random.Random(7)
    def report(i, est, particles):
        spread_m = math.sqrt(sum((p[0] - est[0]) ** 2 + (p[1] - est[1]) ** 2 for p in particles) / len(particles))
        print(f"   scan {i + 1:2}: guess ({est[0]:.2f}, {est[1]:.2f}) is {error(body, est):.2f} m from the truth; "
              f"the guesses are spread over {spread_m:.2f} m")
    final = localise(body, rng, report=report)
    x, y, h = body.true_pose()
    print(f"\nFinal guess ({final[0]:.2f}, {final[1]:.2f}) facing {math.degrees(final[2]):.0f} degrees; "
          f"really ({x:.2f}, {y:.2f}) facing {h:.0f}. Off by {error(body, final):.2f} m.")
