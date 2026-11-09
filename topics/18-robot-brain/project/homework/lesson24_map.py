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
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 24: write this function")


def square_of(x, y):
    """Which grid square is the point (x, y) in? Each square is SQUARE (0.5) metres: (int(x // SQUARE), int(y // SQUARE))."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 24: write this function")


def squares_passed(x0, y0, x1, y1, step=0.05):
    """The squares a beam passes through on its way from (x0, y0) to (x1, y1), NOT counting the square it ends in.
    Walk along the line in small steps (step metres), and collect each new square in order, without repeats."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 24: write this function")


def add_scan(votes, pose, scan):
    """Add one scan's votes. votes is a dict: square -> [wall_votes, free_votes].
    For each (beam_deg, distance) in scan: every square the beam passed gets a free vote; if distance < MAX_RANGE,
    the square where it ended gets a wall vote. Squares not in votes yet start at [0, 0]."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 24: write this function")


def to_map(votes, width, height):
    """Turn votes into a map: a list of strings, one per row. A square is "#" if it has more wall votes than free
    votes, "." if it has any votes otherwise, and "?" if no beam ever reached it."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 24: write this function")


# ---------------- provided ----------------

ROUTE = [centre(s) for s in [(1, 5), (3, 5), (4, 3), (5, 1), (7, 1), (8, 3), (8, 5), (5, 5), (3, 5), (1, 4), (1, 1)]]


def explore(use_true_pose, mismatch=0.02, seed=3):
    """Drive the route, scanning every 10 control steps, and build a map. Returns (map, robot body)."""
    from lesson23_wheels import Odometer, drive_to
    body = Body(start=(1, 5), mismatch=mismatch, seed=seed)
    odo = Odometer(body, (*centre((1, 5)), 0.0))
    votes, step = {}, 0
    for target in ROUTE:
        for _ in range(40):
            if drive_to(body, odo, target, max_steps=10)[0] < 10:
                break
            x, y, h = body.true_pose()
            pose = (x, y, math.radians(h)) if use_true_pose else odo.pose
            add_scan(votes, pose, body.scan())
            step += 1
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
