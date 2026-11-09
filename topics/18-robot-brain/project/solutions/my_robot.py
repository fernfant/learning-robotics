"""MY ROBOT. You build this file yourself, one piece a week.

Every lesson ends with "Add it to your robot": a small gap in this file, marked with the week, that you fill in
by connecting what you just built (your lesson file) to your robot. Until you fill a gap, your robot says
"I can't do that yet". When you fill it, your robot can.

    cd homework
    python3 my_robot.py            talk to your robot ('help' shows what it can do, 'quit' stops)
    python3 my_robot.py --show     week 12: the showcase (a demo, the 12-task exam, then YOUR tests in my_tasks.txt)
    cd .. ; python3 check.py robot checks every piece you've added so far

The parts marked PROVIDED (drawing the room, the typing loop, the showcase) are done for you.
Everything that makes the robot clever is yours.
"""

import inspect
import random
import sys
import time
from pathlib import Path

from world import ROOM, OBJECTS, ROBOT_START, find_bin, render

NAME = "Robo-Helper"         # WEEK 1: give your robot its own name!
CAT = (4, 1)                 # the cat. It is NOT on the map, so your robot only finds out by sensing it.
CACHE = {}                   # brains you've trained, so the robot only trains them once per run


class Robot:
    def __init__(self, quiet=False, animate=False):
        self.pos = ROBOT_START
        self.objects = dict(OBJECTS)    # where each block is, e.g. {"red block": (2, 1), ...}
        self.binned = set()             # blocks already in the bin
        self.blocked = set()            # squares where the robot found something in the way
        self.last_path = []
        self.quiet, self.animate = quiet, animate

    # ======================= WEEK 1 (Lesson 1): moving =======================
    def arrows(self, text):
        """Move one square for each letter in text ("EESN": east, east, south, north), using your
        Lesson 1 move() and safe_move(). For every letter:
          - if safe_move would leave the robot where it is, there's a wall: return "Bonk! A wall."
          - otherwise call self.step(the new square). If it returns "bump" or "stopped", return
            self.step_message(that result, the square) straight away.
        After the last letter, return f"I'm at {self.pos}."
        """
        # BEGIN ROBOT week=1 lessons=1
        from lesson01_moving import move, safe_move
        for d in text.upper():
            if safe_move(ROOM, self.pos, d) == self.pos:
                return "Bonk! A wall."
            result = self.step(move(self.pos, d))
            if result != "moved":
                return self.step_message(result, move(self.pos, d))
        return f"I'm at {self.pos}."
        # END ROBOT

    # ======================= WEEK 2 (Lessons 2-3): sensing =======================
    def look(self):
        """Return what the sensors see, like "Walls: north 0, east 7, south 5, west 0. Safe speed: 0.25 m/s."
        Use your Lesson 2 distance_to_wall() for "N", "E", "S", "W" (in that order, written north/east/south/west).
        For the safe speed (Lesson 3): fit_line(STOP_DATA) gives w, b; the free distance in metres is
        (the smallest of the four distances) * 0.5 + 0.5; then max_safe_speed(w, b, free)."""
        # BEGIN ROBOT week=2 lessons=2-3
        from lesson02_sensors import distance_to_wall
        from lesson03_learning import STOP_DATA, fit_line, max_safe_speed
        d = {k: distance_to_wall(ROOM, self.pos, k) for k in "NESW"}
        w, b, _ = fit_line(STOP_DATA)
        speed = max_safe_speed(w, b, min(d.values()) * 0.5 + 0.5)
        return f"Walls: north {d['N']}, east {d['E']}, south {d['S']}, west {d['W']}. Safe speed: {speed} m/s."
        # END ROBOT

    # ======================= WEEK 3 (Lessons 4-5): stopping in time =======================
    def should_stop_for(self, square):
        """Something is one square ahead (0.5 m away) and the robot is driving at 0.5 m/s. Should it stop?
        Train your Lesson 4 neuron on make_obstacle_data(450, random.Random(0)), pick the threshold with your
        Lesson 5 safest_threshold(), then return should_stop(weights, bias, (0.5, 0.5), threshold).
        Tip: train once and keep it in CACHE["stop"] so it isn't retrained on every step."""
        # BEGIN ROBOT week=3 lessons=4-5
        from lesson04_neuron import make_obstacle_data, train_neuron, should_stop
        from lesson05_evaluate import safest_threshold
        if "stop" not in CACHE:
            data = make_obstacle_data(450, random.Random(0))
            w, b = train_neuron(data)
            CACHE["stop"] = (w, b, safest_threshold(w, b, data))
        w, b, t = CACHE["stop"]
        return should_stop(w, b, (0.5, 0.5), t)
        # END ROBOT

    # ======================= WEEK 4 (Lesson 6): finding the way =======================
    def route(self, target):
        """The shortest path from self.pos to target, avoiding self.blocked: your Lesson 6 astar_path().
        Return just the path (a list of squares), or None if there isn't one."""
        # BEGIN ROBOT week=4 lessons=6
        from lesson06_paths import astar_path
        path, _ = astar_path(ROOM, self.pos, target, blocked=self.blocked)
        return path
        # END ROBOT

    def goto(self, target):
        """Drive to target. Returns "" if it arrived, or a message saying why not.
          Repeat up to 6 times:
            path = self.plan_route(target)            (PROVIDED below: your route(), or a nicer one in week 12)
            if path is None: return "I can't find a way there."
            for each square after the first: result = self.step(square)
                "bump"    -> return self.step_message("bump", square)
                "stopped" -> self.say(self.step_message("stopped", square)) and plan again (break)
            if every step worked: return ""
          After 6 tries: return "Too many surprises, giving up." """
        # BEGIN ROBOT week=4 lessons=6
        for _ in range(6):
            path = self.plan_route(target)
            if path is None:
                return "I can't find a way there."
            for square in path[1:]:
                result = self.step(square)
                if result == "bump":
                    return self.step_message("bump", square)
                if result == "stopped":
                    self.say(self.step_message("stopped", square) + " Planning a new route.")
                    break
            else:
                return ""
        return "Too many surprises, giving up."
        # END ROBOT

    # ======================= WEEK 5 (Lessons 8-9): understanding words =======================
    def clean(self, text):
        """Fix typos with your Lesson 8 fix_typos(). The word counts come from the words your robot knows:
        count_bigrams(tokenize(" . ".join(the commands in Lesson 9's TRAIN))). Keep them in CACHE["counts"]."""
        # BEGIN ROBOT week=5 lessons=8
        from lesson08_words import tokenize, count_bigrams, fix_typos
        from lesson09_commands import TRAIN
        if "counts" not in CACHE:
            words = [t for t, _ in TRAIN] + ["put the red and blue blocks away", "put all the blocks in the bin"]
            CACHE["counts"] = count_bigrams(tokenize(" . ".join(words)))
        return fix_typos(text, CACHE["counts"])
        # END ROBOT

    def understand_words(self, text):
        """One sentence -> a list with ONE action, using your Lesson 9 parse_command().
        Train the word counter once: CACHE["words"] = train_intent_model(TRAIN)."""
        # BEGIN ROBOT week=5 lessons=9
        from lesson09_commands import TRAIN, train_intent_model, parse_command
        if "words" not in CACHE:
            CACHE["words"] = train_intent_model(TRAIN)
        return [parse_command(CACHE["words"], text)]
        # END ROBOT

    def do(self, action):
        """Carry out one action, like {"intent": "put", "object": "red block"}. Return what the robot says.
          stop -> "Stopping."
          find -> "The red block is in the bin." if it's in self.binned, else f"The red block is at {position}."
          go   -> msg = self.goto(position of the object); return msg or "I'm next to the red block."
          put  -> if already binned: "The red block is already in the bin."
                  goto the object, then goto find_bin(ROOM) (stop early with the message if a goto fails),
                  then add it to self.binned, set self.objects[it] to the bin's position,
                  and return "The red block is in the bin." """
        # BEGIN ROBOT week=5 lessons=9
        intent, obj = action["intent"], action["object"]
        if intent == "stop":
            return "Stopping."
        if intent == "find":
            return f"The {obj} is in the bin." if obj in self.binned else f"The {obj} is at {self.objects[obj]}."
        if intent == "go":
            return self.goto(self.objects[obj]) or f"I'm next to the {obj}."
        if obj in self.binned:
            return f"The {obj} is already in the bin."
        msg = self.goto(self.objects[obj]) or self.goto(find_bin(ROOM))
        if msg:
            return msg
        self.binned.add(obj)
        self.objects[obj] = find_bin(ROOM)
        return f"The {obj} is in the bin."
        # END ROBOT

    # ======================= WEEK 6 (Lesson 15): writing whole plans =======================
    def understand_plans(self, text):
        """Use your Lesson 15 language model to write a plan: words = self.brain().generate(text), then
        plan = words_to_plan(words).
          None   -> return "Sorry, my answer made no sense."
          "ask"  -> return "Which block do you mean: red, blue or green?"
          "none" -> return "Sorry, that's not something I can do."
          otherwise return the plan (a list of actions)."""
        # BEGIN ROBOT week=6 lessons=15
        from lesson15_tiny_lm import words_to_plan
        plan = words_to_plan(self.brain().generate(text))
        if plan is None:
            return "Sorry, my answer made no sense."
        if plan == "ask":
            return "Which block do you mean: red, blue or green?"
        if plan == "none":
            return "Sorry, that's not something I can do."
        return plan
        # END ROBOT

    # ======================= WEEK 7 (Lesson 10): safety =======================
    def is_safe(self, action):
        """Your Lesson 10 validate_action(action, set(self.objects)). Return its (ok, reason)."""
        # BEGIN ROBOT week=7 lessons=10
        from lesson10_llm_safety import validate_action
        return validate_action(action, set(self.objects))
        # END ROBOT

    # ======================= WEEK 8 (Lesson 16): how fast does it think? =======================
    def think_time(self, text):
        """How long does understanding text take? Time self.understand(text) 5 times with your Lesson 16 time_it(),
        then summarize(). Return f"(I thought for {p50 in ms:.2f} ms, so I'd roll {distance in mm:.2f} mm meanwhile.)"
        using thinking_distance(p50 seconds), which gives metres."""
        # BEGIN ROBOT week=8 lessons=16
        from lesson16_speed import time_it, summarize, thinking_distance
        p50 = summarize(time_it(lambda: self.understand(text), 5))["p50"]
        return f"(I thought for {p50 * 1000:.2f} ms, so I'd roll {thinking_distance(p50) * 1000:.2f} mm meanwhile.)"
        # END ROBOT

    # ======================= WEEK 9 (Lesson 17): learning from a teacher =======================
    def teacher_brain(self):
        """A smarter language brain: re-train on a teacher's labels with your Lesson 17 code:
        best_student(distill_examples(UNLABELLED, best_teacher()))."""
        # BEGIN ROBOT week=9 lessons=17
        from lesson17_faster import distill_examples, UNLABELLED, best_teacher, best_student
        return best_student(distill_examples(UNLABELLED, best_teacher()))
        # END ROBOT

    # ======================= WEEK 10 (Lesson 18): a world-class brain (needs an API key) =======================
    def ask_claude(self, text):
        """Ask Claude for a plan with your Lesson 18 ask_planner(), check it with validate_plan(), then do it.
          client = anthropic.Anthropic(); room = SimRobot(objects=self.objects, start=self.pos)
          plan_obj, info = ask_planner(client, room, text)
          not valid -> "I won't run Claude's plan: <reason>."    clarify -> return the question
          otherwise return Claude's reply plus self.do(a) for each action in plan_obj["plan"]."""
        # BEGIN ROBOT week=10 lessons=18
        import anthropic
        from sim import SimRobot
        from lesson18_world_class import ask_planner, validate_plan
        room = SimRobot(objects=self.objects, start=self.pos)
        plan_obj, info = ask_planner(anthropic.Anthropic(), room, text)
        ok, reason = validate_plan(plan_obj, set(self.objects))
        if not ok:
            return f"I won't run Claude's plan: {reason}."
        if plan_obj["clarify"]:
            return plan_obj["clarify"]
        return " ".join([plan_obj["reply"]] + [self.do(a) for a in plan_obj["plan"]])
        # END ROBOT

    # ======================= WEEK 11 (Lesson 19): the exam =======================
    def exam(self):
        """Sit the 12 bake-off tasks. For each task in Lesson 19's TASKS: make a FRESH Robot(quiet=True),
        reply = robot.command(task["command"]), then your score_task(task, robot, {"reply": reply}).
        Print a ✓ or ✗ line per task (unless self.quiet), and return f"I passed {passed} of {len(TASKS)}." """
        # BEGIN ROBOT week=11 lessons=19
        from lesson19_bakeoff import TASKS, score_task
        passed = 0
        for task in TASKS:
            robot = Robot(quiet=True)
            ok, why = score_task(task, robot, {"reply": robot.command(task["command"])})
            passed += ok
            if not self.quiet:
                print(f"  {'✓' if ok else '✗'} {task['command']!r:46} {'' if ok else why}")
        return f"I passed {passed} of {len(TASKS)}."
        # END ROBOT

    # ======================= WEEK 12 (Lesson 12): the routes people like =======================
    def nicest_route(self, target):
        """Pick the route people like best (Lesson 12): routes = candidate_routes(ROOM, self.pos, target);
        learn the taste once (CACHE["taste"] = train_reward_model(collect_comparisons(ROOM, routes from
        ROBOT_START to the bin, 150, random.Random(0)))), then return best_route(taste, ROOM, routes).
        If there are no candidate routes, return self.route(target)."""
        # BEGIN ROBOT week=12 lessons=12
        from lesson12_preferences import candidate_routes, collect_comparisons, train_reward_model, best_route
        if "taste" not in CACHE:
            start_routes = candidate_routes(ROOM, ROBOT_START, find_bin(ROOM))
            CACHE["taste"] = train_reward_model(collect_comparisons(ROOM, start_routes, 150, random.Random(0)))
        routes = candidate_routes(ROOM, self.pos, target)
        return best_route(CACHE["taste"], ROOM, routes) if routes else self.route(target)
        # END ROBOT

    # ======================= PROVIDED: the glue that joins your pieces =======================
    def step(self, square):
        """Move one square. Returns "moved", "stopped" (it saw the cat in time) or "bump"."""
        if square == CAT:
            if built(self.should_stop_for) and self.should_stop_for(square):
                self.blocked.add(square)
                return "stopped"
            return "bump"
        self.pos = square
        self.last_path.append(square)
        self.draw()
        return "moved"

    def step_message(self, result, square):
        if result == "bump":
            return "BUMP! I walked into the cat. (I can't sense things that aren't on the map: add week 3.)"
        return f"Something is in the way at {square}! I stopped just in time."

    def plan_route(self, target):
        if built(self.nicest_route) and not self.blocked:
            return self.nicest_route(target)
        return self.route(target)

    def brain(self):
        if "brain" not in CACHE:
            if not self.quiet:
                print("  (Training my language brain. About 10-20 seconds, once...)")
            if built(self.teacher_brain):
                CACHE["brain"] = self.teacher_brain()
            else:
                from lesson15_tiny_lm import train_tiny_lm
                CACHE["brain"] = train_tiny_lm()[0]
        return CACHE["brain"]

    def understand(self, text):
        if built(self.understand_plans):
            return self.understand_plans(text)
        return self.understand_words(text)

    def say(self, msg):
        if not self.quiet:
            print("  " + msg)

    def draw(self, final=False):
        if not (self.animate or final) or self.quiet:
            return
        if self.animate:
            print("\033[2J\033[H", end="")
        visible = {k: v for k, v in self.objects.items() if k not in self.binned}
        print(render(ROOM, self.pos, {**visible, "cat": CAT}, self.last_path))
        if self.animate:
            time.sleep(0.12)

    def command(self, text):
        """Everything you type goes through here."""
        t, low = text.strip(), text.strip().lower()
        self.last_path = [self.pos]
        try:
            if t and set(t.upper()) <= set("NSEW"):
                return self.arrows(t)
            if low == "look":
                return self.look()
            if low.startswith("goto "):
                name = low[5:].strip()
                target = find_bin(ROOM) if name == "bin" else self.objects.get(f"{name} block")
                return "Try goto red, goto blue, goto green or goto bin." if target is None else self.goto(target) or f"I'm at {self.pos}."
            if low == "exam":
                return self.exam()
            if low.startswith("claude:"):
                if not built(self.ask_claude):
                    return self.ask_claude(t)
                try:
                    return self.ask_claude(t[7:].strip())
                except Exception as e:
                    return f"Claude isn't reachable ({type(e).__name__}). It needs `pip install anthropic` and an API key: ask an adult."
            if built(self.clean):
                fixed = self.clean(t)
                if fixed != t.lower().strip(" ?!."):
                    self.say(f"(I think you meant: {fixed!r})")
                t = fixed
            plan = self.understand(t)
            if built(self.think_time):
                self.say(self.think_time(t))
            if isinstance(plan, str):
                return plan
            replies = []
            for action in plan:
                if built(self.is_safe):
                    ok, reason = self.is_safe(action)
                    if not ok:
                        replies.append(f"Sorry, I won't do that: {reason}.")
                        break
                elif not action or action.get("intent") not in ("put", "go", "find", "stop") or (
                        action.get("intent") != "stop" and action.get("object") not in self.objects):
                    replies.append(f"Uh oh, I don't know what to do with {action}. (No safety check yet: add week 7.)")
                    break
                replies.append(self.do(action))
            return " ".join(r for r in replies if r)
        except NotImplementedError as e:
            return f"I can't do that yet: {e}"


# ======================= PROVIDED: what's built, the typing loop, the showcase =======================
PIECES = [("arrows", 1, "1", "moves with arrows (EESS)"), ("look", 2, "2-3", "looks around: 'look'"),
          ("should_stop_for", 3, "4-5", "stops before it bumps into the cat"), ("goto", 4, "6", "plans routes: 'goto blue'"),
          ("clean", 5, "8", "fixes typos"), ("do", 5, "9", "understands sentences, one action at a time"),
          ("understand_plans", 6, "15", "writes whole plans and asks when you're vague"), ("is_safe", 7, "10", "checks every action first"),
          ("think_time", 8, "16", "knows how long it thinks"), ("teacher_brain", 9, "17", "has a teacher-trained brain"),
          ("ask_claude", 10, "18", "can ask Claude: 'claude: tidy up the room' (needs a key)"), ("exam", 11, "19", "sits the exam: 'exam'"),
          ("nicest_route", 12, "12", "picks the routes people like")]


def built(method):
    """A piece is built once its TODO is gone (it no longer just says NotImplementedError)."""
    return "raise NotImplementedError" not in inspect.getsource(method)


def banner(robot):
    done = [p for p in PIECES if built(getattr(robot, p[0]))]
    print(f"\n=== {NAME}: built up to week {max([p[1] for p in done] or [0])} ===")
    for name, week, lessons, what in PIECES:
        print(f"  {'✓' if built(getattr(robot, name)) else '·'} week {week:>2} (lesson {lessons:>4}): {what}")
    todo = [p for p in PIECES if not built(getattr(robot, p[0]))]
    if todo:
        print(f"  Next gap to fill: week {todo[0][1]}, the {todo[0][0]}() method in my_robot.py.")
    try:
        from lesson11_robohelper import evaluate
        print(f"  Your capstone RoboHelper (Lesson 11) passes {evaluate()[0]:.0%} of its final test.")
    except NotImplementedError:
        pass


def showcase():
    print(f"\n*** {NAME}: THE SHOWCASE ***")
    for cmd in ["EEE", "look", "goto blue", "put teh green blok in the bin", "put the red and blue blocks away",
                "put the block away", "put the purple block in the bin", "exam"]:
        r = Robot()
        print(f"\n> {cmd}")
        reply = r.command(cmd)
        r.draw(final=True)
        print("  " + reply)
    tasks = Path(__file__).resolve().parent / "my_tasks.txt"
    if not tasks.exists():
        print("\nWrite your own exam: copy my_tasks_example.txt to my_tasks.txt, change it, and run --show again.")
        return
    print("\nYOUR EXAM (my_tasks.txt):")
    passed = total = 0
    for line in tasks.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cmd, want = [p.strip() for p in line.split("|")]
        r = Robot(quiet=True)
        r.command(cmd)
        got = ", ".join(sorted(r.binned)) or "nothing"
        want = "nothing" if want in ("", "nothing") else ", ".join(sorted(w.strip() for w in want.split(",")))
        passed, total = passed + (got == want), total + 1
        print(f"  {'✓' if got == want else '✗'} {cmd!r:40} binned: {got:30} wanted: {want}")
    print(f"\n{NAME} passed {passed} of {total} of your tests.")


if __name__ == "__main__":
    if "--show" in sys.argv:
        showcase()
        sys.exit()
    robot = Robot(animate=sys.stdin.isatty())
    banner(robot)
    robot.draw(final=True)
    print("Type commands like EESS, look, goto blue, put the red block in the bin, exam.   help / reset / quit")
    while True:
        try:
            text = input(f"\n{NAME}> ")
        except EOFError:
            break
        low = text.strip().lower()
        if low in ("quit", "exit", "q"):
            break
        if low == "help":
            banner(robot)
            continue
        if low == "reset":
            robot = Robot(animate=robot.animate)
            robot.draw(final=True)
            continue
        reply = robot.command(text)
        robot.draw(final=not robot.animate)
        print(f"  {reply}")
