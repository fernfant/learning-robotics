"""MY ROBOT. You build this file yourself, one piece a week.

Every lesson ends with "Add it to your robot": a small gap in this file, marked with the week, that you fill in
by connecting what you just built (your lesson file) to your robot. Until you fill a gap, your robot says
"I can't do that yet". When you fill it, your robot can.

    cd homework
    python3 my_robot.py            talk to your robot ('help' shows what it can do, 'quit' stops)
    python3 my_robot.py --show     week 16: the showcase (a demo, the 12-task exam, then YOUR tests in my_tasks.txt)
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
        self.last_stop = None           # week 4: (stop chance, threshold) the last time it saw something
        self.slow = False               # week 13: 'slowbrain on' pretends the brain is very slow
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
        # BEGIN ROBOT week=1 lessons=1
        from lesson01_moving import move, safe_move
        for d in text.upper():
            if safe_move(ROOM, self.pos, d) == self.pos:
                return f"Bonk! A wall. I'm at {self.pos}."
            result = self.step(move(self.pos, d))
            if result != "moved":
                return self.step_message(result, move(self.pos, d))
        return f"I'm at {self.pos}."
        # END ROBOT

    # ======================= WEEK 2 (Lessons 2-3): sensing =======================
    def look(self):
        """What the sensors see. A real sensor is noisy, so average 16 readings (Lesson 2):
          for each direction "N", "E", "S", "W":  true = distance_to_wall(ROOM, self.pos, direction)
                                                    seen = smoothed_reading(true, 0.5, 16, random.Random())
          return f"Walls (average of 16 readings): north {N:.1f}, east {E:.1f}, south {S:.1f}, west {W:.1f}."
        Lesson 3 adds the safe speed to the end: w, b, _ = fit_line(STOP_DATA); one square is 0.5 m, so the free space
        in metres is (the smallest TRUE distance) * 0.5 + 0.5; then add f" Safe speed: {max_safe_speed(w, b, free)} m/s." """
        # BEGIN ROBOT week=2 lessons=2-3
        from lesson02_sensors import distance_to_wall, smoothed_reading
        from lesson03_learning import STOP_DATA, fit_line, max_safe_speed
        true = {k: distance_to_wall(ROOM, self.pos, k) for k in "NESW"}
        seen = {k: smoothed_reading(true[k], 0.5, 16, random.Random()) for k in "NESW"}
        w, b, _ = fit_line(STOP_DATA)
        speed = max_safe_speed(w, b, min(true.values()) * 0.5 + 0.5)
        return (f"Walls (average of 16 readings): north {seen['N']:.1f}, east {seen['E']:.1f}, south {seen['S']:.1f}, "
                f"west {seen['W']:.1f}. Safe speed: {speed} m/s.")
        # END ROBOT

    # ======================= WEEK 3 (Lesson 21): real sensor data from a phone =======================
    def phone(self, path):
        """Describe a real phone recording (your own from phyphox, or data/phone_acc.csv), with your week 3 code:
          times, xs, ys, zs = read_phone_csv(path)
          tilt  = tilt_degrees(average x, average y, average z)
          mags  = moving_average([magnitude(x, y, z) for each reading], 5)
          steps = count_steps(mags, 10.5, 15)
        Return f"{seconds:.0f} s of real data: tilted {tilt:.0f} degrees on average, {steps} steps." """
        # BEGIN ROBOT week=3 lessons=21
        from lesson21_phone import read_phone_csv, magnitude, moving_average, tilt_degrees, count_steps
        times, xs, ys, zs = read_phone_csv(path)
        n = len(times)
        tilt = tilt_degrees(sum(xs) / n, sum(ys) / n, sum(zs) / n)
        mags = moving_average([magnitude(x, y, z) for x, y, z in zip(xs, ys, zs)], 5)
        steps = count_steps(mags, 10.5, 15)
        return f"{times[-1] - times[0]:.0f} s of real data: tilted {tilt:.0f} degrees on average, {steps} steps."
        # END ROBOT

    # ======================= WEEK 4 (Lessons 4-5): stopping in time =======================
    def should_stop_for(self, square):
        """Something is one square ahead (0.5 m away) and the robot is driving at 0.5 m/s. Should it stop?
        Train your Lesson 4 neuron on make_obstacle_data(450, random.Random(0)), pick the threshold with your
        Lesson 5 safest_threshold(), then return should_stop(weights, bias, (0.5, 0.5), threshold).
        Also remember what it decided, so the robot can tell you: self.last_stop = (neuron(w, b, (0.5, 0.5)), threshold).
        Tip: train once and keep it in CACHE["stop"] so it isn't retrained on every step."""
        # BEGIN ROBOT week=4 lessons=4-5
        from lesson04_neuron import make_obstacle_data, train_neuron, should_stop, neuron
        from lesson05_evaluate import safest_threshold
        if "stop" not in CACHE:
            data = make_obstacle_data(450, random.Random(0))
            w, b = train_neuron(data)
            CACHE["stop"] = (w, b, safest_threshold(w, b, data))
        w, b, t = CACHE["stop"]
        self.last_stop = (neuron(w, b, (0.5, 0.5)), t)
        return should_stop(w, b, (0.5, 0.5), t)
        # END ROBOT

    # ======================= WEEK 5 (Lesson 6): finding the way =======================
    def route(self, target):
        """The shortest path from self.pos to target, avoiding self.blocked: your Lesson 6 astar_path().
        Return just the path (a list of squares), or None if there isn't one."""
        # BEGIN ROBOT week=5 lessons=6
        from lesson06_paths import astar_path
        path, _ = astar_path(ROOM, self.pos, target, blocked=self.blocked)
        return path
        # END ROBOT

    def goto(self, target):
        """Drive to target. Returns "" if it arrived, or a message saying why not.
          Repeat up to 6 times:
            path = self.plan_route(target)            (PROVIDED below: your route(), or a nicer one in week 16)
            if path is None: return "I can't find a way there."
            for each square after the first: result = self.step(square)
                "bump" (or "late") -> return self.step_message(result, square)
                "stopped" -> self.say(self.step_message("stopped", square)) and plan again (break)
            if every step worked: return ""
          After 6 tries: return "Too many surprises, giving up." """
        # BEGIN ROBOT week=5 lessons=6
        for _ in range(6):
            path = self.plan_route(target)
            if path is None:
                return "I can't find a way there."
            for square in path[1:]:
                result = self.step(square)
                if result in ("bump", "late"):
                    return self.step_message(result, square)
                if result == "stopped":
                    self.say(self.step_message("stopped", square))
                    break
            else:
                return ""
        return "Too many surprises, giving up."
        # END ROBOT

    # ======================= WEEK 6 (Lesson 22): two sensors, one steady angle =======================
    def steady(self):
        """While walking (150-162 s of the shipped recording), how much does the angle wobble? Use your week 6 code:
          t, acc, rate = load(149.9, 161.6); truth = still_angle(t, acc, 149.9, 161.6)
          fused = complementary(acc[0], rate, acc, DT, 0.98)
        Return f"Accelerometer alone wobbles {wobble(t, acc, 149.9, 161.6, truth):.1f} degrees; fused, {wobble(...fused...):.1f}." """
        # BEGIN ROBOT week=6 lessons=22
        from lesson22_fusion import load, still_angle, complementary, wobble, DT
        t, acc, rate = load(149.9, 161.6)
        truth = still_angle(t, acc, 149.9, 161.6)
        fused = complementary(acc[0], rate, acc, DT, 0.98)
        return (f"Accelerometer alone wobbles {wobble(t, acc, 149.9, 161.6, truth):.1f} degrees; "
                f"fused, {wobble(t, fused, 149.9, 161.6, truth):.1f}.")
        # END ROBOT

    # ======================= WEEK 7 (Lessons 8-9): understanding words =======================
    def clean(self, text):
        """Fix typos with your Lesson 8 fix_typos(). The word counts come from the words your robot knows,
        the commands in Lesson 9's TRAIN (a list of (command, intent) pairs, so take just the command):
            words = [command for command, intent in TRAIN]
            CACHE["counts"] = count_bigrams(tokenize(" . ".join(words)))
        Then return fix_typos(text, CACHE["counts"])."""
        # BEGIN ROBOT week=7 lessons=8
        from lesson08_words import tokenize, count_bigrams, fix_typos
        from lesson09_commands import TRAIN
        if "counts" not in CACHE:
            words = [command for command, intent in TRAIN]
            CACHE["counts"] = count_bigrams(tokenize(" . ".join(words)))
        return fix_typos(text, CACHE["counts"])
        # END ROBOT

    def understand_words(self, text):
        """One sentence -> a list with ONE action, using your Lesson 9 parse_command().
        Train the word counter once: CACHE["words"] = train_intent_model(TRAIN)."""
        # BEGIN ROBOT week=7 lessons=9
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
                  and return "The red block is in the bin."
          anything else -> raise ValueError(f"I don't know how to {intent!r}") """
        # BEGIN ROBOT week=7 lessons=9
        intent, obj = action["intent"], action["object"]
        if intent == "stop":
            return "Stopping."
        if intent == "find":
            return f"The {obj} is in the bin." if obj in self.binned else f"The {obj} is at {self.objects[obj]}."
        if intent == "go":
            return self.goto(self.objects[obj]) or f"I'm next to the {obj}."
        if intent != "put":
            raise ValueError(f"I don't know how to {intent!r}")
        if obj in self.binned:
            return f"The {obj} is already in the bin."
        msg = self.goto(self.objects[obj]) or self.goto(find_bin(ROOM))
        if msg:
            return msg
        self.binned.add(obj)
        self.objects[obj] = find_bin(ROOM)
        return f"The {obj} is in the bin."
        # END ROBOT

    # ======================= WEEK 8 (Lesson 15): writing whole plans =======================
    def understand_plans(self, text):
        """Use your Lesson 15 language model to write a plan: words = self.brain().generate(text), then
        plan = words_to_plan(words).
          None   -> return "Sorry, my answer made no sense."
          "ask"  -> return "Which block do you mean: red, blue or green?"
          "none" -> return "Sorry, that's not something I can do."
          otherwise return the plan (a list of actions)."""
        # BEGIN ROBOT week=8 lessons=15
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

    # ======================= WEEK 9 (Lesson 23): real wheels, odometry and PID =======================
    def drive(self, square):
        """Drive the robot's BODY (body.py: wheels that slip, motors with momentum) to the middle of a grid square,
        steering with your PID and tracking itself with your odometry (week 9):
          body = Body(start=self.pos, seed=4); odo = Odometer(body, (*centre(self.pos), 0.0))
          self.blocked.add(CAT)        (it met the cat in week 4: plan around it)
          for each square on self.route(square) after the first: drive_to(body, odo, centre(that square))
        Then compare where it THINKS it is (odo.pose) with where it REALLY is (body.true_pose()).
        Return f"Arrived. I think I'm at ({x:.2f}, {y:.2f}); really I'm {error:.2f} m away from that."
        and if body.bumped, add " I scraped a wall on the way: my odometry drifted and I didn't notice. (Weeks 11-12 fix this.)" """
        # BEGIN ROBOT week=9 lessons=23
        from body import Body, centre
        from lesson23_wheels import Odometer, drive_to
        body = Body(start=self.pos, seed=4)
        odo = Odometer(body, (*centre(self.pos), 0.0))
        self.blocked.add(CAT)
        path = self.route(square) or [self.pos]
        for sq in path[1:]:
            drive_to(body, odo, centre(sq))
        x, y, _ = body.true_pose()
        error = ((odo.pose[0] - x) ** 2 + (odo.pose[1] - y) ** 2) ** 0.5
        self.body = body
        msg = f"Arrived. I think I'm at ({odo.pose[0]:.2f}, {odo.pose[1]:.2f}); really I'm {error:.2f} m away from that."
        if body.bumped:
            msg += " I scraped a wall on the way: my odometry drifted and I didn't notice. (Weeks 11-12 fix this.)"
        return msg
        # END ROBOT

    # ======================= WEEK 10 (Lesson 10): safety =======================
    def is_safe(self, action):
        """Your Lesson 10 validate_action(action, set(self.objects)). Return its (ok, reason)."""
        # BEGIN ROBOT week=10 lessons=10
        from lesson10_llm_safety import validate_action
        return validate_action(action, set(self.objects))
        # END ROBOT

    # ======================= WEEK 11 (Lesson 24): scan the room and make a map =======================
    def make_map(self):
        """Drive around the room scanning, and build a map with your week 11 add_scan and to_map (explore() does
        the driving). Return the map rows plus a last line saying how many squares are right:
          rows, _ = explore(True); right, total = score(rows)
          return rows + [f"{right:.0%} of {total} squares right (the 'c' square is the cat the official map doesn't know)"]"""
        # BEGIN ROBOT week=11 lessons=24
        from lesson24_map import explore, score
        rows, _ = explore(True)
        right, total = score(rows)
        rows = [r[:4] + ("c" if r[4] == "#" and i == 1 else r[4]) + r[5:] for i, r in enumerate(rows)]
        return rows + [f"{right:.0%} of {total} squares right (the 'c' square is the cat the official map doesn't know)"]
        # END ROBOT

    # ======================= WEEK 12 (Lesson 25): where am I? =======================
    def where_am_i(self, square=(6, 3)):
        """Kidnapped! The robot's body is put down on `square` facing west, and it has no idea where. Use your
        week 12 particle filter: body = Body(start=square, heading_deg=180, seed=5); guess = localise(body, random.Random(7))
        Return f"I think I'm at ({gx:.2f}, {gy:.2f}). Really ({x:.2f}, {y:.2f}): {error:.2f} m off." """
        # BEGIN ROBOT week=12 lessons=25
        from body import Body
        from lesson25_localise import localise, error
        body = Body(start=square, heading_deg=180, seed=5)
        guess = localise(body, random.Random(7))
        x, y, _ = body.true_pose()
        return f"I think I'm at ({guess[0]:.2f}, {guess[1]:.2f}). Really ({x:.2f}, {y:.2f}): {error(body, guess):.2f} m off."
        # END ROBOT

    # ======================= WEEK 13 (Lesson 16): how fast does it think? =======================
    def think_time(self, text):
        """How long does understanding text take? Time self.understand(text) 5 times with your Lesson 16 time_it(),
        then summary = summarize(...). Return f"(I thought for {p50 in ms:.2f} ms, so I'd roll {distance in mm:.2f} mm meanwhile.)"
        using thinking_distance(p50 seconds), which gives metres.
        Then the budget: if NOT fits_budget(summary, 0.2), add " Too slow! I'd hit the cat before deciding to stop." """
        # BEGIN ROBOT week=13 lessons=16
        from lesson16_speed import time_it, summarize, thinking_distance, fits_budget
        summary = summarize(time_it(lambda: self.understand(text), 5))
        p50 = summary["p50"]
        msg = f"(I thought for {p50 * 1000:.2f} ms, so I'd roll {thinking_distance(p50) * 1000:.2f} mm meanwhile.)"
        if not fits_budget(summary, 0.2):
            msg += " Too slow! I'd hit the cat before deciding to stop."
        return msg
        # END ROBOT

    # ======================= WEEK 14 (Lesson 17): learning from a teacher =======================
    def teacher_brain(self):
        """A smarter language brain: re-train on a teacher's labels with your Lesson 17 code:
        best_student(distill_examples(UNLABELLED, best_teacher()))."""
        # BEGIN ROBOT week=14 lessons=17
        from lesson17_faster import distill_examples, UNLABELLED, best_teacher, best_student
        return best_student(distill_examples(UNLABELLED, best_teacher()))
        # END ROBOT

    # ======================= WEEK 15 (Lesson 18): a world-class brain (needs an API key) =======================
    def ask_claude(self, text):
        """Ask Claude for a plan with your Lesson 18 ask_planner(), check it with validate_plan(), then do it.
          client = anthropic.Anthropic(); room = SimRobot(objects=self.objects, start=self.pos)
          plan_obj, info = ask_planner(client, room, text)
          not valid -> "I won't run Claude's plan: <reason>."    clarify -> return the question
          otherwise return Claude's reply plus self.do(a) for each action in plan_obj["plan"]."""
        # BEGIN ROBOT week=15 lessons=18
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

    # ======================= WEEK 15 (Lesson 19): the exam =======================
    def exam(self):
        """Sit the 12 bake-off tasks. For each task in Lesson 19's TASKS: make a FRESH Robot(quiet=True),
        reply = robot.command(task["command"]), then your score_task(task, robot, {"reply": reply}).
        Print a ✓ or ✗ line per task (unless self.quiet), and return f"I passed {passed} of {len(TASKS)}." """
        # BEGIN ROBOT week=15 lessons=19
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

    # ======================= WEEK 16 (Lesson 12): the routes people like =======================
    def nicest_route(self, target):
        """Pick the route people like best (Lesson 12): routes = candidate_routes(ROOM, self.pos, target);
        learn the taste once (CACHE["taste"] = train_reward_model(collect_comparisons(ROOM, routes from
        ROBOT_START to the bin, 150, random.Random(0)))), then return best_route(taste, ROOM, routes).
        If there are no candidate routes, return self.route(target)."""
        # BEGIN ROBOT week=16 lessons=12
        from lesson12_preferences import candidate_routes, collect_comparisons, train_reward_model, best_route
        if "taste" not in CACHE:
            start_routes = candidate_routes(ROOM, ROBOT_START, find_bin(ROOM))
            CACHE["taste"] = train_reward_model(collect_comparisons(ROOM, start_routes, 150, random.Random(0)))
        routes = candidate_routes(ROOM, self.pos, target)
        return best_route(CACHE["taste"], ROOM, routes) if routes else self.route(target)
        # END ROBOT

    # ======================= WEEK 16 BOSS (Lesson 14): use what your robot can SEE =======================
    def see_and_plan(self, text):
        """The two exam tasks every small brain fails need the robot to look at the room, not just read words.
        Your robot KNOWS where every block is (self.objects) and where the bin is. Return a plan for:
          "...closest to the bin..."         -> put away the unbinned block nearest the bin (Lesson 1's manhattan())
          "...room..." / "...everything..." / "...all..."  (but NOT if the text says "except" or "but")
                                             -> put away every unbinned block, red then blue then green
        A plan is a list of actions like [{"intent": "put", "object": "blue block"}].
        For anything else return None, and your language brain handles it as usual."""
        # BEGIN ROBOT week=16 lessons=14
        from lesson01_moving import manhattan
        words = text.lower().split()
        left = [b for b in ("red block", "blue block", "green block") if b not in self.binned]
        if "closest" in words and left:
            nearest = min(left, key=lambda b: manhattan(self.objects[b], find_bin(ROOM)))
            return [{"intent": "put", "object": nearest}]
        if any(w in words for w in ("room", "everything", "all")) and not any(w in words for w in ("except", "but")):
            return [{"intent": "put", "object": b} for b in left]
        return None
        # END ROBOT

    # ======================= WEEK 16 BODY CAPSTONE: everything together, on wheels =======================
    def rescue(self, name):
        """The real-robot finale. The body is dropped somewhere it doesn't know (square (6, 3), facing west). Then:
          1. body = Body(start=(6, 3), heading_deg=180, seed=5); guess = localise(body, random.Random(7))   (week 12)
          2. start = square_of(guess[0], guess[1]) (week 11); goal = self.objects[name + " block"]
             path = astar_path(ROOM, start, goal)[0]                                                        (week 5)
          3. odo = Odometer(body, guess); drive_to(body, odo, centre(sq)) for every square after the first   (week 9)
          4. Compare: x, y, _ = body.true_pose(); how far is it really from centre(goal)?
        Return f"Rescued the {name} block: I started lost, found myself, and drove there. I'm {miss:.2f} m from it." """
        # BEGIN ROBOT week=16 lessons=14
        from body import Body, centre
        from lesson06_paths import astar_path
        from lesson23_wheels import Odometer, drive_to
        from lesson24_map import square_of
        from lesson25_localise import localise
        body = Body(start=(6, 3), heading_deg=180, seed=5)
        guess = localise(body, random.Random(7))
        goal = self.objects[name + " block"]
        path = astar_path(ROOM, square_of(guess[0], guess[1]), goal)[0]
        odo = Odometer(body, guess)
        for sq in path[1:]:
            drive_to(body, odo, centre(sq))
        x, y, _ = body.true_pose()
        gx, gy = centre(goal)
        miss = ((x - gx) ** 2 + (y - gy) ** 2) ** 0.5
        return f"Rescued the {name} block: I started lost, found myself, and drove there. I'm {miss:.2f} m from it."
        # END ROBOT

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
            return "BUMP! I walked into the cat. (It's not on my map, so I can't sense it yet: add week 4.)"
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
            if low.startswith("phone"):
                path = t[5:].strip() or str(Path(__file__).resolve().parent / "data" / "phone_acc.csv")
                return self.phone(path)
            if low == "steady":
                return self.steady()
            if low.startswith("drive "):
                name = low[6:].strip()
                target = find_bin(ROOM) if name == "bin" else self.objects.get(f"{name} block")
                return "Try drive red, drive blue, drive green or drive bin." if target is None else self.drive(target)
            if low == "map":
                return "\n  ".join(self.make_map())
            if low == "whereami":
                return self.where_am_i()
            if low.startswith("rescue "):
                name = low[7:].strip()
                return self.rescue(name) if f"{name} block" in self.objects else "Try rescue red, rescue blue or rescue green."
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
        """Check each action (if you've built week 10's is_safe), then do it. Without a safety check, a bad
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
                               "it's a bad action. Week 10's safety check will stop bad actions before they reach do().")
                break
        return " ".join(r for r in replies if r)


# ======================= PROVIDED: what's built, the typing loop, the showcase =======================
PIECES = [("arrows", 1, "1", "moves with arrows (EESS)"), ("look", 2, "2-3", "looks around: 'look'"),
          ("phone", 3, "21", "reads REAL phone sensor data: 'phone'"),
          ("should_stop_for", 4, "4-5", "stops before it bumps into the cat"), ("goto", 5, "6", "plans routes: 'goto blue'"),
          ("steady", 6, "22", "fuses two sensors into one steady angle: 'steady'"),
          ("clean", 7, "8", "fixes typos"), ("do", 7, "9", "understands sentences, one action at a time"),
          ("understand_plans", 8, "15", "writes whole plans and asks when you're vague"),
          ("drive", 9, "23", "drives on real wheels with PID and odometry: 'drive blue'"),
          ("is_safe", 10, "10", "checks every action first"),
          ("make_map", 11, "24", "scans the room and draws its own map: 'map'"),
          ("where_am_i", 12, "25", "finds itself when it's kidnapped: 'whereami'"),
          ("think_time", 13, "16", "knows how long it thinks"), ("teacher_brain", 14, "17", "has a teacher-trained brain"),
          ("ask_claude", 15, "18", "can ask Claude: 'claude: tidy up the room' (needs a key)"), ("exam", 15, "19", "sits the exam: 'exam'"),
          ("nicest_route", 16, "12", "picks the routes people like"),
          ("see_and_plan", 16, "14", "the boss: uses what it SEES ('tidy up the room', 'the block closest to the bin')"),
          ("rescue", 16, "14", "the body capstone: lost, finds itself, drives there on wheels: 'rescue blue'")]


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
