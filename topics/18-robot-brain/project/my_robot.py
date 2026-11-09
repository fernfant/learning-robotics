"""YOUR robot. Run it after every lesson: it is built only from the code YOU have finished, so it grows as you do.

    python3 my_robot.py               talk to your robot (type 'help' to see what it can do, 'quit' to stop)
    python3 my_robot.py --show        the showcase: a demo of everything it can do, then YOUR exam (my_tasks.txt)
    python3 my_robot.py --solutions   the same, with the worked solutions (to see where you're heading)

Week 1 it can only follow arrows. By week 12 it understands sentences, plans, dodges the cat, checks itself
for safety, learns from a teacher and picks the routes people like. Nothing here is magic: every ability below
is one of your lesson files.
"""

import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOLUTIONS = "--solutions" in sys.argv
sys.path.insert(0, str(HERE / ("solutions" if SOLUTIONS else "homework")))

from world import ROOM, OBJECTS, ROBOT_START, find_bin, render   # noqa: E402  (the room is provided)

CAT = (4, 1)                 # the cat that isn't on the map
CACHE = {}                   # trained brains, shared by every robot in this run (training takes a while)
SAVE = HERE / "my_robot.json"
TASKS = HERE / "my_tasks.txt"
COLOURS = ("red", "blue", "green")
ARROWS = {"N": "north (up)", "S": "south (down)", "E": "east (right)", "W": "west (left)"}


def works(fn):
    try:
        fn()
        return True
    except NotImplementedError:
        return False


# Every ability: (key, week, lesson, what it lets the robot do, a test that runs YOUR code)
def _key():
    import os
    import importlib.util
    if not os.environ.get("ANTHROPIC_API_KEY") or importlib.util.find_spec("anthropic") is None:
        raise NotImplementedError("needs an API key and `pip install anthropic`")
    __import__("lesson18_world_class").validate_plan({"reply": "", "clarify": "", "plan": []}, set())


def _exam():
    from types import SimpleNamespace
    __import__("lesson19_bakeoff").score_task({"command": "x", "binned": set()}, SimpleNamespace(binned=set(), pos=ROBOT_START), {"reply": ""})


def _plans():
    from lesson15_tiny_lm import words_to_plan, plan_examples
    words_to_plan(["stop"])
    plan_examples(["bin {x}"], ["everything but the {c}"], random.Random(0))


ABILITIES = [
    ("move", "1", "01", "follows arrow commands like EESS", lambda: __import__("lesson01_moving").follow(ROOM, ROBOT_START, "E")),
    ("sense", "2", "02", "measures how far the walls are ('look')", lambda: __import__("lesson02_sensors").distance_to_wall(ROOM, ROBOT_START, "E")),
    ("brake", "2", "03", "knows how fast it can go and still stop", lambda: __import__("lesson03_learning").fit_line(__import__("lesson03_learning").STOP_DATA, steps=5)),
    ("stop", "3", "04-05", "stops before it bumps into the cat", lambda: __import__("lesson05_evaluate").safest_threshold(*__import__("lesson04_neuron").train_neuron(
        __import__("lesson04_neuron").make_obstacle_data(40, random.Random(0)), epochs=5), __import__("lesson04_neuron").make_obstacle_data(40, random.Random(0)))),
    ("route", "4", "06", "plans its own route ('goto blue', 'goto bin')", lambda: __import__("lesson06_paths").astar_path(ROOM, ROBOT_START, find_bin(ROOM))),
    ("typos", "5", "08", "fixes typos in what you type", lambda: __import__("lesson08_words").fix_typos("teh", {"the": {"red": 1}})),
    ("words", "5", "09", "understands sentences, one action at a time", lambda: __import__("lesson09_commands").train_intent_model([("stop", "stop")])),
    ("plans", "6", "15", "writes whole plans ('put the red and blue blocks away') and asks when you're vague", _plans),
    ("safety", "7", "10", "checks every action before moving", lambda: __import__("lesson10_llm_safety").validate_action({"intent": "stop", "object": None}, set())),
    ("whole", "7", "11", "is a whole robot YOU assembled (your RoboHelper), tested end to end", lambda: __import__("lesson11_robohelper").RoboHelper().run_command("stop")),
    ("speed", "8", "16", "times how long it thinks, and how far it rolls meanwhile", lambda: __import__("lesson16_speed").time_it(lambda: None, 2)),
    ("teacher", "9", "17", "learns new phrasings from a teacher (a smarter language brain)",
     lambda: __import__("lesson17_faster").distill_examples(["stop"], lambda c: "stop")),
    ("claude", "10", "18", "can ask Claude: type 'claude: tidy up the room' (needs an API key)", _key),
    ("exam", "11", "19", "sits the 12-task exam: type 'exam'", _exam),
    ("taste", "12", "12", "picks the routes people like (fewer turns, away from walls)",
     lambda: __import__("lesson12_preferences").reward([0, 0, 0], (1, 1, 1))),
]
NAMES = {k: (wk, lesson, what) for k, wk, lesson, what, _ in ABILITIES}


class MyRobot:
    def __init__(self, has, animate=True, quiet=False):
        self.has, self.animate, self.quiet = has, animate, quiet
        self.pos, self.objects, self.binned = ROBOT_START, dict(OBJECTS), set()
        self.blocked = set()
        if "stop" in has:
            from lesson04_neuron import make_obstacle_data, train_neuron
            from lesson05_evaluate import safest_threshold
            data = make_obstacle_data(450, random.Random(0))
            self.stop_w, self.stop_b = train_neuron(data)
            self.stop_t = safest_threshold(self.stop_w, self.stop_b, data)
        if "brake" in has:
            from lesson03_learning import fit_line, STOP_DATA
            self.bw, self.bb, _ = fit_line(STOP_DATA)
        if "words" in has:
            from lesson09_commands import TRAIN, train_intent_model
            if "intent" not in CACHE:
                CACHE["intent"] = train_intent_model(TRAIN)
            self.intent_model = CACHE["intent"]

    def say(self, msg):
        if not self.quiet:
            print("  " + msg)

    # ---------------- drawing ----------------
    def show(self, path=(), final=False):
        if not self.animate and not final:
            return
        visible = {k: v for k, v in self.objects.items() if k not in self.binned}
        art = render(ROOM, self.pos, {**visible, "cat": CAT}, list(path))
        if self.animate:
            print("\033[2J\033[H", end="")
        print(art)
        if self.animate:
            time.sleep(0.12)

    # ---------------- moving, one square at a time ----------------
    def step_to(self, nxt):
        """Move one square. The cat is not on the map: only a robot that can sense and stop (weeks 2-3) avoids it."""
        if nxt == CAT:
            if "stop" in self.has and "sense" in self.has:
                from lesson04_neuron import should_stop
                speed = self.safe_speed()
                if should_stop(self.stop_w, self.stop_b, (0.5, speed), self.stop_t):
                    self.blocked.add(nxt)
                    return "stopped"
            return "bump"
        self.pos = nxt
        return "moved"

    def safe_speed(self):
        if "brake" not in self.has:
            return 1.0
        from lesson03_learning import max_safe_speed
        from lesson02_sensors import distance_to_wall
        free = min(distance_to_wall(ROOM, self.pos, d) for d in "NSEW") * 0.5 + 0.5
        return max_safe_speed(self.bw, self.bb, free)

    def arrows(self, text):
        from lesson01_moving import move, safe_move
        path = [self.pos]
        for d in text.upper():
            nxt = move(self.pos, d)
            if safe_move(ROOM, self.pos, d) == self.pos:
                return path, f"Bonk! A wall to the {ARROWS[d].split()[0]}."
            result = self.step_to(nxt)
            if result == "bump":
                return path, "BUMP! I walked into the cat. (I can't sense things that aren't on the map yet: weeks 2-3.)"
            if result == "stopped":
                return path, f"Something is in the way at {nxt}! I stopped just in time."
            path.append(self.pos)
            self.show(path)
        return path, f"I'm at {self.pos}."

    def route(self, target):
        from lesson06_paths import astar_path
        if "taste" in self.has and not self.blocked:
            from lesson12_preferences import candidate_routes, best_route
            routes = candidate_routes(ROOM, self.pos, target)
            if routes:
                return best_route(self.taste_weights(), ROOM, routes)
        path, _ = astar_path(ROOM, self.pos, target, blocked=self.blocked)
        return path

    def taste_weights(self):
        if not hasattr(self, "_taste"):
            from lesson12_preferences import candidate_routes, collect_comparisons, train_reward_model
            routes = candidate_routes(ROOM, ROBOT_START, find_bin(ROOM))
            self._taste = train_reward_model(collect_comparisons(ROOM, routes, 150, random.Random(0)))
        return self._taste

    def drive_to(self, target):
        """Plan, drive, and replan if the cat is in the way. Returns (arrived, message)."""
        trail = [self.pos]
        for _ in range(6):
            path = self.route(target)
            if path is None:
                return False, f"I can't find a way to {target}."
            for nxt in path[1:]:
                result = self.step_to(nxt)
                if result == "bump":
                    self.show(trail)
                    return False, "BUMP! I walked into the cat. (Teach me to sense and stop: weeks 2-3.)"
                if result == "stopped":
                    self.say(f"Something is in the way at {nxt}! Stopping and planning a new route.")
                    break
                trail.append(self.pos)
                self.show(trail)
            else:
                return True, ""
        return False, "Too many surprises, giving up."

    # ---------------- understanding ----------------
    def understand(self, text):
        """Returns a list of actions, or a string reply (a question or a refusal)."""
        if "typos" in self.has:
            text = self.fix(text)
        plan = self.think(text)
        if "speed" in self.has:
            from lesson16_speed import time_it, summarize, thinking_distance
            s = summarize(time_it(lambda: self.think(text), 5))
            self.say(f"(I thought for {s['p50'] * 1000:.2f} ms, so at 1 m/s I'd roll {thinking_distance(s['p50']) * 1000:.2f} mm meanwhile)")
        return plan

    def think(self, text):
        if "plans" in self.has:
            from lesson15_tiny_lm import words_to_plan
            words = self.language_brain().generate(text)
            plan = words_to_plan(words)
            if plan is None:
                return f"Sorry, my answer made no sense ({' '.join(words) or 'nothing'})."
            if plan == "ask":
                return "Which block do you mean: red, blue or green?"
            if plan == "none":
                return "Sorry, that's not something I can do."
            return plan
        from lesson09_commands import parse_command
        return [parse_command(self.intent_model, text)]

    def fix(self, text):
        from lesson08_words import tokenize, count_bigrams, fix_typos
        if "counts" not in CACHE:
            from lesson09_commands import TRAIN
            corpus = [t for t, _ in TRAIN] + ["put the red and blue blocks away", "put all the blocks in the bin"]   # the room's own words
            if "plans" in self.has:
                from lesson15_tiny_lm import training_data
                corpus += [t for t, _ in training_data()]
            CACHE["counts"] = count_bigrams(tokenize(" . ".join(corpus)))
        fixed = fix_typos(text, CACHE["counts"])
        if fixed != " ".join(tokenize(text)):
            self.say(f"(I think you meant: {fixed!r})")
        return fixed

    def language_brain(self):
        if "brain" not in CACHE:
            print("  (Teaching my language brain. This takes about 10-20 seconds, once...)")
            if "teacher" in self.has:
                from lesson17_faster import distill_examples, UNLABELLED, best_teacher, best_student
                CACHE["brain"] = best_student(distill_examples(UNLABELLED, best_teacher()))
            else:
                from lesson15_tiny_lm import train_tiny_lm
                CACHE["brain"] = train_tiny_lm()[0]
        return CACHE["brain"]

    # ---------------- doing ----------------
    def do(self, action):
        if "safety" in self.has:
            from lesson10_llm_safety import validate_action
            ok, reason = validate_action(action, set(self.objects))
            if not ok:
                return f"Sorry, I won't do that: {reason}."
        elif not action or action.get("intent") not in ("put", "go", "find", "stop") or (
                action.get("intent") != "stop" and action.get("object") not in self.objects):
            return f"Uh oh, I don't know what to do with {action}. (No safety checks yet: week 7 adds them.)"
        intent, obj = action["intent"], action["object"]
        if intent == "stop":
            return "Stopping."
        if intent == "find":
            return f"The {obj} is in the bin." if obj in self.binned else f"The {obj} is at {self.objects[obj]}."
        if "route" not in self.has:
            return "I understand you, but I can't plan routes yet (week 4). Try arrows like EESS."
        if obj in self.binned:
            return f"The {obj} is already in the bin."
        ok, msg = self.drive_to(self.objects[obj])
        if not ok or intent == "go":
            return msg or f"I'm next to the {obj}."
        ok, msg = self.drive_to(find_bin(ROOM))
        if not ok:
            return msg
        self.binned.add(obj)
        self.objects[obj] = find_bin(ROOM)
        return f"The {obj} is in the bin."

    def command(self, text):
        t = text.strip()
        low = t.lower()
        if not t:
            return ""
        if set(t.upper()) <= set("NSEW"):
            return self.arrows(t)[1]
        if low == "look":
            if "sense" not in self.has:
                return "I can't sense anything yet (week 2)."
            from lesson02_sensors import distance_to_wall
            dists = ", ".join(f"{ARROWS[d].split()[0]} {distance_to_wall(ROOM, self.pos, d)}" for d in "NESW")
            speed = f" Safe speed here: {self.safe_speed()} m/s." if "brake" in self.has else ""
            return f"Squares to the nearest wall: {dists}.{speed}"
        if low.startswith("goto "):
            if "route" not in self.has:
                return "I can't plan routes yet (week 4). Try arrows like EESS."
            name = low[5:].strip()
            target = find_bin(ROOM) if name == "bin" else self.objects.get(f"{name} block")
            if target is None:
                return "Try: goto red, goto blue, goto green or goto bin."
            ok, msg = self.drive_to(target)
            return msg or f"I'm at {self.pos}."
        if low == "exam":
            return self.exam()
        if low.startswith("claude:"):
            return self.ask_claude(t[7:].strip()) if "claude" in self.has else "I can't ask Claude yet (week 10, and it needs an API key)."
        if low == "reset":
            self.__init__(self.has, self.animate)
            return "Back to the start."
        if "words" not in self.has:
            return "I don't understand sentences yet (week 5). Try arrows like EESS" + (", look" if "sense" in self.has else "") + (", or goto blue." if "route" in self.has else ".")
        plan = self.understand(t)
        if isinstance(plan, str):
            return plan
        replies = []
        for action in plan:
            replies.append(self.do(action))
            if replies[-1].startswith(("Sorry", "BUMP", "I can't", "Uh oh", "Too many")):
                break
        return " ".join(r for r in replies if r)


    def exam(self):
        if "exam" not in self.has:
            return "I can't sit the exam yet (week 11)."
        from lesson19_bakeoff import TASKS, score_task
        passed = 0
        for task in TASKS:
            r = MyRobot(self.has, animate=False, quiet=True)
            reply = r.command(task["command"])
            ok, why = score_task(task, r, {"reply": reply})
            passed += ok
            print(f"  {'✓' if ok else '✗'} {task['command']!r:46} {'' if ok else why}")
        return f"I passed {passed} of {len(TASKS)}."

    def ask_claude(self, text):
        import anthropic
        from sim import SimRobot
        from lesson18_world_class import ask_planner, validate_plan
        snapshot = SimRobot(objects=self.objects, start=self.pos)
        snapshot.binned = set(self.binned)
        plan_obj, info = ask_planner(anthropic.Anthropic(), snapshot, text)
        ok, reason = validate_plan(plan_obj, set(self.objects))
        print(f"  (Claude thought for {info['seconds']:.1f} s, {info['tokens_in']} tokens in, {info['tokens_out']} out)")
        if not ok:
            return f"I won't run Claude's plan: {reason}."
        if plan_obj["clarify"]:
            return plan_obj["clarify"]
        replies = [plan_obj["reply"]] + [self.do(a) for a in plan_obj["plan"]]
        return " ".join(r for r in replies if r)


def abilities():
    return [k for k, *_, test in ABILITIES if works(test)]


def banner(has, name):
    week = max([int(NAMES[k][0]) for k in has] or [0])
    print(f"\n=== {name}, your robot (built up to week {week}) ===")
    for k, wk, lesson, what, _ in ABILITIES:
        extra = ""
        if k == "whole" and k in has:
            from lesson11_robohelper import evaluate
            extra = f": it passes {evaluate()[0]:.0%} of its final test"
        print(f"  {'✓' if k in has else '·'} week {wk:>2} (lesson {lesson:>5}): {what}{extra}")
    missing = [k for k, *_ in ABILITIES if k not in has]
    if missing:
        wk, lesson, what = NAMES[missing[0]]
        print(f"  Next: week {wk}, lesson {lesson}. Then your robot {what}.")
    if not SOLUTIONS and SAVE.exists():
        before = set(json.loads(SAVE.read_text()).get("abilities", []))
        new = [k for k in has if k not in before]
        if new:
            print("  NEW since last time: " + "; ".join(NAMES[k][2] for k in new) + "!")


def help_text(has):
    lines = ["Try:"]
    if "move" in has:
        lines.append("  EESS             move with arrows (N S E W)")
    if "sense" in has:
        lines.append("  look             what the sensors see")
    if "route" in has:
        lines.append("  goto blue        plan a route (also: goto red, goto green, goto bin)")
    if "words" in has:
        lines.append("  put the red block in the bin")
    if "plans" in has:
        lines.append("  put the red and blue blocks away     /    put the block away")
    if "safety" in has:
        lines.append("  put the purple block in the bin   (a safe robot refuses)")
    if "exam" in has:
        lines.append("  exam             sit the 12-task exam")
    if "claude" in has:
        lines.append("  claude: tidy up the room      ask Claude to plan it")
    lines.append("  reset            start again       quit   stop")
    return "\n".join(lines)


def showcase(has, name):
    """The capstone show: a demo of every ability, then YOUR exam from my_tasks.txt."""
    print(f"\n*** {name}: THE SHOWCASE ***")
    demo = [("move", "EEE"), ("sense", "look"), ("route", "goto blue"), ("words", "put the green block in the bin"),
            ("typos", "put teh red blok in the bin"), ("plans", "put the red and blue blocks away"),
            ("plans", "put the block away"), ("safety", "put the purple block in the bin")]
    for key, cmd in demo:
        if key in has:
            r = MyRobot(has, animate=False)
            print(f"\n> {cmd}   [{NAMES[key][2]}]")
            reply = r.command(cmd)
            r.show(final=True)
            print("  " + reply)
    if "exam" in has:
        print("\n> exam   [the 12 tasks from the bake-off]")
        print("  " + MyRobot(has, animate=False).exam())
    if not TASKS.exists():
        print(f"\nWrite your own exam: copy my_tasks_example.txt to {TASKS.name}, change it, and run --show again.")
        return
    print(f"\nYOUR EXAM ({TASKS.name}):")
    passed = total = 0
    for line in TASKS.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cmd, want = [p.strip() for p in line.split("|")]
        r = MyRobot(has, animate=False, quiet=True)
        reply = r.command(cmd)
        got = ", ".join(sorted(r.binned)) or "nothing"
        want_set = "nothing" if want in ("", "nothing") else ", ".join(sorted(w.strip() for w in want.split(",")))
        ok = got == want_set
        passed, total = passed + ok, total + 1
        print(f"  {'✓' if ok else '✗'} {cmd!r:40} binned: {got:30} wanted: {want_set}")
    print(f"\n{name} passed {passed} of {total} of your tests.")


if __name__ == "__main__":
    has = abilities()
    saved = json.loads(SAVE.read_text()) if SAVE.exists() and not SOLUTIONS else {}
    name = "Robo-Helper" if SOLUTIONS else saved.get("name")
    if not name:
        name = input("Your robot needs a name. What's it called? ").strip() or "Robo-Helper"
    banner(has, name)
    if not SOLUTIONS:
        SAVE.write_text(json.dumps({"name": name, "abilities": has}))
    if "--show" in sys.argv:
        showcase(has, name)
        sys.exit()
    if "move" not in has:
        print("\nYour robot can't do anything yet. Finish Lesson 1 (moving) and come back!")
        sys.exit()
    robot = MyRobot(has, animate=sys.stdin.isatty())
    robot.show(final=True)
    print(help_text(has))
    while True:
        try:
            text = input(f"\n{name}> ")
        except EOFError:
            break
        if text.strip().lower() in ("quit", "exit", "q"):
            break
        if text.strip().lower() == "help":
            print(help_text(has))
            continue
        reply = robot.command(text)
        if not robot.animate:
            robot.show(final=True)
        print(f"  {reply}")
