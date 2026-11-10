"""Week 11: a laser scanner, coordinate frames, and building a map.

The robot's laser scanner says things like "18 degrees to my left, a wall 1.3 m away". To put that on a map you
need two FRAMES:
  ROBOT FRAME   angles measured from where the robot faces (positive = clockwise on screen = to the robot's right)
  ROOM FRAME    the map's own x and y
Turning a reading from one frame into the other is the most-used trick in all of robotics:
    angle_in_room = robot_heading + beam_angle
    x = robot_x + distance * cos(angle_in_room),   y = robot_y + distance * sin(angle_in_room)

Then MAPPING: every beam says "the squares I passed through are FREE, and the square where I stopped is a WALL".
Count those votes over many scans and a map appears, including things the official map doesn't have (the cat!).
But you need to know where the robot WAS for each scan. Use the drifting odometry, and the map smears.
"""

import math

from world import ROOM
from body import Body, SQUARE, centre

MAX_RANGE = 4.0


# ---------------- YOUR HOMEWORK ----------------

def beam_end(pose, beam_deg, distance):
    """Robot frame -> room frame. pose is (x, y, heading in RADIANS); the beam points beam_deg degrees from the
    robot's heading and hit something distance metres away. Return the (x, y) of that point, in the room."""
    # BEGIN SOLUTION
    x, y, h = pose
    a = h + math.radians(beam_deg)
    return x + distance * math.cos(a), y + distance * math.sin(a)
    # END SOLUTION


def square_of(x, y):
    """Which grid square is the point (x, y) in? Each square is SQUARE (0.5) metres: (int(x // SQUARE), int(y // SQUARE))."""
    # BEGIN SOLUTION
    return int(x // SQUARE), int(y // SQUARE)
    # END SOLUTION


def squares_passed(x0, y0, x1, y1, step=0.05):
    """The squares a beam passes through on its way from (x0, y0) to (x1, y1), NOT counting the square it ends in.
    Walk along the line in small steps (step metres), and collect each new square in order, without repeats."""
    # BEGIN SOLUTION
    length = math.hypot(x1 - x0, y1 - y0)
    end, out = square_of(x1, y1), []
    for i in range(int(length / step) + 1):
        f = i * step / length if length else 0
        s = square_of(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
        if s != end and s not in out:
            out.append(s)
    return out
    # END SOLUTION


def add_scan(votes, pose, scan):
    """Add one scan's votes. votes is a dict: square -> [wall_votes, free_votes].
    For each (beam_deg, distance) in scan: every square the beam passed gets a free vote; if distance < MAX_RANGE,
    the square where it ended gets a wall vote. Squares not in votes yet start at [0, 0]."""
    # BEGIN SOLUTION
    for beam_deg, distance in scan:
        ex, ey = beam_end(pose, beam_deg, distance)
        for s in squares_passed(pose[0], pose[1], ex, ey):
            votes.setdefault(s, [0, 0])[1] += 1
        if distance < MAX_RANGE:
            votes.setdefault(square_of(ex, ey), [0, 0])[0] += 1
    return votes
    # END SOLUTION


def to_map(votes, width, height):
    """Turn votes into a map: a list of strings, one per row. A square is "#" if it has more wall votes than free
    votes, "." if it has any votes otherwise, and "?" if no beam ever reached it."""
    # BEGIN SOLUTION
    rows = []
    for y in range(height):
        row = ""
        for x in range(width):
            w, f = votes.get((x, y), [0, 0])
            row += "?" if w + f == 0 else "#" if w > f else "."
        rows.append(row)
    return rows
    # END SOLUTION


# ---------------- provided ----------------

ROUTE = [centre(s) for s in [(1, 5), (4, 5), (4, 3), (7, 3), (7, 1), (5, 1), (7, 1), (8, 1), (8, 5), (3, 5), (1, 5), (1, 1), (2, 1)]]


class TruePose:
    """Cheating, for comparison: always knows exactly where the robot is (a real robot can't)."""

    def __init__(self, body):
        self.body = body

    def update(self):
        x, y, h = self.body.true_pose()
        self.pose = (x, y, math.radians(h))
        return self.pose


def explore(use_true_pose, mismatch=0.02, seed=3):
    """Drive the route, scanning every 10 control steps, and build a map. Returns (map, robot body).
    use_true_pose=True cheats: it steers AND maps with the true pose. False uses only its own odometry."""
    from lesson23_wheels import Odometer, drive_to
    body = Body(start=(1, 5), mismatch=mismatch, seed=seed)
    tracker = TruePose(body) if use_true_pose else Odometer(body, (*centre((1, 5)), 0.0))
    tracker.update()
    votes = {}
    for target in ROUTE:
        for _ in range(40):
            if drive_to(body, tracker, target, max_steps=10)[0] < 10:
                break
            add_scan(votes, tracker.pose, body.scan())
    return to_map(votes, len(ROOM[0]), len(ROOM)), body


def score(mapped, room=ROOM):
    """Of the squares the map decided about, the share that match the real room (the cat's square doesn't count)."""
    right = total = 0
    for y, row in enumerate(room):
        for x, real in enumerate(row):
            m = mapped[y][x]
            if m == "?" or (x, y) == (4, 1):
                continue
            total += 1
            right += (m == "#") == (real == "#")
    return right / total, total


if __name__ == "__main__":
    print("1) FRAMES. The robot is at (1.0, 2.0) facing south (90 degrees, down the screen). The beam at +90 degrees")
    print("   points to the robot's RIGHT (y grows down, so positive angles turn clockwise), and hits a wall 1 m away.")
    print(f"   in the room, that point is {tuple(round(v, 2) for v in beam_end((1.0, 2.0, math.radians(90)), 90, 1.0))}")
    print("\n2) MAPPING. Drive around the room scanning, and let every beam vote.")
    for name, true in (("knowing exactly where it is (cheating)", True), ("using its own odometry", False)):
        mapped, body = explore(true)
        acc, n = score(mapped)
        print(f"\n   {name}: {acc:.0%} of {n} squares right")
        print("   real room      the robot's map")
        for real, m in zip(ROOM, mapped):
            print(f"   {real}     {m}")
    print("\n   Look at square (4, 1): the official map says floor, but the scanner found the cat.")
