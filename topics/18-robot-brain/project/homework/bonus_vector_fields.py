"""Bonus (Course Module 22): gradient, divergence and curl, used to steer a robot.

A different way to drive than A*: give every point in the room an arrow (a VECTOR FIELD) and let the robot
follow the arrows. Pull towards the goal, push away from obstacles. That's a POTENTIAL FIELD planner.
  gradient    the arrows point downhill on a "height map" (the potential). Following them is gradient descent.
  divergence  how much the arrows spread out of a point (a source) or squeeze into it (a sink). The goal is a sink.
  curl        how much the arrows swirl. A little swirl around obstacles stops the robot getting stuck.

    python3 bonus_vector_fields.py
"""

import math

H = 1e-4  # step for numerical derivatives


# ---------- the maths, checked numerically ----------

def grad(phi, x, y):
    """Numerical gradient: how fast phi changes in x and in y."""
    return ((phi(x + H, y) - phi(x - H, y)) / (2 * H), (phi(x, y + H) - phi(x, y - H)) / (2 * H))


def div(F, x, y):
    """Divergence = dFx/dx + dFy/dy: positive = a source (arrows spread out), negative = a sink."""
    return (F(x + H, y)[0] - F(x - H, y)[0]) / (2 * H) + (F(x, y + H)[1] - F(x, y - H)[1]) / (2 * H)


def curl(F, x, y):
    """2D curl = dFy/dx - dFx/dy: positive = anticlockwise swirl (out of the screen), negative = clockwise."""
    return (F(x + H, y)[1] - F(x - H, y)[1]) / (2 * H) - (F(x, y + H)[0] - F(x, y - H)[0]) / (2 * H)


# ---------- a potential-field robot ----------

GOAL = (9.0, 5.0)
BOX = [(5.0, 5.0, 1.2)]                                    # (x, y, radius): one box between start and goal
SOFA = [(5.0, 3.8, 0.9), (5.0, 5.0, 0.9), (5.0, 6.2, 0.9)]  # three overlapping circles: a wall, like a sofa
OBSTACLES = list(BOX)
INFLUENCE = 2.0                        # obstacles only push within this distance of their edge


def attract(x, y, k=1.0):
    """Pull towards the goal: minus the gradient of k/2 * distance^2."""
    return (-k * (x - GOAL[0]), -k * (y - GOAL[1]))


def repel(x, y, k=6.0):
    """Push away from each obstacle, stronger the closer you are (the classic Khatib field)."""
    fx = fy = 0.0
    for ox, oy, r in OBSTACLES:
        dx, dy = x - ox, y - oy
        d = math.hypot(dx, dy)
        gap = max(d - r, 1e-3)
        if gap < INFLUENCE:
            push = k * (1 / gap - 1 / INFLUENCE) / gap ** 2
            fx, fy = fx + push * dx / d, fy + push * dy / d
    return fx, fy


def swirl(x, y, k=6.0):
    """The repelling push turned 90 degrees anticlockwise: it slides the robot AROUND the obstacle instead of
    straight back. A rotated field like this has curl."""
    fx, fy = repel(x, y, k)
    return (-fy, fx)


def drive(start, use_swirl, dt=0.02, steps=4000, max_speed=1.0):
    """Follow the field. Returns (reached_goal, path_length, end_point)."""
    x, y = start
    length = 0.0
    for _ in range(steps):
        ax, ay = attract(x, y)
        rx, ry = repel(x, y)
        sx, sy = swirl(x, y) if use_swirl else (0.0, 0.0)
        vx, vy = ax + rx + sx, ay + ry + sy
        speed = math.hypot(vx, vy)
        if speed > max_speed:
            vx, vy = vx / speed * max_speed, vy / speed * max_speed
        x, y = x + vx * dt, y + vy * dt
        length += math.hypot(vx, vy) * dt
        if math.hypot(x - GOAL[0], y - GOAL[1]) < 0.1:
            return True, length, (x, y)
    return False, length, (x, y)


def starts():
    """Start points on the left: 11 heights from y = 2.5 to 7.5."""
    return [(1.0, 2.5 + 0.5 * i) for i in range(11)]


if __name__ == "__main__":
    print("1) THE POST'S THREE FIELDS, checked numerically at a few points:")
    phi = lambda x, y: 1 - x ** 2 - 2 * y ** 2
    print(f"   grad phi at (0.5, 0.5) = ({grad(phi, 0.5, 0.5)[0]:.3f}, {grad(phi, 0.5, 0.5)[1]:.3f})   formula (-2x, -4y) = (-1, -2)")
    print(f"   grad phi at the top (0, 0) = ({grad(phi, 0, 0)[0]:.3f}, {grad(phi, 0, 0)[1]:.3f})   zero: a peak is flat")
    for name, F in (("(x, y)", lambda x, y: (x, y)), ("(-x, -y)", lambda x, y: (-x, -y))):
        print(f"   div {name:9} = {div(F, 0.3, -0.7):.3f}   ({'source' if div(F, 0.3, -0.7) > 0 else 'sink'})")
    for name, F in (("(-y, x)", lambda x, y: (-y, x)), ("(y, -x)", lambda x, y: (y, -x))):
        print(f"   curl {name:8} = {curl(F, 0.3, -0.7):.3f}   ({'anticlockwise, out of the screen' if curl(F, 0.3, -0.7) > 0 else 'clockwise, into the screen'})")

    print("\n2) THE ROBOT'S FIELD: goal at (9, 5), a box of radius 1.2 at (5, 5).")
    OBSTACLES[:] = BOX
    print(f"   div of the pull towards the goal = {div(attract, 7.0, 4.0):.2f}  (negative everywhere: the goal is a sink)")
    print(f"   curl of the pull = {curl(attract, 7.0, 4.0):.2f}  (a pure gradient field never swirls)")
    print(f"   curl of the swirl just above the box, at (5, 7) = {curl(swirl, 5.0, 7.0):.2f}  (not zero: it really swirls)")

    print("\n3) DRIVING: 11 starts on the left, follow the arrows to the goal. (Straight line: 8.0 m.)")
    for scene, obstacles in (("one box", BOX), ("a sofa (3 circles in a wall)", SOFA)):
        OBSTACLES[:] = obstacles
        print(f"   {scene}:")
        for use_swirl in (False, True):
            results = [drive(st, use_swirl) for st in starts()]
            ok = [r for r in results if r[0]]
            avg = sum(r[1] for r in ok) / len(ok) if ok else 0
            name = "gradient only   " if not use_swirl else "gradient + swirl"
            print(f"     {name} reached the goal from {len(ok):2}/11 starts" + (f", average path {avg:.1f} m" if ok else ""))
    print("   A* on a grid would find a way round every time, but it needs a map and a search first.")
