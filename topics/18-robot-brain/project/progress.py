"""Robo-Helper's progress report: what can YOUR robot do so far? Run it after every lesson.

    python3 progress.py              measures your homework
    python3 progress.py --solutions  measures the worked solutions

Every row runs real code from one lesson and measures what that lesson added to the robot.
Rows for lessons you haven't done yet say "not built yet". Takes about a minute (it trains the small brains).
"""

import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ("solutions" if "--solutions" in sys.argv else "homework")))

BRAINS = {}


def brain(name):
    from brains import get_brain
    if name not in BRAINS:
        BRAINS[name] = get_brain(name)
    return BRAINS[name]


def passed(task, robot, result):
    """The bake-off's exact check (Lesson 19 has you write it; progress uses its own copy so it works in any week)."""
    from world import ROBOT_START
    reply = result.get("reply", "")
    return (robot.binned == task["binned"] and not (task.get("still") and tuple(robot.pos) != ROBOT_START)
            and not ("at" in task and tuple(robot.pos) != task["at"]) and task.get("says", "") in reply
            and not (task.get("asks") and not reply.strip().endswith("?")))


def bakeoff(name):
    from sim import run_brain, CAT
    from lesson19_bakeoff import TASKS
    b = brain(name)
    return sum(passed(t, *run_brain(b, t["command"], surprises=t.get("surprises", (CAT,)))) for t in TASKS)


def typo_score(name, fix):
    """Typo commands where the robot does exactly what it does for the correct spelling."""
    import brains
    from sim import run_brain
    from lesson08_words import TYPO_COMMANDS
    b, orig = brain(name), brains.clean
    if not fix:
        brains.clean = lambda c: c
    try:
        same = 0
        for typo, meant in TYPO_COMMANDS:
            r1, o1 = run_brain(b, typo)
            r2, o2 = run_brain(b, meant)
            same += (r1.binned, tuple(r1.pos), o1["reply"]) == (r2.binned, tuple(r2.pos), o2["reply"])
        return f"{same}/{len(TYPO_COMMANDS)}"
    finally:
        brains.clean = orig


# ---------------- one function per lesson: returns what it measured ----------------

def l01():
    from world import ROOM, ROBOT_START
    from lesson01_moving import follow
    return f"follows the commands EEEESSS from {ROBOT_START} to {follow(ROOM, ROBOT_START, 'EEEESSS')[-1]}"


def l02():
    from world import ROOM
    from lesson02_sensors import distance_to_wall, average_error
    d = distance_to_wall(ROOM, (1, 1), "E")
    one, many = (average_error(d, 1.0, n, 500, random.Random(0)) for n in (1, 16))
    return f"distance sensor error {one:.2f} -> {many:.2f} by averaging 16 readings"


def l03():
    from lesson03_learning import fit_line, max_safe_speed, STOP_DATA
    w, b, hist = fit_line(STOP_DATA)
    return f"learned its braking distance (error {hist[0]:.2f} -> {hist[-1]:.4f}); safe speed with 1 m free: {max_safe_speed(w, b, 1.0)} m/s"


def l05():
    from lesson04_neuron import make_obstacle_data, train_neuron
    from lesson05_evaluate import train_test_split, safest_threshold, evaluate
    rng = random.Random(2)
    train, test = train_test_split(make_obstacle_data(600, rng), 0.25, rng)
    w, b = train_neuron(train)
    r = evaluate(w, b, test, safest_threshold(w, b, train))
    return f"stop detector catches {r['recall']:.0%} of obstacles on new data (precision {r['precision']:.0%})"


def l06():
    from world import ROOM, ROBOT_START, find_bin
    from lesson06_paths import astar_path
    path, expanded = astar_path(ROOM, ROBOT_START, find_bin(ROOM))
    return f"plans the shortest route to the bin: {len(path) - 1} steps (A* looked at {expanded} squares)"


def l07():
    from lesson07_trial_error import MAZE, find_char, q_learn
    _, log = q_learn(MAZE, find_char(MAZE, "S"), find_char(MAZE, "G"), rng=random.Random(0))
    return f"learns a maze by trial and error: {log[0]} steps on the first try -> {log[-1]} on the last"


def l08():
    return f"typo commands handled like the correct spelling: {typo_score('words', False)} -> {typo_score('words', True)} with the typo fixer"


def l09():
    return f"understands one action per command: bake-off {bakeoff('words')}/12"


def l15():
    from lesson15_tiny_lm import accuracy, test_data
    return f"writes whole plans and asks when unsure: bake-off {bakeoff('tinylm')}/12, new commands {accuracy(brain('tinylm').model, test_data()):.0%}"


def l15a():
    from lesson15_tiny_lm import accuracy, test_data
    a, t = accuracy(brain('attention').model, test_data()), accuracy(brain('tinylm').model, test_data())
    return f"attention: new commands {a:.0%} (tiny LM {t:.0%}; over 3 seeds 92% vs 89%), bake-off {bakeoff('attention')}/12"


def l10():
    from world import OBJECTS
    from lesson09_commands import TRAIN, train_intent_model, parse_command
    from lesson10_llm_safety import MOCK_REPLIES, safe_parse
    model = train_intent_model(TRAIN)
    caught = sum(safe_parse(r, set(OBJECTS), c, lambda x: parse_command(model, x))[1] != "llm" for c, r in MOCK_REPLIES)
    return f"checks every AI answer before moving: {caught} broken answers caught, {len(MOCK_REPLIES) - caught} good ones let through"


def l11():
    from lesson11_robohelper import evaluate
    rate, failures = evaluate()
    return f"the whole robot, tested end to end: {rate:.0%} of test commands done right"


def l16():
    from lesson16_speed import time_it, summarize, thinking_distance
    b = brain("tinylm")
    s = summarize(time_it(lambda: b.model.generate("put the red and blue blocks away"), repeats=50))
    return f"knows how long it thinks: tiny LM p95 {s['p95'] * 1000:.1f} ms = {thinking_distance(s['p95']) * 1000:.1f} mm rolled while thinking"


def l17():
    from lesson17_faster import count_weights, size_bytes
    n = count_weights(brain("distilled").model)
    return (f"learns new phrasings from a teacher: bake-off {bakeoff('distilled')}/12; "
            f"4-bit copy {bakeoff('tinylm-4bit')}/12 at {size_bytes(n, 4):.0f} bytes (was {size_bytes(n, 32):.0f})")


def l13():
    from lesson13_lora import factory_model, our_robot_truth, make_examples, train_lora, mse, matvec, lora_forward, count_params
    rng = random.Random(0)
    W = factory_model(rng)
    truth = our_robot_truth(W)
    train, test = make_examples(truth, 12, rng), make_examples(truth, 200, rng)
    A, B = train_lora(W, train, rank=1)
    return (f"fixes its leaky sensor with LoRA: danger error {mse(lambda x: matvec(W, x), test):.3f} -> "
            f"{mse(lambda x: lora_forward(W, A, B, x), test):.3f}, training {count_params(A, B)} numbers")


def l18():
    if not brain("planner-replay").runs:
        raise FileNotFoundError
    score = bakeoff("planner-replay")
    return f"Claude plans with the whole room in view (recorded): bake-off {score}/12"


def l19():
    scores = {n: bakeoff(n) for n in ("words", "tinylm", "distilled")}
    return "the same 12 tasks for every brain: " + ", ".join(f"{n} {s}/12" for n, s in scores.items())


def l12():
    from world import ROOM, ROBOT_START, find_bin
    from lesson06_paths import astar_path
    from lesson12_preferences import candidate_routes, collect_comparisons, train_reward_model, best_route, route_features
    rng = random.Random(0)
    routes = candidate_routes(ROOM, ROBOT_START, find_bin(ROOM))
    w = train_reward_model(collect_comparisons(ROOM, routes, 150, rng))
    a = route_features(ROOM, astar_path(ROOM, ROBOT_START, find_bin(ROOM))[0])
    b = route_features(ROOM, best_route(w, ROOM, routes))
    return f"picks the route people prefer: wall brushes {a[1]} -> {b[1]}, turns {a[2]} -> {b[2]} (same {b[0]} steps)"


def l20():
    from lesson20_mcp_server import RobotService
    s = RobotService()
    s.call("go_to", {"object": "green block"})
    ok, _ = s.call("pick_up", {"object": "green block"})
    return "any AI app can drive it over MCP, and the server's own rules hold" if not ok else "server let an AI pick up the protected block!"


ROWS = [
    ("1", "01", "moves", l01), ("2", "02", "senses", l02), ("2", "03", "learns", l03), ("3", "04-05", "decides to stop", l05),
    ("4", "06", "finds the way", l06), ("bonus", "07", "learns by trying", l07), ("5", "08", "reads typos", l08),
    ("5", "09", "understands", l09), ("6", "15", "writes plans", l15), ("6+", "15 stretch", "attention", l15a),
    ("7", "10", "stays safe", l10), ("7", "11", "capstone", l11), ("8", "16", "speed", l16), ("9", "17", "faster, smarter", l17),
    ("9", "13", "adapts (LoRA)", l13), ("10", "18", "world-class brain", l18), ("11", "19", "bake-off", l19),
    ("12", "12", "what people like", l12), ("bonus", "20", "MCP", l20),
]

if __name__ == "__main__":
    print(f"Robo-Helper progress report ({'solutions' if '--solutions' in sys.argv else 'your homework'})\n")
    print(f"{'week':6}{'lesson':12}{'ability':20}measured")
    done = 0
    start = time.perf_counter()
    for week, lesson, ability, fn in ROWS:
        try:
            result = fn()
            done += 1
        except NotImplementedError:
            result = "… not built yet"
        except FileNotFoundError:
            result = "… needs recordings (see brains.py record)"
        except Exception as e:
            result = f"✗ broken: {type(e).__name__}: {e}"
        print(f"{week:6}{lesson:12}{ability:20}{result}", flush=True)
    print(f"\n{done} of {len(ROWS)} abilities working   ({time.perf_counter() - start:.0f} s)")
