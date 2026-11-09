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
import json
import random
import traceback
import sys
import time
from pathlib import Path

from world import ROOM, OBJECTS, ROBOT_START, find_bin, render

NAME = "Robo-Helper"         # WEEK 1: give your robot its own name!
CAT = (4, 1)                 # the cat at (4, 1) is drawn for you, but it's NOT on the robot's map: the robot only finds out by sensing it.
CACHE = {}                   # brains you've trained, so the robot only trains them once per run


class Robot:
    def __init__(self, quiet=False, animate=False):
        self.pos = ROBOT_START
        self.objects = dict(OBJECTS)    # where each block is, e.g. {"red block": (2, 1), ...}
        self.binned = set()             # blocks already in the bin
        self.blocked = set()            # squares where the robot found something in the way
        self.last_path = []
        self.last_stop = None           # week 3: (stop chance, threshold) the last time it saw something
        self.slow = False               # week 8: 'slowbrain on' pretends the brain is very slow
        self.quiet, self.animate = quiet, animate

    # ======================= WEEK 1 (Lesson 1): moving =======================
    def arrows(self, text):
        """Move one square for each letter in text ("EESN": east, east, south, north), using your
        Lesson 1 move() and safe_move(). For every letter:
          - if safe_move would leave the robot where it is, there's a wall: return f"Bonk! A wall. I'm at {self.pos}."
          - otherwise call self.step(the new square). If it returns "bump" or "stopped", return
            self.step_message(that result, the square) straight away.
        After the last letter, return f"I'm at {self.pos}."
        """
        # TODO week 1: fill in this gap (see 'Add it to your robot' on the week 1 page). Read the docstring above.
        raise NotImplementedError("week 1. Fill in this gap in my_robot.py")

    # ======================= WEEK 2 (Lessons 2-3): sensing =======================
    def look(self):
        """What the sensors see. A real sensor is noisy, so average 16 readings (Lesson 2):
          for each direction "N", "E", "S", "W":  true = distance_to_wall(ROOM, self.pos, direction)
                                                    seen = smoothed_reading(true, 0.5, 16, random.Random())
          return f"Walls (average of 16 readings): north {N:.1f}, east {E:.1f}, south {S:.1f}, west {W:.1f}."
        Lesson 3 adds the safe speed to the end: w, b, _ = fit_line(STOP_DATA); one square is 0.5 m, so the free space
        in metres is (the smallest TRUE distance) * 0.5 + 0.5; then add f" Safe speed: {max_safe_speed(w, b, free)} m/s." """
        # TODO week 2: fill in this gap (see 'Add it to your robot' on the week 2 page). Read the docstring above.
        raise NotImplementedError("week 2. Fill in this gap in my_robot.py")

    # ======================= WEEK 3 (Lessons 4-5): stopping in time =======================
    def should_stop_for(self, square):
        """Something is one square ahead (0.5 m away) and the robot is driving at 0.5 m/s. Should it stop?
        Train your Lesson 4 neuron on make_obstacle_data(450, random.Random(0)), pick the threshold with your
        Lesson 5 safest_threshold(), then return should_stop(weights, bias, (0.5, 0.5), threshold).
        Also remember what it decided, so the robot can tell you: self.last_stop = (neuron(w, b, (0.5, 0.5)), threshold).
        Tip: train once and keep it in CACHE["stop"] so it isn't retrained on every step."""
        # TODO week 3: fill in this gap (see 'Add it to your robot' on the week 3 page). Read the docstring above.
        raise NotImplementedError("week 3. Fill in this gap in my_robot.py")

    # ======================= WEEK 4 (Lesson 6): finding the way =======================
    def route(self, target):
        """The shortest path from self.pos to target, avoiding self.blocked: your Lesson 6 astar_path().
        Return just the path (a list of squares), or None if there isn't one."""
        # TODO week 4: fill in this gap (see 'Add it to your robot' on the week 4 page). Read the docstring above.
        raise NotImplementedError("week 4. Fill in this gap in my_robot.py")

    def goto(self, target):
        """Drive to target. Returns "" if it arrived, or a message saying why not.
          Repeat up to 6 times:
            path = self.plan_route(target)            (PROVIDED below: your route(), or a nicer one in week 12)
            if path is None: return "I can't find a way there."
            for each square after the first: result = self.step(square)
                "bump" (or "late") -> return self.step_message(result, square)
                "stopped" -> self.say(self.step_message("stopped", square)) and plan again (break)
            if every step worked: return ""
          After 6 tries: return "Too many surprises, giving up." """
        # TODO week 4: fill in this gap (see 'Add it to your robot' on the week 4 page). Read the docstring above.
        raise NotImplementedError("week 4. Fill in this gap in my_robot.py")

    # ======================= WEEK 5 (Lessons 8-9): understanding words =======================
    def clean(self, text):
        """Fix typos with your Lesson 8 fix_typos(). The word counts come from the words your robot knows,
        the commands in Lesson 9's TRAIN (a list of (command, intent) pairs, so take just the command):
            words = [command for command, intent in TRAIN]
            CACHE["counts"] = count_bigrams(tokenize(" . ".join(words)))
        Then return fix_typos(text, CACHE["counts"])."""
        # TODO week 5: fill in this gap (see 'Add it to your robot' on the week 5 page). Read the docstring above.
        raise NotImplementedError("week 5. Fill in this gap in my_robot.py")

    def understand_words(self, text):
        """One sentence -> a list with ONE action, using your Lesson 9 parse_command().
        Train the word counter once: CACHE["words"] = train_intent_model(TRAIN)."""
        # TODO week 5: fill in this gap (see 'Add it to your robot' on the week 5 page). Read the docstring above.
        raise NotImplementedError("week 5. Fill in this gap in my_robot.py")

    def do(self, action):
        """Carry out one action, like {"intent": "put", "object": "red block"}. Return what the robot says.
          stop -> "Stopping."
          find -> "The red block is in the bin." if it's in self.binned, else f"The red block is at {position}."
          go   -> msg = self.goto(position of the object); return msg or "I'm next to the red block."
          put  -> if already binned: "The red block is already in the bin."
                  goto the object, then goto find_bin(ROOM) (stop early with the message if a goto fails),
                  then add it to self.binned, set self.objects[it] to the bin's position,
                  and return "The red block is in the bin."
          anything else -> raise ValueError(f"I don't know how to {intent!r}") """
        # TODO week 5: fill in this gap (see 'Add it to your robot' on the week 5 page). Read the docstring above.
        raise NotImplementedError("week 5. Fill in this gap in my_robot.py")

    # ======================= WEEK 6 (Lesson 15): writing whole plans =======================
    def understand_plans(self, text):
        """Use your Lesson 15 language model to write a plan: words = self.brain().generate(text), then
        plan = words_to_plan(words).
          None   -> return "Sorry, my answer made no sense."
          "ask"  -> return "Which block do you mean: red, blue or green?"
          "none" -> return "Sorry, that's not something I can do."
          otherwise return the plan (a list of actions)."""
        # TODO week 6: fill in this gap (see 'Add it to your robot' on the week 6 page). Read the docstring above.
        raise NotImplementedError("week 6. Fill in this gap in my_robot.py")

    # ======================= WEEK 7 (Lesson 10): safety =======================
    def is_safe(self, action):
        """Your Lesson 10 validate_action(action, set(self.objects)). Return its (ok, reason)."""
        # TODO week 7: fill in this gap (see 'Add it to your robot' on the week 7 page). Read the docstring above.
        raise NotImplementedError("week 7. Fill in this gap in my_robot.py")

    # ======================= WEEK 8 (Lesson 16): how fast does it think? =======================
    def think_time(self, text):
        """How long does understanding text take? Time self.understand(text) 5 times with your Lesson 16 time_it(),
        then summary = summarize(...). Return f"(I thought for {p50 in ms:.2f} ms, so I'd roll {distance in mm:.2f} mm meanwhile.)"
        using thinking_distance(p50 seconds), which gives metres.
        Then the budget: if NOT fits_budget(summary, 0.2), add " Too slow! I'd hit the cat before deciding to stop." """
        # TODO week 8: fill in this gap (see 'Add it to your robot' on the week 8 page). Read the docstring above.
        raise NotImplementedError("week 8. Fill in this gap in my_robot.py")

    # ======================= WEEK 9 (Lesson 17): learning from a teacher =======================
    def teacher_brain(self):
        """A smarter language brain: re-train on a teacher's labels with your Lesson 17 code:
        best_student(distill_examples(UNLABELLED, best_teacher()))."""
        # TODO week 9: fill in this gap (see 'Add it to your robot' on the week 9 page). Read the docstring above.
        raise NotImplementedError("week 9. Fill in this gap in my_robot.py")

    # ======================= WEEK 10 (Lesson 18): a world-class brain (needs an API key) =======================
    def ask_claude(self, text):
        """Ask Claude for a plan with your Lesson 18 ask_planner(), check it with validate_plan(), then do it.
          client = anthropic.Anthropic(); room = SimRobot(objects=self.objects, start=self.pos)
          plan_obj, info = ask_planner(client, room, text)
          not valid -> "I won't run Claude's plan: <reason>."    clarify -> return the question
          otherwise return Claude's reply plus self.do(a) for each action in plan_obj["plan"]."""
        # TODO week 10: fill in this gap (see 'Add it to your robot' on the week 10 page). Read the docstring above.
        raise NotImplementedError("week 10. Fill in this gap in my_robot.py")

    # ======================= WEEK 11 (Lesson 19): the exam =======================
    def exam(self):
        """Sit the 12 bake-off tasks. For each task in Lesson 19's TASKS: make a FRESH Robot(quiet=True),
        reply = robot.command(task["command"]), then your score_task(task, robot, {"reply": reply}).
        Print a ✓ or ✗ line per task (unless self.quiet), and return f"I passed {passed} of {len(TASKS)}." """
        # TODO week 11: fill in this gap (see 'Add it to your robot' on the week 11 page). Read the docstring above.
        raise NotImplementedError("week 11. Fill in this gap in my_robot.py")

    # ======================= WEEK 12 (Lesson 12): the routes people like =======================
    def nicest_route(self, target):
        """Pick the route people like best (Lesson 12): routes = candidate_routes(ROOM, self.pos, target);
        learn the taste once (CACHE["taste"] = train_reward_model(collect_comparisons(ROOM, routes from
        ROBOT_START to the bin, 150, random.Random(0)))), then return best_route(taste, ROOM, routes).
        If there are no candidate routes, return self.route(target)."""
        # TODO week 12: fill in this gap (see 'Add it to your robot' on the week 12 page). Read the docstring above.
        raise NotImplementedError("week 12. Fill in this gap in my_robot.py")

    # ======================= WEEK 12 BOSS (Lesson 14): use what your robot can SEE =======================
    def see_and_plan(self, text):
        """The two exam tasks every small brain fails need the robot to look at the room, not just read words.
        Your robot KNOWS where every block is (self.objects) and where the bin is. Return a plan for:
          "...closest to the bin..."         -> put away the unbinned block nearest the bin (Lesson 1's manhattan())
          "...room..." / "...everything..." / "...all..."  (but NOT if the text says "except" or "but")
                                             -> put away every unbinned block, red then blue then green
        A plan is a list of actions like [{"intent": "put", "object": "blue block"}].
        For anything else return None, and your language brain handles it as usual."""
        # TODO week 12: fill in this gap (see 'Add it to your robot' on the week 12 page). Read the docstring above.
        raise NotImplementedError("week 12. Fill in this gap in my_robot.py")

    # ======================= PROVIDED: the glue that joins your pieces =======================
    def step(self, square):
        """Move one square. Returns "moved", "stopped" (it saw the cat in time) or "bump"."""
        if square == CAT:
            if self.slow:
                return "late"               # 'slowbrain on': it was still thinking when it reached the cat
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
            return "BUMP! I walked into the cat. (It's not on my map, so I can't sense it yet: add week 3.)"
        if result == "late":
            return "BUMP! My slow brain was still thinking when I reached the cat. (Type 'slowbrain off'.)"
        why = f" (stop chance {self.last_stop[0]:.2f}, my safe threshold {self.last_stop[1]:.2f})" if self.last_stop else ""
        return f"Something is in the way at {square}! I stopped just in time{why}."

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
        if self.slow:
            time.sleep(0.5)                     # 'slowbrain on': pretend to be a huge brain far away
        if built(self.see_and_plan):
            plan = self.see_and_plan(text)
            if plan:
                return plan
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
                return self.arrows(t.upper())
            if low in ("slowbrain on", "slowbrain off"):
                self.slow = low.endswith("on")
                return "Pretending to be a very slow brain (half a second per thought)." if self.slow else "Normal brain again."
            if low.startswith("json:"):
                return self.run_plan([json.loads(t[5:])])  # pretend an AI sent this exact answer (Lesson 10)
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
            return self.run_plan(plan)
        except NotImplementedError as e:
            return f"I can't do that yet: {e}"
        except Exception as e:
            where = traceback.extract_tb(e.__traceback__)[-1]
            return (f"Oops, my code broke: {type(e).__name__}: {e} (in {where.name}(), line {where.lineno} of "
                    f"{Path(where.filename).name}). Read the hint again, fix it, and try again.")

    def run_plan(self, plan):
        """Check each action (if you've built week 7's is_safe), then do it. Without a safety check, a bad
        action reaches do() as it is, and do() may crash on it."""
        replies = []
        for action in plan:
            if built(self.is_safe):
                ok, reason = self.is_safe(action)
                if not ok:
                    replies.append(f"Sorry, I won't do that: {reason}.")
                    break
                replies.append(self.do(action))
                continue
            try:
                replies.append(self.do(action))
            except (KeyError, TypeError, ValueError) as e:
                replies.append(f"Uh oh! I tried to do {action} and crashed ({type(e).__name__}: {e}). Your code is fine: "
                               "it's a bad action. Week 7's safety check will stop bad actions before they reach do().")
                break
        return " ".join(r for r in replies if r)


# ======================= PROVIDED: what's built, the typing loop, the showcase =======================
PIECES = [("arrows", 1, "1", "moves with arrows (EESS)"), ("look", 2, "2-3", "looks around: 'look'"),
          ("should_stop_for", 3, "4-5", "stops before it bumps into the cat"), ("goto", 4, "6", "plans routes: 'goto blue'"),
          ("clean", 5, "8", "fixes typos"), ("do", 5, "9", "understands sentences, one action at a time"),
          ("understand_plans", 6, "15", "writes whole plans and asks when you're vague"), ("is_safe", 7, "10", "checks every action first"),
          ("think_time", 8, "16", "knows how long it thinks"), ("teacher_brain", 9, "17", "has a teacher-trained brain"),
          ("ask_claude", 10, "18", "can ask Claude: 'claude: tidy up the room' (needs a key)"), ("exam", 11, "19", "sits the exam: 'exam'"),
          ("nicest_route", 12, "12", "picks the routes people like"),
          ("see_and_plan", 12, "14", "the boss: uses what it SEES ('tidy up the room', 'the block closest to the bin')")]


def built(method):
    """A piece is built once its TODO is gone (it no longer just says NotImplementedError)."""
    return "raise NotImplementedError" not in inspect.getsource(method)


def banner(robot):
    done = [p for p in PIECES if built(getattr(robot, p[0]))]
    try:
        from lesson00_hello import introduce
        print("\n" + introduce(NAME))
    except NotImplementedError:
        pass
    print(f"\n=== {NAME}: built up to week {max([p[1] for p in done] or [0])} ===")
    for name, week, lessons, what in PIECES:
        print(f"  {'✓' if built(getattr(robot, name)) else '·'} week {week:>2}: {what}")
    todo = [p for p in PIECES if not built(getattr(robot, p[0])) and p[0] != "ask_claude"]   # Claude is optional
    if todo:
        print(f"  Next gap to fill: week {todo[0][1]}, the {todo[0][0]}() method in my_robot.py (see 'Add it to your robot' on the week {todo[0][1]} page).")
    try:
        from lesson11_robohelper import evaluate
        print(f"  Your week-7 capstone (RoboHelper, its simpler twin) passes {evaluate()[0]:.0%} of its final test.")
    except NotImplementedError:
        pass


def showcase():
    print(f"\n*** {NAME}: THE SHOWCASE ***")
    banner(Robot())
    for cmd in ["EEE", "look", "goto blue", "put teh green blok in the bin", "put the red and blue blocks away",
                "put the block away", "where's the green one?", "tidy up the room", 'json: {"intent": "launch", "object": "red block"}',
                "exam"]:
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
    built_count = sum(built(getattr(Robot, p[0])) for p in PIECES)
    print(f"\n*** {NAME}: {built_count} of {len(PIECES)} pieces built, every one of them by you. ***")


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
