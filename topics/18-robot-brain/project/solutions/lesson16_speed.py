"""Lesson 16 (Week 8): inference engineering, part 1. How fast is a brain, and what does it cost?

"Inference" = USING a trained model (as opposed to training it). Every time Robo-Helper hears a
command, its brain runs inference. Inference engineers measure four things:

  LATENCY      how long one answer takes (seconds). Measure many times: report the median (p50)
               and the slow tail (p95), never just the average.
  TTFT         time to first token: how long until the FIRST word comes back (streaming).
  THROUGHPUT   tokens per second once it's going.
  COST         money per answer. Cloud models charge per token in and per token out.

For a robot there's a fifth: how far does it travel (or how long does it stand frozen) while it thinks?
"""

import math
import statistics
import time

ROBOT_SPEED = 1.0           # metres per second, a slow indoor robot
PRICE_PER_MTOK = {"input": 4.00, "output": 20.00}   # claude-opus-5-5, US dollars per million tokens


# ---------------- YOUR HOMEWORK ----------------

def time_it(fn, repeats=20):
    """Call fn() `repeats` times. Return a list of how many seconds each call took.
    Use time.perf_counter() (a precise stopwatch) before and after each call."""
    # BEGIN SOLUTION
    out = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        out.append(time.perf_counter() - start)
    return out
    # END SOLUTION


def percentile(values, p):
    """The value that p% of the values are at or below (nearest-rank method):
    sort the values, then take the one at position ceil(p/100 * n) - 1 (but at least position 0).
    percentile([5, 1, 3, 2, 4], 50) == 3,  percentile(..., 100) == 5."""
    # BEGIN SOLUTION
    s = sorted(values)
    return s[max(0, math.ceil(p / 100 * len(s)) - 1)]
    # END SOLUTION


def summarize(seconds):
    """Return {"p50": ..., "p95": ..., "mean": ...} for a list of timings (all in seconds)."""
    # BEGIN SOLUTION
    return {"p50": percentile(seconds, 50), "p95": percentile(seconds, 95), "mean": statistics.mean(seconds)}
    # END SOLUTION


def tokens_per_second(tokens_out, seconds_total, ttft):
    """Throughput AFTER the first token: the tokens still to come divided by the time they took.
    (tokens_out - 1) / (seconds_total - ttft). Return 0.0 if there's no time left to divide by."""
    # BEGIN SOLUTION
    if seconds_total - ttft <= 0:
        return 0.0
    return (tokens_out - 1) / (seconds_total - ttft)
    # END SOLUTION


def cost_usd(tokens_in, tokens_out, price=PRICE_PER_MTOK):
    """Prices are per MILLION tokens. 1,000 tokens in and 200 out at $4/$20 costs $0.008."""
    # BEGIN SOLUTION
    return tokens_in / 1e6 * price["input"] + tokens_out / 1e6 * price["output"]
    # END SOLUTION


def thinking_distance(seconds, speed=ROBOT_SPEED):
    """Metres a robot moving at `speed` covers while its brain is busy for `seconds`."""
    # BEGIN SOLUTION
    return seconds * speed
    # END SOLUTION


def fits_budget(summary, budget_seconds):
    """A brain fits a latency budget only if its SLOW answers do: p95 <= budget."""
    # BEGIN SOLUTION
    return summary["p95"] <= budget_seconds
    # END SOLUTION


# ---------------- provided: measuring a real model with streaming ----------------

def measure_stream(client, command, model="claude-opus-5-5"):
    """Stream one answer from a real model and time it. Returns ttft, total, tokens_in, tokens_out.
    The model thinks before it writes, so TTFT includes thinking time."""
    start = time.perf_counter()
    ttft = None
    with client.messages.stream(
        model=model,
        max_tokens=2000,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": f"A robot heard: {command!r}. In one short sentence, what should it do?"}],
    ) as stream:
        for _ in stream.text_stream:
            if ttft is None:
                ttft = time.perf_counter() - start
        final = stream.get_final_message()
    total = time.perf_counter() - start
    return {"ttft": ttft or total, "total": total,
            "tokens_in": final.usage.input_tokens, "tokens_out": final.usage.output_tokens}


def load_recorded_seconds(kind):
    """Seconds per command from the recorded real runs (recordings/<kind>.json), or [] if none."""
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parent / "recordings" / f"{kind}.json"
    if not path.exists():
        return [], 0, 0
    runs = json.loads(path.read_text())["runs"]
    return [r["seconds"] for r in runs], sum(r["tokens_in"] for r in runs), sum(r["tokens_out"] for r in runs)


if __name__ == "__main__":
    from brains import get_brain
    from lesson09_commands import parse_command
    command = "put the red block in the bin"
    print(f"Timing each brain's THINKING on {command!r} (200 runs)\n")
    print(f"{'brain':30} {'p50':>10} {'p95':>10}  robot travels while thinking")
    small = []
    for n in ("tinylm", "attention", "tinylm-4bit"):
        try:
            small.append(get_brain(n))
        except NotImplementedError:
            print(f"({n}: not built yet: it comes with the week 6 stretch or week 9)")
    words = get_brain("words")
    thinkers = [(words, lambda: parse_command(words.model, command))] + [(b, (lambda b: lambda: b.model.generate(command))(b)) for b in small]
    for brain, think in thinkers:
        s = summarize(time_it(think, repeats=200))
        print(f"{brain.name:30} {s['p50'] * 1000:8.3f}ms {s['p95'] * 1000:8.3f}ms  {thinking_distance(s['p95']) * 1000:.2f} mm")
    for kind in ("planner", "agent"):
        secs, tin, tout = load_recorded_seconds(kind)
        if not secs:
            print(f"{kind + ' (Claude)':28}  no recordings yet (see brains.py record)")
            continue
        s = summarize(secs)
        print(f"{kind + ' (Claude, recorded)':28} {s['p50']:9.2f}s {s['p95']:9.2f}s  {thinking_distance(s['p95']):.1f} m"
              f"   cost for {len(secs)} commands: ${cost_usd(tin, tout):.3f}")
    print("\nBudget: the robot must react to a 'stop!' within 0.2 s.")
    print("Which brains could you trust with that? Which could still plan a whole tidy-up?")
