"""Week 6: the gyroscope, drift, and sensor fusion. Two imperfect sensors make one good one.

Which way is the phone pointing? Two sensors can tell you, and each is bad in its own way:
  ACCELEROMETER  angle = atan2(y, x) of the gravity reading. Never drifts, but shakes wildly whenever you move.
  GYROSCOPE      measures how fast the phone is turning (degrees per second). Add it up over time and you get
                 the angle: smooth, even while moving. But a tiny error in every reading adds up: it DRIFTS.
A COMPLEMENTARY FILTER trusts the gyro from moment to moment, and the accelerometer over the long run:
    angle = predicted_by_gyro + (1 - alpha) * (accelerometer_angle - predicted_by_gyro)
Every self-balancing scooter, drone and phone does a version of this.

Real data: data/phone_acc.csv and data/phone_gyro.csv (the same recording as week 3).
Careful: angles WRAP AROUND. 179 degrees + 2 degrees is -179, not 181.
"""

import math
from pathlib import Path

from lesson21_phone import read_phone_csv, read_labels

DATA = Path(__file__).resolve().parent / "data"
DT = 0.02           # 50 readings a second


# ---------------- YOUR HOMEWORK ----------------

def wrap(angle):
    """Bring any angle (degrees) into the range -180 (included) to 180 (not included).
    wrap(190) -> -170, wrap(-190) -> 170, wrap(360) -> 0. Tip: (angle + 180) % 360 - 180"""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 22: write this function")


def accel_angle(x, y):
    """The phone's angle from the accelerometer: atan2(y, x), in degrees."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 22: write this function")


def integrate_gyro(start_angle, rates, dt):
    """Add up the turning: start at start_angle, and for each rate (degrees per second) add rate * dt, wrapping
    every time. Return the list of angles, one per rate (the first one already includes rates[0] * dt)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 22: write this function")


def complementary(start_angle, rates, accel_angles, dt, alpha):
    """Fuse the two sensors. Start at start_angle. For each (rate, accel_angle):
        predicted = angle + rate * dt                                     (trust the gyro now)
        angle = wrap(predicted + (1 - alpha) * wrap(accel_angle - predicted))   (nudge towards the accelerometer)
    Return the list of angles. alpha near 1 = mostly gyro; alpha 0 = accelerometer only."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 22: write this function")


# ---------------- provided ----------------

def load(start=0.0, end=91.0):
    """Angles from the accelerometer and turning rates from the gyro (degrees per second), between start and end.
    The phone turns about its z axis here, so the rate is minus the gyro's z reading. (After 91 s the phone lies
    so flat that this angle stops making sense: a real limit of using one angle for a 3D object.)"""
    t, ax, ay, _ = read_phone_csv(DATA / "phone_acc.csv")
    _, _, _, gz = read_phone_csv(DATA / "phone_gyro.csv")
    keep = [i for i, ti in enumerate(t) if start <= ti < end]
    return ([t[i] for i in keep], [accel_angle(ax[i], ay[i]) for i in keep], [-math.degrees(gz[i]) for i in keep])


def still_angle(t, angles, start, end):
    """The true angle during a still stretch: the accelerometer, averaged over the whole stretch."""
    seg = [a for ti, a in zip(t, angles) if start <= ti < end]
    s = sum(math.sin(math.radians(a)) for a in seg)
    c = sum(math.cos(math.radians(a)) for a in seg)
    return math.degrees(math.atan2(s, c))


def wobble(t, est, start, end, truth):
    seg = [wrap(e - truth) for ti, e in zip(t, est) if start <= ti < end]
    return math.sqrt(sum(x * x for x in seg) / len(seg))


if __name__ == "__main__":
    t, acc, rate = load(0, 91)
    print("1) DRIFT. Standing still for 20 s (5-25 s): the accelerometer's angle barely moves (it's the truth here).")
    t2, acc2, rate2 = load(5.0, 24.6)
    gyro = integrate_gyro(acc2[0], rate2, DT)
    end_truth = still_angle(t2, acc2, 23.6, 24.6)
    bias = sum(rate2) / len(rate2)
    print(f"   accelerometer: {acc2[0]:+.1f} degrees at the start, {end_truth:+.1f} at the end")
    print(f"   gyroscope alone: {gyro[-1]:+.1f} at the end, so {wrap(gyro[-1] - end_truth):+.1f} degrees off after 20 s "
          f"(it reads {bias:+.3f} degrees a second while still: that's its bias)")
    print(f"   at that rate, after 10 minutes it would be {bias * 600:+.0f} degrees off")
    print("\n2) SHAKE. Standing, sitting, standing, then lying down (0-91 s). Still stretches checked against the truth:")
    gyro = integrate_gyro(acc[0], rate, DT)
    still = [(s, e) for s, e, w in read_labels() if w in ("standing", "sitting", "laying") and e <= 91]
    for name, est in [("accelerometer alone", acc), ("gyroscope alone", gyro)] + \
                     [(f"complementary alpha {a}", complementary(acc[0], rate, acc, DT, a)) for a in (0.9, 0.98)]:
        errs = [wobble(t, est, s, e, still_angle(t, acc, s, e)) for s, e in still]
        print(f"   {name:26} typical error while still: {sum(errs) / len(errs):5.2f} degrees")

    print("\n3) WALKING (150-162 s): the accelerometer shakes with every step.")
    t3, acc3, rate3 = load(149.9, 161.6)
    truth = still_angle(t3, acc3, 149.9, 161.6)
    for name, est in [("accelerometer alone", acc3), ("gyroscope alone", integrate_gyro(acc3[0], rate3, DT)),
                      ("complementary alpha 0.98", complementary(acc3[0], rate3, acc3, DT, 0.98))]:
        print(f"   {name:26} wobbles {wobble(t3, est, 149.9, 161.6, truth):5.2f} degrees around its average")
