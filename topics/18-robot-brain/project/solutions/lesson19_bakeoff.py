"""Lesson 19 (Week 15): the bake-off. Every brain, the same 12 tasks, the same room, the same cat.

You built brains from zero (word counter, tiny language model) and plugged in a world-class one
(Claude as planner, Claude as agent). Which is best? It depends what you measure:
did the robot do the RIGHT thing, how long did it think, and what did it cost?

    python3 lesson19_bakeoff.py                   score every brain that can run, save traces
    python3 lesson19_bakeoff.py --watch tinylm 5  watch one brain do task 5 in the terminal

Then open traces/bakeoff.json in the course's replay viewer (Lesson 19 page) to watch them side by side.
"""

import json
import sys
from pathlib import Path

from world import ROBOT_START
from sim import run_brain, watch, CAT
from lesson16_speed import summarize, cost_usd

# Each task says what a correct robot ends up doing:
#   binned   the bin must hold EXACTLY these blocks afterwards
#   still    True if the robot must not move at all (refuse, stop, or ask a question)
#   at       where the robot must end up
#   says     text the reply must contain
#   asks     True if the reply must be a question (ends with "?")
TASKS = [
    {"command": "put the red block in the bin", "binned": {"red block"}},
    {"command": "where's the green one?", "binned": set(), "still": True, "says": "(1, 5)"},
    {"command": "make me a sandwich", "binned": set(), "still": True},
    {"command": "put the red and blue blocks away", "binned": {"red block", "blue block"}},
    {"command": "tidy up the room", "binned": {"red block", "blue block", "green block"}},
    {"command": "bin everything except the green block", "binned": {"red block", "blue block"}},
    {"command": "put away the block that's closest to the bin", "binned": {"blue block"}},
    {"command": "put the block away", "binned": set(), "still": True, "asks": True},
    {"command": "go to the blue block", "binned": set(), "at": (6, 3)},
    {"command": "stop", "binned": set(), "still": True},
    {"command": "hmm what about the blue", "binned": set()},
    {"command": "put the purple block in the bin", "binned": set(), "still": True},
]


# ---------------- YOUR HOMEWORK ----------------

def score_task(task, robot, result):
    """Did the robot do the right thing? Return (passed, reason). Check, in this order:
      1. robot.binned == task["binned"]                 else (False, "binned X, wanted Y")
      2. task.get("still"): robot.pos must equal ROBOT_START   else (False, "moved but shouldn't have")
      3. "at" in task: robot.pos must equal task["at"]          else (False, "ended at P, wanted Q")
      4. "says" in task: task["says"] must be in result["reply"]       else (False, "reply missing ...")
      5. task.get("asks"): result["reply"] must end with "?" (after .strip()) else (False, "should ask a question")
    If all pass: (True, "ok")."""
    # BEGIN SOLUTION
    reply = result.get("reply", "")
    if robot.binned != task["binned"]:
        return False, f"binned {sorted(robot.binned) or 'nothing'}, wanted {sorted(task['binned']) or 'nothing'}"
    if task.get("still") and tuple(robot.pos) != ROBOT_START:
        return False, "moved but shouldn't have"
    if "at" in task and tuple(robot.pos) != task["at"]:
        return False, f"ended at {robot.pos}, wanted {task['at']}"
    if "says" in task and task["says"] not in reply:
        return False, f"reply missing {task['says']!r}"
    if task.get("asks") and not reply.strip().endswith("?"):
        return False, "should ask a question"
    return True, "ok"
    # END SOLUTION


def scorecard(rows):
    """rows: list of {"passed": bool, "seconds": float, "tokens_in": int, "tokens_out": int} for ONE brain.
    Return {"passed": count, "total": count, "p50": seconds, "p95": seconds, "cost": dollars}.
    Use summarize() and cost_usd() from Lesson 16."""
    # BEGIN SOLUTION
    s = summarize([r["seconds"] for r in rows])
    return {"passed": sum(r["passed"] for r in rows), "total": len(rows), "p50": s["p50"], "p95": s["p95"],
            "cost": cost_usd(sum(r["tokens_in"] for r in rows), sum(r["tokens_out"] for r in rows))}
    # END SOLUTION


# ---------------- provided: running the bake-off ----------------

def run_bakeoff(brain_names, tasks=TASKS):
    from brains import get_brain
    traces, cards = {}, {}
    for name in brain_names:
        try:
            brain = get_brain(name)
        except NotImplementedError:
            print(f"  ({name}: not built yet: it comes with the week 8 stretch or week 14, so it sits this one out)")
            continue
        rows, runs = [], []
        for task in tasks:
            robot, result = run_brain(brain, task["command"], surprises=task.get("surprises", (CAT,)))
            if result.get("missing"):
                break
            passed, reason = score_task(task, robot, result)
            rows.append({"passed": passed, "seconds": result["seconds"],
                         "tokens_in": result["tokens_in"], "tokens_out": result["tokens_out"]})
            runs.append({"command": task["command"], "passed": passed, "reason": reason, "reply": result.get("reply", ""),
                         "seconds": result["seconds"], "frames": robot.frames})
        if len(rows) < len(tasks):
            print(f"  skipping {brain.name}: {result.get('reply')}")
            continue
        cards[brain.name] = scorecard(rows)
        traces[brain.name] = runs
    return cards, traces


def print_table(cards, traces):
    names = list(cards)
    print(f"\n{'task':46}" + "".join(f"{n.split(' (')[0]:>16}" for n in names))
    for i, task in enumerate(TASKS):
        print(f"{str(i + 1) + '. ' + task['command']:46}" + "".join(f"{'✓' if traces[n][i]['passed'] else '✗':>16}" for n in names))
    print(f"{'PASSED':46}" + "".join(f"{str(cards[n]['passed']) + '/' + str(cards[n]['total']):>16}" for n in names))
    print(f"{'thinking time p50':46}" + "".join(f"{fmt_s(cards[n]['p50']):>16}" for n in names))
    print(f"{'thinking time p95':46}" + "".join(f"{fmt_s(cards[n]['p95']):>16}" for n in names))
    print(f"{'cost for all 12':46}" + "".join(f"{'$' + format(cards[n]['cost'], '.3f'):>16}" for n in names))


def fmt_s(s):
    return f"{s * 1000:.2f} ms" if s < 1 else f"{s:.1f} s"


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--watch"]:
        from brains import get_brain
        brain, task = get_brain(args[1]), TASKS[int(args[2]) - 1]
        robot, result = run_brain(brain, task["command"], surprises=task.get("surprises", (CAT,)))
        watch(robot.frames)
        print(f"\n[{brain.name}] {task['command']!r} -> {result['reply']!r}   {score_task(task, robot, result)}")
        sys.exit()
    names = args or ["words", "tinylm", "attention", "distilled", "tinylm-4bit", "planner-replay", "agent-replay"]
    cards, traces = run_bakeoff(names)
    print_table(cards, traces)
    out = Path(__file__).resolve().parent / "traces"
    out.mkdir(exist_ok=True)
    (out / "bakeoff.json").write_text(json.dumps({"tasks": [t["command"] for t in TASKS], "brains": traces}, indent=1))
    print(f"\nTraces saved to {out / 'bakeoff.json'}")
    for n, runs in traces.items():
        for i, r in enumerate(runs):
            if not r["passed"]:
                print(f"  {n.split(' (')[0]:8} task {i + 1:2}: {r['reason']}   (reply: {r['reply'][:60]!r})")
