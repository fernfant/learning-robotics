"""Week 9: wheels, odometry and PID. Driving a real(istic) robot.

The grid robot jumped between squares. Robo-Helper's body (body.py) has two wheels and drives smoothly:
  KINEMATICS   both wheels roll forward d_left and d_right metres. The robot moves forward their average,
               and turns by (d_left - d_right) / wheel_base radians (a faster right wheel turns it LEFT).
               Here headings grow clockwise on screen (y grows down), so turning left makes the heading smaller.
  ODOMETRY     the robot can't see where it is, but its ENCODERS count wheel ticks. Turn ticks into metres, add up
               every little move, and you get an estimate of where it is. Wheels slip, so the estimate DRIFTS.
  PID          to drive to a point, steer by the ERROR (how far off we are):
                   output = kp * error  +  ki * (error added up over time)  +  kd * (how fast the error is changing)
               P pushes, I fixes small steady errors, D stops it overshooting. Cruise control and drones use this.
"""

import math

from body import Body, WHEEL_BASE, WHEEL_RADIUS, TICKS_PER_REV, centre

DT = 0.05     # 20 control steps a second


# ---------------- YOUR HOMEWORK ----------------

def ticks_to_metres(ticks, ticks_per_rev=TICKS_PER_REV, radius=WHEEL_RADIUS):
    """One full wheel turn (ticks_per_rev ticks) rolls the wheel's circumference, 2 * pi * radius metres."""
    # BEGIN SOLUTION
    return ticks / ticks_per_rev * 2 * math.pi * radius
    # END SOLUTION


def move_pose(pose, d_left, d_right, wheel_base=WHEEL_BASE):
    """Odometry: pose is (x, y, heading in RADIANS). The wheels rolled d_left and d_right metres.
        d = (d_left + d_right) / 2          dtheta = (d_left - d_right) / wheel_base
        x += d * cos(heading + dtheta / 2)  y += d * sin(heading + dtheta / 2)   heading += dtheta
    Return the new (x, y, heading). (Using heading + dtheta / 2 is a little more accurate on curves.)"""
    # BEGIN SOLUTION
    x, y, h = pose
    d, dtheta = (d_left + d_right) / 2, (d_left - d_right) / wheel_base
    return x + d * math.cos(h + dtheta / 2), y + d * math.sin(h + dtheta / 2), h + dtheta
    # END SOLUTION


def errors_to(pose, target):
    """How far, and which way, to the target (x, y)?
    distance = straight-line distance. heading_error = (direction to the target) - (current heading), in radians,
    wrapped into -pi..pi so the robot always turns the short way. Return (distance, heading_error)."""
    # BEGIN SOLUTION
    x, y, h = pose
    want = math.atan2(target[1] - y, target[0] - x)
    return math.hypot(target[0] - x, target[1] - y), (want - h + math.pi) % (2 * math.pi) - math.pi
    # END SOLUTION


def pid_step(state, error, dt, kp, ki, kd):
    """One step of a PID controller. state is (integral, previous_error), or None the very first time.
        integral = integral + error * dt
        derivative = (error - previous_error) / dt      (0 the first time)
        output = kp * error + ki * integral + kd * derivative
    Return (output, (integral, error))."""
    # BEGIN SOLUTION
    integral, prev = state if state else (0.0, error)
    integral += error * dt
    output = kp * error + ki * integral + kd * (error - prev) / dt
    return output, (integral, error)
    # END SOLUTION


# ---------------- provided: driving with your pieces ----------------

class Odometer:
    """Keeps the robot's own estimate of its pose, from the encoders only (your move_pose and ticks_to_metres)."""

    def __init__(self, body, pose):
        self.body, self.pose = body, pose
        self.last = body.encoders()

    def update(self):
        now = self.body.encoders()
        dl, dr = (ticks_to_metres(n - o) for n, o in zip(now, self.last))
        self.last = now
        self.pose = move_pose(self.pose, dl, dr)
        return self.pose


def drive_to(body, odo, target, kp=3.0, ki=0.0, kd=0.15, max_speed=0.3, tolerance=0.05, max_steps=400):
    """Drive to target (x, y) using only the odometer's estimate. Heading is controlled by your pid_step.
    Returns (steps taken, the largest heading error seen while driving, in degrees)."""
    state, worst = None, 0.0
    for step in range(max_steps):
        pose = odo.update()
        dist, herr = errors_to(pose, target)
        if dist < tolerance:
            return step, worst
        turn, state = pid_step(state, herr, DT, kp, ki, kd)
        speed = min(max_speed, dist) * max(0.0, math.cos(herr))      # slow down when facing the wrong way
        body.drive(speed + turn * WHEEL_BASE / 2, speed - turn * WHEEL_BASE / 2, DT)   # left faster -> heading grows
        if step > 5:
            worst = max(worst, abs(math.degrees(herr)))
    return max_steps, worst


def turn_to(body, odo, heading_deg, kp, ki=0.0, kd=0.0, seconds=6.0):
    """Turn on the spot to face heading_deg, using your pid_step on the heading error.
    Returns the list of headings (degrees) the odometer saw, one per step."""
    state, seen = None, []
    for _ in range(int(seconds / DT)):
        pose = odo.update()
        err = (math.radians(heading_deg) - pose[2] + math.pi) % (2 * math.pi) - math.pi
        turn, state = pid_step(state, err, DT, kp, ki, kd)
        body.drive(turn * WHEEL_BASE / 2, -turn * WHEEL_BASE / 2, DT)
        seen.append(math.degrees(pose[2]))
    return seen


def settle_report(headings, goal):
    over = max(0.0, max(headings) - goal)
    settled = next((i for i in range(len(headings)) if all(abs(h - goal) < 2 for h in headings[i:])), None)
    return over, (settled * DT if settled is not None else None)


def true_error(body, target):
    x, y, _ = body.true_pose()
    return math.hypot(target[0] - x, target[1] - y)


def odometry_drift(body, odo):
    x, y, _ = body.true_pose()
    return math.hypot(odo.pose[0] - x, odo.pose[1] - y)


SQUARE_ROUTE = [centre(s) for s in [(4, 4), (4, 5), (1, 5), (1, 4)]]   # a loop in the open middle of the room


if __name__ == "__main__":
    print("1) ODOMETRY. Drive a loop 3 times using only the encoders. Where does the robot THINK it is, vs really?")
    for slip in (0.0, 0.05, 0.15):
        body = Body(start=(1, 4), slip=slip, seed=1, cat=False)
        odo = Odometer(body, (*centre((1, 4)), 0.0))
        for lap in range(3):
            for p in SQUARE_ROUTE:
                drive_to(body, odo, p)
        print(f"   wheel slip {slip:4.0%}: after 3 laps the estimate is {odometry_drift(body, odo):.2f} m from the truth")

    print("\n2) PID. Turn on the spot from facing east (0) to facing south (90 degrees). Perfect wheels, but motors with momentum.")
    for name, gains in [("P only, kp 2", (2.0, 0.0, 0.0)), ("P only, kp 8", (8.0, 0.0, 0.0)),
                        ("P only, kp 20", (20.0, 0.0, 0.0)), ("PD, kp 20, kd 1.5", (20.0, 0.0, 1.5))]:
        body = Body(start=(1, 5), slip=0.0, mismatch=0.0, seed=2, cat=False)
        odo = Odometer(body, (*centre((1, 5)), 0.0))
        over, settled = settle_report(turn_to(body, odo, 90, *gains), 90)
        print(f"   {name:18} overshoots by {over:5.1f} degrees, settles within 2 degrees after "
              + (f"{settled:.1f} s" if settled is not None else "never (still wobbling after 6 s)"))

    print("\n3) TOGETHER. Drive along the bottom corridor from (1, 5) to (8, 5), 3.5 m, using odometry and PD steering.")
    goal = centre((8, 5))
    for mismatch in (0.0, 0.02):
        body = Body(start=(1, 5), slip=0.05, mismatch=mismatch, seed=2, cat=False)
        odo = Odometer(body, (*centre((1, 5)), 0.0))
        steps, _ = drive_to(body, odo, goal)
        print(f"   left wheel {mismatch:3.0%} bigger: the robot thinks it arrived after {steps * DT:.1f} s; "
              f"really it's {true_error(body, goal):.2f} m away")
