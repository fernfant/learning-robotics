# LLMs & Robotics: a personal course

A self-paced course on large language models and robotics. It's built from links I collected, each turned into a module with plain-language summaries, deep dives, interactive demos and a "Start here" box written for a teenager.

**Browse it:** https://fernfant.github.io/learning-robotics/

## What's inside

- **21 modules** (`topics/`): LLM evals, inference engineering, post-training, Ilya's 30 papers, robotics maths, and more. Each module is marked LLM, Robotics, or LLM + Robotics.
- **Module 18, "Build a Robot Brain"** (`topics/18-robot-brain/`): our own 16-week, hands-on course (robot body with real sensor data, and robot brain) for ages 12+ with basic Python. **New here? Start with this one.**
  - You build **Robo-Helper**, a simulated robot, using only the Python standard library.
  - Homework is in `project/homework/`, worked answers in `project/solutions/`, and `check.py` marks it (100 checks).
  - `progress.py` shows what each lesson added to the robot, measured.
- **Module 20**: six from-scratch repos (micrograd, minGPT, nanoGPT, llm.c, tinygrad, minimalRL), each run and tested on a Mac.
- **Module 21**: ten interactive maths explainers, each one applied to Robo-Helper.

## Run it locally

```
python3 -m http.server 8020        # then open http://localhost:8020
cd topics/18-robot-brain/project && python3 check.py all --solutions
```

## Sources and credits

Every module credits its source at the top of the page. [`sources.html`](sources.html) lists every link, author, date and primary source. The course pages summarise and link to the originals; they don't republish them.

- The raw copies I saved while building the course (articles, posts, PDFs, READMEs) are **not** in this repo, except the MIT-licensed READMEs of the Module 20 repos (`sources/20-*-readme.md`, © their authors, MIT licence).
- Module 06 is written from the original papers, because its companion repo (Ojhaharsh/30u30) is CC BY-NC-ND. It links to that repo and doesn't copy it.
- Short code excerpts from MIT-licensed repos (Module 20) are quoted with credit.
- The interactive explainers in Module 21 belong to their authors and are linked, not copied.

If you're an author and would like something changed, please open an issue.
