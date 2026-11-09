"""Robo-Helper's BODY: a simulated robot with two wheels and a laser scanner, in the same room. Provided for you.

The grid robot hopped from square to square and always knew exactly where it was. A real robot doesn't:
  - it drives with two WHEELS. Turn them at the same speed and it goes straight; turn them differently and it turns.
  - the wheels SLIP a little, differently every time, so it never moves exactly as told.
  - ENCODERS count how far each wheel turned (in ticks). That's all it really knows about its own motion.
  - a LASER SCANNER measures the distance to the nearest wall in 36 directions, with a little noise.

Coordinates are in metres. One grid square is 0.5 m, so the room is 5 m wide and 4 m tall.
x grows to the right, y grows DOWN the screen (like the grid). Heading 0 = facing east (right),
90 degrees = facing south (down), 180 = west, -90 = north.

The robot's TRUE pose is hidden inside Body. Your code only sees encoders and scans, like a real robot.
true_pose() is there for checking your work, never for driving.
"""

import math
import random

from world import ROOM, ROBOT_START

SQUARE = 0.5              # metres per grid square
WHEEL_BASE = 0.2          # metres between the two wheels
WHEEL_RADIUS = 0.03       # metres
TICKS_PER_REV = 360       # encoder ticks per wheel turn
RADIUS = 0.1              # the robot is a circle, 0.1 m across... from its centre
CAT = (4, 1)
CAT_XY, CAT_R = ((CAT[0] + 0.5) * SQUARE, (CAT[1] + 0.5) * SQUARE), 0.15


def centre(square):
    """The middle of a grid square, in metres."""
    return ((square[0] + 0.5) * SQUARE, (square[1] + 0.5) * SQUARE)


def is_wall(x, y, room=ROOM, cat=True):
    """True if the point (x, y) in metres is inside a wall, outside the room, or inside the cat."""
    gx, gy = int(math.floor(x / SQUARE)), int(math.floor(y / SQUARE))
    if gy < 0 or gy >= len(room) or gx < 0 or gx >= len(room[0]) or room[gy][gx] == "#":
        return True
    return cat and math.hypot(x - CAT_XY[0], y - CAT_XY[1]) < CAT_R


def ray(x, y, angle, room=ROOM, cat=True, max_range=4.0, step=0.01):
    """Distance from (x, y) along angle (radians) to the first wall, or max_range if none."""
    dx, dy = math.cos(angle), math.sin(angle)
    d = 0.0
    while d < max_range:
        d += step
        if is_wall(x + dx * d, y + dy * d, room, cat):
            return d
    return max_range


class Body:
    def __init__(self, start=None, heading_deg=0.0, slip=0.05, scan_noise=0.02, seed=0, cat=True, mismatch=0.02, lag=0.25):
        self.x, self.y = centre(start or ROBOT_START)
        self.theta = math.radians(heading_deg)
        self.rng = random.Random(seed)
        self.slip, self.scan_noise, self.cat = slip, scan_noise, cat
        self.mismatch = mismatch     # the right wheel is a little bigger than the left: a real, steady error
        self.lag = lag               # motors take about this many seconds to reach a new speed (they have momentum)
        self.vl = self.vr = 0.0      # how fast the motors are really turning right now
        self.left_turned = self.right_turned = 0.0    # metres each wheel really rolled
        self.bumped = False
        self.trail = [(self.x, self.y)]

    def drive(self, v_left, v_right, dt):
        """Turn the motors so each wheel should roll at these speeds (metres per second) for dt seconds.
        The encoders count what the MOTORS did. On the floor, the wheels slip a bit, and the right wheel is
        slightly bigger, so the robot really moves a little differently."""
        k = min(1.0, dt / self.lag) if self.lag else 1.0
        self.vl += (v_left - self.vl) * k
        self.vr += (v_right - self.vr) * k
        self.left_turned += self.vl * dt
        self.right_turned += self.vr * dt
        vl = self.vl * (1 + self.rng.gauss(0, self.slip))
        vr = self.vr * (1 + self.mismatch) * (1 + self.rng.gauss(0, self.slip))
        d, dtheta = (vl + vr) / 2 * dt, (vr - vl) / WHEEL_BASE * dt
        nx = self.x + d * math.cos(self.theta + dtheta / 2)
        ny = self.y + d * math.sin(self.theta + dtheta / 2)
        hit = any(is_wall(nx + RADIUS * math.cos(a), ny + RADIUS * math.sin(a), cat=self.cat)
                  for a in (i * math.pi / 4 for i in range(8)))
        self.theta = (self.theta + dtheta + math.pi) % (2 * math.pi) - math.pi
        if hit:
            self.bumped = True        # the wheels turned, but the robot is stuck against something
            return
        self.x, self.y = nx, ny
        self.trail.append((nx, ny))

    def encoders(self):
        """(left_ticks, right_ticks): how far each wheel has turned since the start, in whole ticks."""
        per_metre = TICKS_PER_REV / (2 * math.pi * WHEEL_RADIUS)
        return int(self.left_turned * per_metre), int(self.right_turned * per_metre)

    def scan(self, beams=36):
        """[(angle_deg, distance_m), ...]: the laser scanner, angles relative to where the robot faces."""
        out = []
        for i in range(beams):
            rel = i * 360 / beams
            d = ray(self.x, self.y, self.theta + math.radians(rel), cat=self.cat)
            out.append((rel, max(0.0, d + self.rng.gauss(0, self.scan_noise))))
        return out

    def true_pose(self):
        """(x, y, heading_deg). For CHECKING only: a real robot can't know this."""
        return self.x, self.y, math.degrees(self.theta)


def draw(body=None, estimate=None, room=ROOM, grid=None):
    """A picture of the room, 4 characters per square: R = where the robot really is, E = where it thinks it is."""
    W, H = len(room[0]) * 4, len(room) * 4
    pic = [[" " for _ in range(W)] for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if (grid is not None and grid[y // 4][x // 4] == "#") or (grid is None and room[y // 4][x // 4] == "#"):
                pic[y][x] = "#"
    if grid is None:
        cx, cy = CAT[0] * 4 + 2, CAT[1] * 4 + 2
        pic[cy][cx] = "c"
    put = lambda x, y, ch: 0 <= int(y / SQUARE * 4) < H and 0 <= int(x / SQUARE * 4) < W and pic[int(y / SQUARE * 4)].__setitem__(int(x / SQUARE * 4), ch)
    if body is not None:
        for x, y in body.trail[::3]:
            put(x, y, ".")
        put(body.x, body.y, "R")
    if estimate is not None:
        put(estimate[0], estimate[1], "E")
    return "\n".join("".join(row) for row in pic)
