"""Bonus (Course Module 21): the maths behind robots, each idea used to make Robo-Helper better.

Play with the interactive explainers first (links on the Module 21 page), then run this file.
Standard library only. Every experiment prints a before/after number you can check.

    python3 bonus_robot_math.py
"""

import cmath
import heapq
import math
import random

from world import ROOM, ROBOT_START, OBJECTS, find_bin
from lesson02_sensors import noisy_reading
from lesson03_learning import STOP_DATA, gradients, mse
from lesson06_paths import neighbors
from lesson07_trial_error import MAZE, find_char, q_learn, greedy_path

CAT = (4, 1)


# 1. LINEAR ALGEBRA: turn what the robot's sensor sees (its own frame) into room coordinates.
def rotate(v, degrees):
    """Rotate a 2D vector with the rotation matrix [[cos, -sin], [sin, cos]]. y grows DOWN in our room,
    so a positive angle turns clockwise on screen."""
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return (round(c * v[0] - s * v[1], 9), round(s * v[0] + c * v[1], 9))


def sensor_to_room(robot_pos, heading_degrees, reading):
    """The sensor says 'something is `reading` squares straight ahead'. Where is it in the room?"""
    dx, dy = rotate((reading, 0), heading_degrees)
    return (round(robot_pos[0] + dx), round(robot_pos[1] + dy))


# 2. BAYES: where is the cat? Update a belief over squares from noisy "distance east" readings.
def free_squares(room):
    return [(x, y) for y, row in enumerate(room) for x, ch in enumerate(row) if ch != "#"]


def bayes_cat(readings, robot, row_squares, noise):
    """Belief over the squares east of the robot on its row. Prior: uniform. Each reading multiplies in
    the Gaussian likelihood of that reading given the cat's distance, then we normalise."""
    belief = {sq: 1.0 for sq in row_squares}
    for r in readings:
        for sq in belief:
            d = sq[0] - robot[0]
            belief[sq] *= math.exp(-((r - d) ** 2) / (2 * noise ** 2))
        total = sum(belief.values())
        belief = {sq: p / total for sq, p in belief.items()}
    return belief


# 3. MARKOV CHAINS: the cat wanders square to square. Where does it spend its time?
def cat_chain(room, bed=CAT, stay=0.5, pull=0.8):
    """Transition probabilities: stay put with probability `stay`, otherwise step to a free neighbour,
    preferring squares closer to its bed (weight exp(-pull * distance to bed)). Real cats have favourite spots."""
    P = {}
    for sq in free_squares(room):
        nbrs = neighbors(room, sq)
        if not nbrs:
            P[sq] = {sq: 1.0}
            continue
        wts = {n: math.exp(-pull * (abs(n[0] - bed[0]) + abs(n[1] - bed[1]))) for n in nbrs}
        total = sum(wts.values())
        P[sq] = {sq: stay, **{n: (1 - stay) * w / total for n, w in wts.items()}}
    return P


def stationary(P, steps=500):
    """Start the cat anywhere (uniform) and apply the chain many times: the long-run share of time per square."""
    dist = {sq: 1 / len(P) for sq in P}
    for _ in range(steps):
        new = dict.fromkeys(P, 0.0)
        for sq, p in dist.items():
            for nxt, q in P[sq].items():
                new[nxt] += p * q
        dist = new
    return dist


def astar_cost(room, start, goal, cost):
    """A* where entering a square costs cost(square) (at least 1). Returns the path."""
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    frontier, came, g = [(h(start), start)], {start: None}, {start: 0.0}
    while frontier:
        _, cur = heapq.heappop(frontier)
        if cur == goal:
            break
        for n in neighbors(room, cur):
            ng = g[cur] + cost(n)
            if n not in g or ng < g[n]:
                g[n], came[n] = ng, cur
                heapq.heappush(frontier, (ng + h(n), n))
    path, p = [], goal
    while p is not None:
        path.append(p)
        p = came[p]
    return path[::-1]


def bumps_per_trip(path, P, start_dist, rng, trials=2000):
    """Simulate the wandering cat while the robot walks the path; count how often they land on the same square."""
    squares = list(start_dist)
    weights = [start_dist[s] for s in squares]
    hits = 0
    for _ in range(trials):
        cat = rng.choices(squares, weights)[0]
        for robot_sq in path[1:]:
            nxt = list(P[cat])
            cat = rng.choices(nxt, [P[cat][n] for n in nxt])[0]
            hits += cat == robot_sq
    return hits / trials


# 4. KALMAN FILTER: track the distance to the wall while the robot drives towards it.
def drive_and_measure(start=7.0, speed=0.5, dt=0.1, steps=100, noise=1.0, rng=None):
    rng = rng or random.Random(0)
    true = [max(start - speed * dt * k, 0.0) for k in range(steps)]
    return true, [noisy_reading(t, noise, rng) for t in true]


def moving_average(readings, n):
    return [sum(readings[max(0, k - n + 1):k + 1]) / len(readings[max(0, k - n + 1):k + 1]) for k in range(len(readings))]


def kalman(readings, speed, dt, noise, q=0.01):
    """1D Kalman filter. Predict: the distance shrinks by speed*dt (we know our own speed), uncertainty grows by q.
    Update: blend in the reading, trusting it by the Kalman gain K = P / (P + noise^2)."""
    x, P, out = readings[0], noise ** 2, []
    for r in readings:
        x, P = x - speed * dt, P + q            # predict
        K = P / (P + noise ** 2)                # how much to trust the sensor
        x, P = x + K * (r - x), (1 - K) * P     # update
        out.append(x)
    return out


def rms(est, true):
    return math.sqrt(sum((e - t) ** 2 for e, t in zip(est, true)) / len(true))


# 5. A*: how much does the heuristic save, and what if you trust it MORE (weighted A*)?
def weighted_astar(room, start, goal, w=1.0):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    frontier, came, g, expanded = [(w * h(start), start)], {start: None}, {start: 0}, 0
    while frontier:
        _, cur = heapq.heappop(frontier)
        expanded += 1
        if cur == goal:
            break
        for n in neighbors(room, cur):
            if n not in g or g[cur] + 1 < g[n]:
                g[n], came[n] = g[cur] + 1, cur
                heapq.heappush(frontier, (g[n] + w * h(n), n))
    return g[goal], expanded


# 6. FOURIER: the wheels shake the sensor at a steady rhythm. Find it, and remove it.
def dft(xs):
    n = len(xs)
    return [sum(x * cmath.exp(-2j * math.pi * k * t / n) for t, x in enumerate(xs)) for k in range(n)]


def idft(X):
    n = len(X)
    return [sum(X[k] * cmath.exp(2j * math.pi * k * t / n) for k in range(n)).real / n for t in range(n)]


def remove_peak(xs):
    """Zero the strongest non-zero frequency (and its mirror), then transform back."""
    X = dft(xs)
    n = len(X)
    k = max(range(1, n // 2), key=lambda i: abs(X[i]))
    X[k] = X[n - k] = 0
    return idft(X), k


# 7. MOMENTUM: Lesson 3's line fit, with and without a "heavy ball".
def fit_steps(data, lr, beta, target, max_steps=5000):
    """Gradient descent with momentum: v = beta*v + grad; w -= lr*v. Steps until mse < target."""
    w = b = vw = vb = 0.0
    for step in range(1, max_steps + 1):
        dw, db = gradients(w, b, data)
        vw, vb = beta * vw + dw, beta * vb + db
        w, b = w - lr * vw, b - lr * vb
        if mse(w, b, data) < target:
            return step
    return None


if __name__ == "__main__":
    print("1) LINEAR ALGEBRA: the robot at (4, 3) facing 90 degrees (down the screen) sees something 2 squares ahead.")
    print(f"   rotate((2, 0), 90) = {rotate((2, 0), 90)}  ->  it is at room square {sensor_to_room((4, 3), 90, 2)}")

    print("\n2) BAYES: where is the cat? The robot at (1, 1) takes noisy 'distance east' readings (noise 1.0).")
    row = [sq for sq in free_squares(ROOM) if sq[1] == 1 and sq[0] > 1]
    rng = random.Random(0)
    for n in (1, 4, 16):
        right = 0
        for _ in range(500):
            reads = [noisy_reading(CAT[0] - 1, 1.0, rng) for _ in range(n)]
            b = bayes_cat(reads, (1, 1), row, 1.0)
            right += max(b, key=b.get) == CAT
        print(f"   {n:2} readings: most likely square is the right one {right / 5:.0f}% of the time")

    print("\n3) MARKOV CHAIN: a wandering cat with a favourite bed at (4, 1). Route to the blue block avoiding where it usually is.")
    P = cat_chain(ROOM)
    pi = stationary(P)
    top = sorted(pi.items(), key=lambda kv: -kv[1])[:3]
    print("   cat's favourite squares (long-run share):", ", ".join(f"{sq} {p:.1%}" for sq, p in top))
    goal = OBJECTS["blue block"]
    plain = astar_cost(ROOM, ROBOT_START, goal, lambda s: 1.0)
    careful = astar_cost(ROOM, ROBOT_START, goal, lambda s: 1.0 + 20 * pi[s])
    for name, path in (("shortest", plain), ("cat-aware", careful)):
        print(f"   {name:9} route: {len(path) - 1:2} steps, expected run-ins with the cat per trip "
              f"{bumps_per_trip(path, P, pi, random.Random(1)):.3f}")

    print("\n4) KALMAN FILTER: driving towards a wall at 0.5 m/s, sensor noise 1.0 m, 10 readings a second.")
    true, reads = drive_and_measure()
    for name, est in (("raw readings", reads), ("average of last 16", moving_average(reads, 16)),
                      ("Kalman filter", kalman(reads, 0.5, 0.1, 1.0))):
        print(f"   {name:20} typical error {rms(est, true):.2f} m")

    print("\n5) A*: the room, start to bin. Plain search vs A* vs weighted A* (trusting the guess more).")
    for w in (0.0, 1.0, 2.0, 5.0):
        length, expanded = weighted_astar(ROOM, ROBOT_START, find_bin(ROOM), w)
        name = "no heuristic (Dijkstra)" if w == 0 else f"A* weight {w:g}"
        print(f"   {name:24} path {length} steps, squares looked at {expanded}")

    print("\n6) FOURIER: a 64-reading sensor log with a wheel wobble (8 cycles) and noise.")
    rng = random.Random(3)
    clean = [3.0 - 0.02 * t for t in range(64)]
    wobble = [0.6 * math.sin(2 * math.pi * 8 * t / 64) for t in range(64)]
    log = [c + w + rng.gauss(0, 0.1) for c, w in zip(clean, wobble)]
    fixed, k = remove_peak(log)
    print(f"   strongest rhythm found at {k} cycles per log (we put it at 8)")
    print(f"   typical error vs the true distance: {rms(log, clean):.2f} m before, {rms(fixed, clean):.2f} m after removing it")

    print("\n7) MOMENTUM: Lesson 3's braking-distance fit. Steps until the error is below 0.001.")
    for lr, beta in ((0.1, 0.0), (0.1, 0.5), (0.1, 0.9), (0.3, 0.0)):
        s = fit_steps(STOP_DATA, lr, beta, 0.001)
        print(f"   learning rate {lr}, momentum {beta}: {s if s else 'never (diverged or too slow)'} steps")

    print("\n8) REINFORCEMENT LEARNING: Lesson 7's maze. How much exploring is best? (5 seeds each)")
    start, goal = find_char(MAZE, "S"), find_char(MAZE, "G")
    for eps in (0.0, 0.05, 0.2, 0.5):
        lengths, firsts = [], []
        for seed in range(5):
            Q, log = q_learn(MAZE, start, goal, epsilon=eps, rng=random.Random(seed))
            path = greedy_path(Q, MAZE, start, goal)
            lengths.append(len(path) - 1 if path and path[-1] == goal else None)
            firsts.append(next((i for i, n in enumerate(log) if n <= 9), None))
        ok = [x for x in lengths if x is not None]
        print(f"   epsilon {eps:4}: learned route found by {len(ok)}/5 seeds (length {min(ok) if ok else '-'}), "
              f"first 9-step-or-better episode: {firsts}")
