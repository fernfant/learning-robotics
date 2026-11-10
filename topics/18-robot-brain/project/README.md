# Robo-Helper: build a robot brain from scratch

Over 16 weeks you'll build **Robo-Helper**, a robot in a simulated room. Its **body** half works on real sensor data
from a phone (data/: a real recording, plus your own from the free phyphox app): smoothing, tilt, steps, gyroscope drift
and sensor fusion. Then wheels with encoders and odometry, a PID controller, a laser scanner that builds a map, and a
particle filter that finds the robot when it's lost. Its **brain** half understands commands like
*"put the red block in the bin"*, writes plans, checks itself for safety, and is measured honestly against a world-class
model. Every lesson adds one real piece to YOUR robot (`homework/my_robot.py`).

## What you need

- A computer with **Python 3.8 or newer**. Check by typing `python3 --version` in a terminal.
- No extra packages. Everything uses only Python's standard library.
- (Optional, weeks 15–15) an Anthropic API key, to use Claude as the robot's brain. Ask a parent or guardian, since it costs a
  little money (the whole bake-off is about a dollar). Without a key you replay **recorded real runs**, so nothing is blocked.
  Set it up like this (once):

  ```
  python3 -m venv ~/robo-venv
  source ~/robo-venv/bin/activate
  pip install anthropic
  ```
  Then add `export ANTHROPIC_API_KEY=...` to your `~/.zshrc` (or ask a parent to). Never paste a key into code, a chat or a file you share.

## The folders

```
project/
  homework/      <- YOUR files. Open the lesson file, fill in the TODOs.
  solutions/     <- worked answers. Only peek after you've really tried!
  check.py       <- marks your homework
  make_starters.py  (for teachers: rebuilds homework/ from solutions/)
```

## Running the robot with different brains (from week 10)

```
cd solutions        (or homework, once your lessons are done)
python3 sim.py "put the red and blue blocks away" --brain words --watch
python3 sim.py "bin everything except the green block" --brain tinylm --watch
python3 sim.py "tidy up the room" --brain planner-replay --watch    (Claude, recorded)
python3 sim.py "tidy up the room" --brain agent                      (Claude, live: needs a key)
python3 lesson19_bakeoff.py                                          (every brain, 12 tasks)
```

Brains, in the order you build them. Each one is measured on the same 12 bake-off tasks (it never trained on them):

| brain | week | what's new | bake-off |
|---|---|---|---|
| `words` | 5 | one action per command (typos fixed by Lesson 8 in front of it) | 5/12 |
| `tinylm` | 6 | writes whole plans ("put red blue"), asks when you're vague | 8/12 |
| `attention` | 6 stretch | slightly better on new phrasings (held-out 89% -> 92%, average of 3 seeds) | 8/12 |
| `distilled` | 9 | learns new phrasings from a teacher's labels | 10/12 |
| `tinylm-4bit` | 9 | the distilled brain in 4-bit numbers: 1/8 of the size | 10/12 |
| `planner` / `agent` | 10 | Claude, sees the whole room (needs a key; `*-replay` replays recorded runs) | (recorded) |
| `local` | optional | a small model on your own computer via Ollama | |

Bonus (Lesson 20): `python3 lesson20_mcp_server.py` turns the robot into an **MCP server** that Claude Code or Claude Desktop can drive
(Python 3.11+ and `pip install mcp`). Watch it live with `python3 lesson20_watch.py`. Try it without any AI: `--selftest`.

## Bonus: the maths behind robots

`python3 bonus_robot_math.py` uses eight maths ideas on Robo-Helper and prints each before/after:
rotation, Bayes (finding the cat), a Markov chain (a cat with a favourite bed), a Kalman filter (distance while driving),
weighted A*, Fourier (removing wheel wobble), momentum, and exploring in Q-learning. Play with each idea first:
course Module 21 (`topics/21-robot-math.html`) links an interactive explainer for every one.
`python3 bonus_vector_fields.py` steers the robot with a field of arrows (gradient, divergence, curl; course Module 22):
following the gradient alone gets stuck behind a sofa from 9 of 11 starts, adding a swirl reaches the goal from all 11.

## YOUR robot: homework/my_robot.py (you build it)

One file, one gap per week. Every lesson ends with "Add it to your robot": you write the few lines that connect
what you just built to your robot. Until you fill a gap, the robot says "I can't do that yet".

```
cd homework
python3 my_robot.py              (talk to your robot)
python3 my_robot.py --show       (week 16: the capstone show, with a demo, the 12-task exam and your own tests in my_tasks.txt)
cd ..
python3 check.py robot           (checks each piece of YOUR robot)
```

## Your robot's report card

```
python3 progress.py              (what YOUR finished lessons added to the robot, measured)
python3 progress.py --solutions  (the same with every lesson finished)
```

Every lesson must make Robo-Helper better at something you can measure. This shows it.

## The loop for every lesson

1. Read the lesson page in the course (`topics/18-robot-brain/`).
2. Open `homework/lessonNN_*.py` and write the functions marked `TODO`.
3. Run the file to see what it does:  `cd homework` then `python3 lesson01_moving.py`
4. Check your work from the `project` folder:  `python3 check.py 1`
5. Green ✓ = done. Red ✗ = read the hint and try again. Yellow … = not written yet.
6. Do the lesson's **real-world challenge** (away from the screen).

`python3 check.py all` checks everything. The capstone (lesson 11) uses your own earlier lessons,
so if something breaks there, the checker tells you which earlier lesson to fix.

## Rules that make you actually learn

- **Try before you peek.** The struggle is where the learning happens. Use the hints on the lesson page one at a time.
- **Type it yourself.** Don't copy-paste from the solutions.
- **Explain it back.** After each lesson, explain the idea to someone else (or a rubber duck) in two sentences.
- **Break it on purpose.** Change a number and predict what will happen *before* you run it.
