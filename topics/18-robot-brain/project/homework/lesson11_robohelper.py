"""Lesson 11: the capstone. Robo-Helper puts it all together.

    command text --(L9 parser / L10 safety checks)--> action
    action --(L6 A* planner)--> route
    route --(L1 moving, L2 sensing, L4/L5 stop detector, L3 safe speed)--> driving
    result --(L5 evaluation habits)--> success rate on a test set

Most of this file is written for you. Your job: finish run_command() and evaluate().
"""

import random

from world import ROOM, OBJECTS, ROBOT_START, find_bin, render
from lesson02_sensors import distance_to_wall
from lesson03_learning import STOP_DATA, fit_line, max_safe_speed
from lesson04_neuron import make_obstacle_data, train_neuron, should_stop
from lesson05_evaluate import safest_threshold
from lesson06_paths import astar_path
from lesson09_commands import TRAIN, train_intent_model, parse_command
from lesson10_llm_safety import validate_action

SQUARE = 0.5  # metres per grid square


class RoboHelper:
    def __init__(self, room=ROOM, objects=None, start=ROBOT_START, surprises=(), seed=0):
        self.room = room
        self.objects = dict(objects if objects is not None else OBJECTS)
        self.pos = start
        self.holding = None
        self.binned = set()
        self.surprises = set(surprises)   # things NOT on the map (a cat, a bag...)
        self.known_blocked = set()        # surprises the robot has seen so far
        self.log = []
        rng = random.Random(seed)
        # Lesson 9: understand words. Lesson 3: braking. Lessons 4-5: a safe stop detector.
        self.intent_model = train_intent_model(TRAIN)
        self.w, self.b, _ = fit_line(STOP_DATA)
        data = make_obstacle_data(450, rng)
        self.stop_w, self.stop_b = train_neuron(data)
        self.stop_threshold = safest_threshold(self.stop_w, self.stop_b, data)

    def say(self, msg):
        self.log.append(msg)
        self.on_event("say", msg)

    def on_event(self, kind, detail=""):
        """Called after every move and message. Does nothing here: the simulator (sim.py) uses it to record."""

    def parse(self, text):
        return parse_command(self.intent_model, text)

    def drive_to(self, target, max_replans=5):
        """Drive to target, stopping and replanning if a surprise blocks the way.
        Returns True if we arrived."""
        replans = 0
        while self.pos != target:
            path, _ = astar_path(self.room, self.pos, target, blocked=self.known_blocked)
            if path is None:
                self.say(f"I can't find a way to {target}.")
                return False
            for nxt in path[1:]:
                direction = {(1, 0): "E", (-1, 0): "W", (0, 1): "S", (0, -1): "N"}[(nxt[0] - self.pos[0], nxt[1] - self.pos[1])]
                speed = max_safe_speed(self.w, self.b, distance_to_wall(self.room, self.pos, direction) * SQUARE + SQUARE)
                if nxt in self.surprises:
                    # The sensor sees something one square ahead, closing at our speed.
                    if should_stop(self.stop_w, self.stop_b, (SQUARE, speed), self.stop_threshold):
                        self.say(f"Something is in the way at {nxt}! Stopping and finding another route.")
                        self.known_blocked.add(nxt)
                        replans += 1
                        if replans > max_replans:
                            self.say("Too many surprises, giving up.")
                            return False
                        break
                self.pos = nxt
                self.on_event("move", nxt)
            else:
                continue
        return True

    def run_command(self, text, parser=None):
        """Turn text into an action, check it, then do it. Return a result dict:
            {"ok": bool, "action": action_or_None, "message": str}
        Steps:
          1. action = (parser or self.parse)(text)
          2. ok, reason = validate_action(action, set(self.objects)); if not ok, return a failure
             with message "Sorry, I can't do that: <reason>"
          3. intent "stop": message "Stopping.", ok True
          4. intent "find": if the object is in self.binned -> "The X is in the bin.",
             elif self.holding == X -> "I'm holding the X.", else "The X is at (x, y)."
          5. intent "go": ok = self.drive_to(self.objects[X]); message "I'm next to the X." or a failure
          6. intent "put": if X already binned -> ok True, "The X is already in the bin."
             else drive_to the object, set self.holding = X, drive_to find_bin(self.room),
             then self.binned.add(X), self.objects[X] = bin position, self.holding = None,
             message "The X is in the bin."
        """
        # TODO: write this part. Read the docstring above carefully.
        raise NotImplementedError("Lesson 11: write this function")


# (command, what a correct robot should end up doing)
#   expect "ok" / "refuse": should the command succeed or be safely refused?
#   binned: objects that must be in the bin afterwards (checked on a fresh robot per test)
TEST_COMMANDS = [
    ("put the red block in the bin", "ok", {"red block"}),
    ("throw the blue block away", "ok", {"blue block"}),
    ("tidy up the green block", "ok", {"green block"}),
    ("go to the blue block", "ok", set()),
    ("drive over to the green block", "ok", set()),
    ("where is the red block", "ok", set()),
    ("find the green block", "ok", set()),
    ("stop", "ok", set()),
    ("halt now", "ok", set()),
    ("put the purple block in the bin", "refuse", set()),
    ("make me a sandwich", "refuse", set()),
    ("go to the moon", "refuse", set()),
]


def evaluate(commands=TEST_COMMANDS, surprises=((4, 1),), seed=0):
    """Run each command on a FRESH RoboHelper (with the given surprises).
    A test passes if:
      expect == "ok"     -> result["ok"] is True and robot.binned is EXACTLY the set `binned`
                            (nothing extra: binning the wrong block is a failure, even if the right one is in too)
      expect == "refuse" -> result["ok"] is False (refusing is the correct, safe behaviour)
    Return (pass_rate, failures) where failures is a list of (command, message)."""
    # TODO: write this part. Read the docstring above carefully.
    raise NotImplementedError("Lesson 11: write this function")


if __name__ == "__main__":
    robot = RoboHelper(surprises={(4, 1)})
    print(render(robot.room, robot.pos, robot.objects))
    for text in ["where is the blue block", "put the blue block in the bin", "where is the blue block"]:
        result = robot.run_command(text)
        print(f"> {text}\n  {result['message']}")
    print("  log:", robot.log)
    print(render(robot.room, robot.pos, {k: v for k, v in robot.objects.items() if k not in robot.binned}))
    rate, failures = evaluate()
    print(f"\nTest set: {rate:.0%} passed")
    for f in failures:
        print("  FAILED:", f)
