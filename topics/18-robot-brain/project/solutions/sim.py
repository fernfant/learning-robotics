"""The simulator: runs Robo-Helper with any "brain" and records everything it does.
Provided for you (no TODOs). Used from Week 10 (after the capstone) onwards.

    python3 sim.py "put the red and blue blocks away"            (default brain: word counter)
    python3 sim.py "tidy the room" --brain tinylm --watch         (watch it move, frame by frame)

A brain turns a command into robot behaviour. Every brain gets the SAME robot, room and surprises,
so any difference you see is the brain's doing.
"""

import json
import sys
import time

from world import ROOM, OBJECTS, find_bin, render
from lesson11_robohelper import RoboHelper
from lesson10_llm_safety import validate_action

CAT = (4, 1)   # the surprise obstacle used in every bake-off task, unless a task says otherwise


class SimRobot(RoboHelper):
    """A RoboHelper that records a frame after every move or message, and offers small
    'tool' actions (look, go_to, pick_up, put_in_bin) that an AI agent can call one at a time."""

    def __init__(self, surprises=(CAT,), seed=0):
        super().__init__(surprises=surprises, seed=seed)
        self.frames = []
        self.on_event("start", "")

    def on_event(self, kind, detail=""):
        self.frames.append({
            "kind": kind, "detail": str(detail), "pos": list(self.pos), "holding": self.holding,
            "objects": {k: list(v) for k, v in self.objects.items() if k not in self.binned and k != self.holding},
            "binned": sorted(self.binned), "seen": sorted(list(p) for p in self.known_blocked),
        })

    # ---- tools an agent can call ----
    def look(self):
        objs = {k: tuple(v) for k, v in self.objects.items() if k not in self.binned}
        return (f"Robot at {self.pos}, holding {self.holding or 'nothing'}. Bin at {find_bin(self.room)}. "
                f"Blocks not yet in the bin: {objs or 'none'}. In the bin: {sorted(self.binned) or 'nothing'}. "
                f"Obstacles seen so far: {sorted(self.known_blocked) or 'none'}.")

    def go_to(self, obj):
        if obj not in self.objects:
            return False, f"Unknown object {obj!r}. Known: {sorted(self.objects)}"
        if obj in self.binned:
            return False, f"The {obj} is already in the bin."
        ok = self.drive_to(self.objects[obj])
        return ok, (f"Arrived at the {obj} at {self.pos}." if ok else f"Couldn't reach the {obj}.")

    def pick_up(self, obj):
        if self.holding:
            return False, f"Already holding the {self.holding}. Put it in the bin first."
        if obj not in self.objects or obj in self.binned:
            return False, f"There's no {obj!r} here to pick up."
        if tuple(self.objects[obj]) != tuple(self.pos):
            return False, f"Not at the {obj}: it's at {self.objects[obj]}, robot is at {self.pos}. Use go_to first."
        self.holding = obj
        self.on_event("pick", obj)
        return True, f"Picked up the {obj}."

    def put_in_bin(self):
        if not self.holding:
            return False, "Not holding anything."
        obj = self.holding
        if not self.drive_to(find_bin(self.room)):
            return False, "Couldn't reach the bin."
        self.binned.add(obj)
        self.objects[obj] = find_bin(self.room)
        self.holding = None
        self.on_event("drop", obj)
        return True, f"The {obj} is in the bin."

    def do_action(self, action):
        """Run one validated {"intent", "object"} action through the normal run_command path."""
        result = self.run_command("", parser=lambda _: action)
        self.on_event("say", result["message"])
        return result


def run_brain(brain, command, surprises=(CAT,), seed=0):
    """Give one command to a brain, on a fresh robot. Returns (robot, result).
    result = {"reply": str, "actions": [...], "seconds": float, "tokens_in": int, "tokens_out": int}"""
    robot = SimRobot(surprises=surprises, seed=seed)
    start = time.perf_counter()
    result = brain.act(robot, command)
    result.setdefault("seconds", time.perf_counter() - start)
    result.setdefault("tokens_in", 0)
    result.setdefault("tokens_out", 0)
    robot.on_event("done", result.get("reply", ""))
    return robot, result


def frame_text(frame, room=ROOM):
    objs = {k: tuple(v) for k, v in frame["objects"].items()}
    pic = render(room, tuple(frame["pos"]), objs)
    rows = [list(r) for r in pic.split("\n")]
    for x, y in frame["seen"]:
        rows[y][x] = "X"
    note = f'{frame["kind"]}: {frame["detail"]}' if frame["detail"] else frame["kind"]
    held = f'  holding: {frame["holding"]}' if frame["holding"] else ""
    return "\n".join("".join(r) for r in rows) + f"\n{note}{held}  | in bin: {', '.join(frame['binned']) or '-'}"


def watch(frames, delay=0.15):
    for f in frames:
        print("\033[2J\033[H" + frame_text(f))
        time.sleep(delay)


def save_trace(path, brain_name, command, robot, result):
    with open(path, "w") as fh:
        json.dump({"brain": brain_name, "command": command, "reply": result.get("reply", ""),
                   "seconds": result["seconds"], "tokens_in": result["tokens_in"], "tokens_out": result["tokens_out"],
                   "frames": robot.frames}, fh, indent=1)


if __name__ == "__main__":
    from brains import get_brain
    args = sys.argv[1:]
    name = args[args.index("--brain") + 1] if "--brain" in args else "words"
    words = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--brain")]
    command = " ".join(words) or "put the red block in the bin"
    brain = get_brain(name)
    robot, result = run_brain(brain, command)
    if "--watch" in args:
        watch(robot.frames)
    else:
        print(frame_text(robot.frames[-1]))
    print(f"\n[{brain.name}] {result.get('reply', '')}  ({result['seconds'] * 1000:.1f} ms, {len(robot.frames)} frames)")
