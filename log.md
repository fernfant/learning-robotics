# Log

## [2026-10-21] init | Course created
Set up the folder structure, schema (CLAUDE.md), shared styles and the index.

## [2026-10-21] ingest | How To Use Decision Models for Evals (Hamel Husain & Antaripa Saha)
- Link: https://x.com/HamelHusain/status/2112588257104216294 (X article; full version at hamel.dev/blog/posts/decision-model-evals/)
- Module 01. Not robotics-specific, so it's bridged to perception thresholds, safety stops, calibration in planning and robot-policy evals.

## [2026-10-21] ingest | TensorTonic (tensortonic.com)
- Module 02. ML practice platform, not robotics-specific. Framed as a robotics practice track (maths → geometry/CV → RL ladder → ViT/DDPM → inference) with an interactive 2-link arm transform demo.
- Cross-linked with module 01. Logged gaps for future modules: quaternions/SE(3), kinematics, control, Kalman/SLAM, planning, imitation learning/VLAs, ROS/simulators.

## [2026-10-21] ingest | Linus Ekenstam on gakku: "Don't automate the part where the child learns"
- Link: https://x.com/LinusEkenstam/status/2112526605189054844. Also used gakku.ai's homepage. Couldn't watch the 2:45 demo video.
- Module 03. EdTech post, not robotics. Bridged to HRI: levels of automation, shared autonomy/policy blending, intent inference with goal switching, ask/act/wait, and learning science for the user's own study habits.
- Demo checked in node: with no forgetting and a late switch, α ≥ 0.8 reaches the wrong goal and confidence scaling doesn't fix it. Forgetting does.
- Cross-linked 01↔03 (calibration → arbitration) and 02↔03 (practice habits).

## [2026-10-21] ingest | Maxime Rivest: distil a tiny model from your own logged runs (own-voice-stt)
- Link: https://x.com/MaximeRivest/status/2112156468212289887. Followed through to github.com/MaximeRivest/own-voice-stt (README, evaluation, pitfalls, next-steps). Chart image saved.
- Module 04. First link with direct robotics relevance: on-device models, data flywheels, voice commands and "stop" latency, privileged-teacher distillation in locomotion.
- Numbers come from the repo README tables (459 hand-corrected clips). Chart values are described approximately.
- Cross-linked with 01 (evaluation, Pareto), 02 (inference engineering), 03 (voice/HRI).

## [2026-10-21] ingest | @antiAIvo quoting Philip Kiely (Baseten): width / depth / length at trillion scale (Kimi K3)
- Link: https://x.com/antiAIvo/status/2112510656037761095 (Chinese). Quotes https://x.com/philipkiely/status/2112272656217297224, which has a 1h video I couldn't watch.
- Technical content comes from the primary source: the Kimi K3 README and tech report (github.com/MoonshotAI/Kimi-K3), saved in sources/. Baseten serving figures come from baseten.co/library/kimi-k3.
- Module 05. Flagged that the post maps AttnRes to "length", while the report maps it to depth. Followed the report.
- Robotics bridge: VLA backbones, fixed-size recurrent memory for streaming sensors (delta rule ≈ online least squares, as an analogy), MoE for multi-skill/multi-embodiment.
- QB demo checked in node: max/target load 3.19× → 1.44× in 2 QB steps; fixed step ~10 steps and oscillates.

## [2026-10-21] ingest | 30u30: Ilya Sutskever's 30 foundational papers (github.com/Ojhaharsh/30u30)
- Module 06 is a folder: hub (topics/06-30u30/index.html, with a progress tracker and a 12-day robotics fast track) plus 30 paper pages. Manifest in topics/06-30u30/papers.txt.
- The repo is CC BY-NC-ND, so pages are written from the original papers and link to the repo for code and exercises. Repo README saved in sources/.
- Written by 5 parallel agents from the Day 01 template. Each demo was checked with node --check plus a headless run of its maths.
- Notable corrections from fact-checking: Transformer EN-FR BLEU 41.8 (abstract/Table 2); AlexNet input is 227 in practice; RLHF backflip = 900 queries (not bits); the 2017 RLHF paper used TRPO/A2C, not PPO; the 30u30 Day 16 README mixes in Pointer Network results, and the page follows the Order Matters paper.
- User request: make every day easy for a 13-year-old. Added a "Start here (no maths needed)" box to all 30 days and the hub. Convention recorded in CLAUDE.md.
- Final check: 30/30 pages have balanced tags, exactly one kid block before Summary, resolving links, a correct prev/next chain and valid JS.

## [2026-10-21] ingest | Dongxi (东锡): "After pre-training, why post-train?" (X article, Chinese)
- Link: https://x.com/dongxi_nlp/status/2112767071926792566. Article text saved as sources/07-dongxi-post-training.md and .json (images had captions only).
- Module 07. Pre-training vs post-training; the three teachers (SFT demonstration, preference comparison with a KL leash, RLVR checker). Robotics mapping: behaviour cloning, human-ranked rollouts, success detectors, trust regions.
- First module written with the Start-here box from the start (CLAUDE.md convention).
- The "500 safety examples" study is attributed to the article; I didn't name a paper I couldn't confirm.
- Demo π* ∝ π_ref·exp(r/β) checked in node: RM score rises monotonically 0.87 → 3.20 as β falls, the true human score peaks at ~6.4 near β≈1–2 then falls to 3.0 (reward hacking).
- Cross-linked with 01 (reward models and detectors as classifiers), 05 (K3 post-training), 06 Days 29–30.

## [2026-10-21] restructure | Course is now two-track: LLMs & Robotics
- User: the course covers both LLMs and robotics. Renamed the course to "LLMs & Robotics" (the folder name is unchanged).
- Track badges (LLM / Robotics / LLM + Robotics) on every module, every 30u30 day and the index cards. The summaries table got a Track column.
- Retitled modules 01, 02, 03, 04, 05, 06 and 07 so each title names its domain. Replaced "Heads-up: not robotics" notes with track notes.
- Module 06 hub: added an LLM fast track next to the robotics one.
- CLAUDE.md step 4 now assigns a track instead of treating LLM content as off-topic.

## [2026-10-21] ingest | Suraj Sharma: AI Research Engineering roadmap (12 stages)
- Link: https://x.com/suraj_sharma14/status/2112876560629825734. Saved as sources/08-suraj-ai-research-engineer.{md,json}.
- Module 08 (LLM track) is a folder: hub with a reality check on the hype claims, a progress tracker, a suggested order and a map to earlier modules. One page per stage is in progress.
- First batch of stage agents (3 × 4 stages) all stalled with nothing written. Relaunched as 6 × 2 stages with fetch timeouts and one-write-per-page rules.

## [2026-10-22] add | Module 08: real courses and content mapped to each stage
- User asked to map the stages to actual courses. Built topics/08-ai-research-engineer/courses.json (62 resources; every URL checked for HTTP 200 on 2026-10-22; two dead links replaced: the PyTorch custom-autograd tutorial → the "Extending PyTorch" notes, cs231n.stanford.edu → cs231n.github.io).
- Hub: a "Courses & content" section with spine courses (CS336, Karpathy, HF LLM/smol courses, Ultra-Scale Playbook, How To Scale Your Model, MIT 6.5940, ARENA, AI Evals, HF Robotics course) and per-stage tables. Stage pages render the same list.
- CS336 assignment topics confirmed from the course site (A1 basics, A2 systems/Triton FlashAttention2 + distributed, A3 scaling, A4 data, A5 alignment/reasoning RL).

## [2026-10-22] complete | Module 08: 12 stage pages
- Written by 6 agents (2 stages each) after the first batch stalled. Each page has a Start-here box, concepts, a laptop-sized project plus the full version, a reality check, in-course links, a robotics box, a self-check, Courses & content (from courses.json) and papers.
- Demos, each verified headlessly in node: tensor strides/contiguity (01); Chinchilla calculator, 20 tok/param rule vs the parametric fit E=1.69, A=406.4, B=410.7, α=0.34, β=0.28 (02); Switch load-balancing loss + capacity drops (03); rejection-sampling yield vs verifier TPR/FPR (04); DPO vs KTO loss/gradient (05); ZeRO memory calculator reproducing the paper's 7.5B/64-GPU figures (06); vision-token budget (07); MHA/GQA/MQA KV-cache calculator (08); toy logit lens + activation patching (09); n-gram contamination checker (10); paired bootstrap (11); best-of-N selection bias (12).
- Corrections and checks: Stage 09 corrects the post's "single attention head" framing (ROME: mid-layer MLPs at the last subject token); π0 prefix-KV reuse attributed to the paper; the LLaVA-1.5 "~1 day on one 8×A100 node" figure confirmed from the abstract; red-teaming content limited to sandboxed testing of your own classifier, with no attack prompts.
- Full check: 12/12 pages pass tags, ids, links (incl. anchors), kid block, track badge, all mapped course URLs present, pager chain and JS.

## [2026-10-24] ingest | Vishal Singh: 25 AI inference engineering interview problems
- Link: https://x.com/vishalsingh2972/status/2113830444722741637. Saved as sources/09-vishal-inference-25.{md,json}.
- Module 09 (LLM track) is a folder: hub (Start-here box, progress tracker, 24-hour prep plan, links to earlier modules) plus 10 themed pages covering all 25 problems (manifest pages.txt). Pages are being written by 5 agents from a brief requiring worked arithmetic, labelled assumptions, NVIDIA-sourced GPU specs, a model interview answer and a verified demo per page.

## [2026-10-24] ingest | Yacine Mahdid: Prime Agent, a self-improving RLM harness (video with Seth Karten)
- Link: https://x.com/yacinelearning/status/2113688068352004435 (a thumbnail of a 2h36m YouTube video I couldn't watch). Built from primary sources instead: Prime Agent paper (arXiv 2608.23552), repo README, launch post; RLM paper (arXiv 2512.24601) and blogs; Continual Harness paper (arXiv 2605.09998). Saved in sources/10-*.
- Module 10 (LLM + Robotics): RLM (prompt-as-a-variable, recursive sub-calls), Continual Harness H=(ρ,G,K,M) with reset-free refinement (from Gemini Plays Pokémon), Prime Agent architecture, results with critical reading notes, safety bounds (not a sandbox, bounded autonomy, immutable base prompt, rollback).
- Demo: recursion-tree cost, exact arithmetic checked in node (e.g. 2M tokens / 128k window → 16 sub-calls, root reads 8k; 100M / 16k window → 5 levels).
- Cross-linked with 05 (architectural vs scaffolding long context), 06 Day 17 (NTM external memory), 03, 04, 07, 08 Stage 10.

## [2026-10-24] complete | Module 09: 10 pages covering all 25 inference problems
- Written by 5 agents (2 pages each). Each problem has its own section (id pN): what's tested, concepts, a worked answer with real numbers and labelled assumptions, trade-offs, a model interview answer, common mistakes. Plus practise-it, robotics box, self-check, resources (links checked for 200).
- GPU specs from NVIDIA pages, with form factor named: H100 SXM 80 GB / 3.35 TB/s; H100 NVL 94 GB / 3.9 TB/s; H200 141 GB / 4.8 TB/s; B200 per-GPU derived from DGX/HGX totals (180 GB, 8 TB/s, labelled as derived); L40S 48 GB / 864 GB/s; Jetson AGX Orin 64GB 204.8 GB/s. Headline TFLOPS are with sparsity, so they're halved for dense use.
- Spot-checked: 70B GQA KV = 160 KiB/token FP8 (327,680 B BF16) → 500 GiB at 32K×100; H100 roofline ridge ≈ 295 FLOP/B; spec-decode α=0.8, k=4 → 3.36 tokens/verify.
- Demos (all verified headlessly): request timeline, KV sizer + paging, batching simulator, prefix-cache routing simulator, spec-decode speedup, fit/bandwidth/cost calculator, roofline, percentile explorer, autoscaling simulator, 1M-DAU capacity and cost estimator (prices and throughput as assumption sliders).
- Full check: 10/10 pages pass tags, ids, kid block, track badge, all problem sections present, links and anchors, pager chain, JS.

## [2026-10-26] ingest | Dongxi (东锡): "What should young people do in the AI era?" (X post, Chinese)
- Link: https://x.com/dongxi_nlp/status/2114597689228698006. Four keywords: Stanford CS336; Raschka, Build a Reasoning Model (From Scratch); Lambert, RLHF Book; 谭成义三分化 (identified by search as a push/pull/legs strength-training series by 凯圣王 × 谭成义 on Bilibili).
- Module 11 (LLM): study stack with chapter lists (from the rasbt/reasoning-from-scratch README and rlhfbook.com), CS336 assignments, a combined order, a chapter-to-module map, and a time planner where every hour estimate is a labelled assumption. Raschka's site returned 406 to curl, so the page links the GitHub repo and video course.

## [2026-10-26] add | sources.html: sources & summaries page
- User asked for an index and a summary page listing all sources. index.html already lists modules and summaries. Added sources.html, generated by tools/build_sources.py: per module, the link sent, author, date, type, summary (from the index table), primary sources followed, saved files, and all external references auto-extracted from the module's pages (382 unique). Linked from the index header. CLAUDE.md step 8 says to regenerate it after each ingest.

## [2026-10-31] ingest | Jia-Bin Huang: "AI Training and Inference" YouTube playlist (9 videos)
- Link: https://www.youtube.com/playlist?list=PLXrQ2OzD3YKA. Video list, descriptions, chapter lists and references saved in sources/12-jiabin-huang-playlist.json (captions were not retrievable; videos not watched).
- Module 12 (LLM + Robotics): hub with a suggested learning order, total runtime 3h50m and a tracker, plus 9 watch guides (embedded player, timestamped chapter guide, ideas from original papers, links to deeper course pages, robotics box, self-check, references checked for 200, verified demo). Written by 3 agents; two were cut off by a network error and resumed.
- Corrections: video 08's description links "Fantastic Pretraining Optimizers" to the wrong arXiv ID (the guide cites 2509.02046). Module 05 lacked the Per-Head Muon detail the brief assumed, so I added a short aside from K3 report §2.5 (anchor #muon).

## [2026-10-31] ingest | Pavel Simo: 100-days-of-inference-engineering (GitHub journal)
- Module 13 (LLM): book map (Kiely's Inference Engineering, 8 chapters → course pages), journal Days 1–2 summarised (no licence, so not copied), a 100-day plan with one build per chapter, and a clickable 100-day tracker.

## [2026-10-31] ingest | Deep-ML Deep-Path placement test
- Link: https://www.deep-ml.com/deep-path/diagnostic (needs sign-in, so the test wasn't taken). The map was rendered in the built-in browser: 103 concepts, 14 parts, 5 depth zones. Saved as sources/14-deep-ml-deep-path.json.
- Module 14 (LLM + Robotics): route, crosswalk of the 14 parts to course pages (all 103 concepts listed), comparison with TensorTonic and 30u30, and my own 25-question self-placement check (answer key and frontier logic verified in node). Gaps noted: ML compilers; robotics and control (1 concept).

## [2026-11-03] ingest | inferenceengineering.tech (interactive companion to Kiely's book)
- Module 15 (LLM): what's on the site (8 chapters, 3 paths, 7 calculators, cheat sheets, glossary, benchmark), chapter-by-chapter pairing with modules 05/08/09/12/13, and a critical read of its vLLM vs SGLang benchmark (inconsistent dates; one 8B model on 2× H100 TP=2; the winner varies by workload). Official status not confirmable from Baseten's side, so stated as such. The "Free PDF" isn't linked. Module 13 now points to it.

## [2026-11-03] fix | duplicate IDs
- A full-course check found heading/demo ID collisions in modules 11 and 12. In 11 the planner canvas lost to the h2 "plan", so the planner wasn't drawing; renamed it to "planner". In 12 the heading IDs were renamed to sec-*. Final check: 78 pages, no tag, ID, link, in-page anchor or JS problems.

## [2026-11-04] ingest | orca3/llm-model-inference: companion code for "Hands-On LLM Serving and Optimization" (Chi Wang & Peiheng Hu, O'Reilly)
- Link: https://github.com/orca3/llm-model-inference. README, ch09 guide and ch03 server README saved in sources/16-*. No licence file, so summarised and linked only.
- Module 16 (LLM): the book's 10 chapters mapped to course pages; an 8-lab track built from the repo folders with hardware notes; a walkthrough of the from-scratch server's layers; the ch09 Qwen3-14B case study as a method; a comparison with Kiely's book (13/15); practical gotchas (vLLM v0.6.0 pin, inconsistent ShareGPT size in the guide, Git LFS, billable AWS labs); robotics (edge paradigm, llama.cpp, multi-LoRA, serving inside RL).
- Demo: dynamic batching (max wait / max batch) simulator, checked in node. At 40 req/s, batch size 1 overloads (service limit ≈29 req/s with 30+4 ms), batch 8 brings mean latency to ~55 ms, and a longer wait grows the batch and the latency.
- Cross-linked with 13 (labs as the 100-day "build") and 15.

## [2026-11-04] ingest | shikamaru: "The Ultimate Free AI Curriculum That Replaces Your Degree" (X article)
- Link: https://x.com/shikamarutsai/status/2088918066310652358. Parsed into 391 courses in 14 categories with 775 links (733 unique). Saved as sources/17-*.
- Provenance: the article reproduces kmario23/deep-learning-drizzle (its "Go to Contents" links point there, and the repo's To-Do list is copied word for word) without credit. Module credits the original. The repo has no licence file.
- Link health (4 Nov 2026): HTTP check of all 733 unique links, plus YouTube oEmbed for 328 videos and playlists. A first content-regex YouTube check gave false positives (346/347 "unavailable"); discarded and redone with oEmbed. Result: 610 working, 87 dead, 6 removed videos, 16 restricted (private or non-embeddable), 14 blocked to scripts. 381/391 courses still have a working link.
- Module 17 (LLM + Robotics): searchable catalog (category / year / text / working-only), reality check (newest course 2022), 2026 updates per category, and a robotics section (Modern Robotics, MIT Manipulation, MIT Underactuated, CS285, HF Robotics + LeRobot, MuJoCo, Isaac Lab; all 200). Catalog filter fixed so the 2 undated courses show (391/391).

## [2026-11-04] create | Module 18: Build a Robot Brain (our own 12-week course)
- Written for a 15-year-old with basic Python, from everything in modules 01–17. One lesson a week for 12 weeks, covering robot basics and inference engineering. Each lesson builds its idea from first principles and has a browser demo checked against the Python, homework marked by `check.py`, hint ladders and a real-world challenge.
- Project `topics/18-robot-brain/project/` (standard library only): `solutions/` with BEGIN/END SOLUTION markers, `make_starters.py` → `homework/`, and `check.py` with 84 checks, all passing on the solutions. Includes `sim.py` (a simulator recording a frame per move, plus tools for agents) and `brains.py` (word counter, tiny neural LM, local Ollama, Claude planner, Claude tool-using agent, and replays of recorded runs).
- Weeks: 1–4 move/sense/learn/neuron/test/A*; 5–6 words, a classifier, a tiny LM from zero; 7 safety layer + capstone; 8 latency/p95/TTFT/tokens/cost; 9 caching/quantising/distilling + LoRA; 10 Claude as planner and as agent (with validate_plan / execute_tool); 11 bake-off (12 tasks, scorecard, replay viewer); 12 RLHF by hand + going real. Q-learning is a bonus.
- Honest numbers:
  - Capstone 83%. Exact bin-set checking exposed "find the green block" binning the block.
  - Bake-off: the word counter scores 5/12, the tiny LM 4/12. The tiny LM bins blue when asked for purple.
  - 4-bit quantisation keeps 100% at 1/8 the size; 2-bit drops to 75%.
  - Distilling from a weak teacher drops the hard set from 83% to 67%; a careful teacher gets 100%.
- Pending: real Claude runs are not recorded yet (they need the user's API key). The pages mark where results go with `<!-- CLAUDE-RESULTS -->`, and no Claude numbers are invented.

## [2026-11-04] enhance | Module 18: attention, an AI model as judge, MCP (prompted by backprop.site/learning-ai)
- Source: https://backprop.site/learning-ai, a free AI-engineer roadmap that collects external links (81 topics, 16 modules). We used it as a gap check against our course and didn't copy any of its content.
- Attention (week 6 stretch, `lesson15_attention.py`, `check.py 15a`):
  - The query is the word just written, scores are dot product ÷ √E, softmax gives the weights, and the context is the weighted average. Backprop through attention is written by hand and matches a numerical gradient check.
  - Real effect: with the colour buried in filler words, colour accuracy (average of 3 seeds) is 81/89 at 6 filler words, 67/78 at 10 and 74/81 at 14 (averaging vs attention).
  - It doesn't fix word order (no positions) or unknown words.
- AI model as judge (week 11 stretch, `lesson19_judge.py`, `check.py 19a`): a reply-only rule judge agrees with the exact checks 58% of the time on the word counter and 33% on the tiny LM, fooled by confident replies. The Claude judge (reply-only vs with-evidence) is pending recording.
- MCP (bonus lesson 20, `lesson20_mcp_server.py` + `lesson20_watch.py`): built on the official MCP Python SDK 2.3.0 (`mcp.server.MCPServer`; `ToolError` keeps the refusal reason). Tested end to end with the SDK's stdio `Client`: 5 tools discovered, calls work, and guard() refusals reach the client with their reason. Stretch: reset_room skips guard (find the hole).
- check.py: 94/94 on the solutions. 22 pages validated.

## [2026-11-05] ingest | Sergii Makarevych: "Evals: how to know whether an AI system actually works" (X article)
- Link: https://x.com/sermakarevich/status/2106453816757354947 (3 Oct 2026). Raw saved as `sources/19-makarevych-evals.json` (fxtwitter, 310 article blocks).
- Module 19 (LLM): `topics/19-evals-field-guide.html`. Start-here box, then the loop (input, system, grader, number), error analysis, code graders, AI judges and how to check them (kappa 0.15 at 60% agreement vs 57% for "always pass"), the five judge biases and GAUGE (evidence beats judge strength), panels, detectors and typed judges, error bars and paired comparisons (60 cases ≈ 12-point floor), RAG and agent grading (pass^k, cost per success), reward hacking, benchmarks, and the weekly cadence.
- Demos: judge quality (kappa, catch rate vs the "always pass" baseline), error-bar width vs number of cases, pass@k vs pass^k. Checked in node against the article's numbers (kappa 0.155, ±11.6 at n=60, pass^3 at 0.9 = 0.729).
- Caveats on the page: the running-example numbers come from the author's tutorial, which isn't publicly linked, and many of the cited 2026 papers are arXiv preprints we haven't checked independently.
- Applied to Module 18 (week 11, stretch 2): `lesson19_judge.py` gains `kappa`, `catch_rate` and `bootstrap_ci` as homework, and `check.py 19a` goes from 3 to 6 checks (97/97 in total). Real output: the rule judge scores kappa 0.21 on the word counter (caught 3/7) and 0.00 on the tiny LM (it passed all 12 runs). Bake-off error bars: words 5/12 [17%, 67%], tinylm 4/12 [8%, 58%]; paired difference +8 [+0, +25], since they differ on only one task. Corrected the page's "worse than a coin" claim: the right baseline is "always pass", not a coin. The judge demo now shows kappa (JS matches the Python).
- Cross-links: 01 ↔ 19, 04 ↔ 19, 18 (hub + week 11) ↔ 19.

## [2026-11-09] enhance | Module 18: every lesson makes the robot measurably better (rebuild of the mini-LLM weeks)
- Prompted by the user: "ensure that each lesson is building towards better function of the robot in a practical and real way, including the lessons on the mini LLMs".
- Audit first, with real numbers: the old tiny LM, which wrote a single action, scored 4/12, worse than the word counter's 5/12. The attention, distilled and 4-bit brains weren't plugged into the robot at all.
- Lesson 8: the bigram model's first job on the robot is a typo fixer. New homework: `edits1`, `fix_word`, `fix_typos`, plus `TYPO_COMMANDS`, which includes one deliberate failure. Fixes 8 of 9. `brains.clean()` runs it in front of the small brains. Typo commands handled the same as the correct spelling: 6/9 → 9/9.
- Lesson 15: the tiny LM now writes plans: `put red blue`, `ask` or `none`, up to 5 words. New homework: `words_to_plan`, `plan_examples`.
  - Synthetic training data comes from templates. An earlier prototype with about 66 hand-written examples got only 20–40% of held-out plans right.
  - The 12 bake-off commands are removed from the training data, leaving 343 examples. A page helper caught 3 that had leaked in; they were fixed in code and every number was re-measured.
  - Held-out plans: 92%. Bake-off: 5 → 8/12.
- Attention stretch: over 3 seeds, held-out plans go 89% → 92%, and the bake-off is unchanged at 8/12. The old claim that attention handles filler words better didn't hold with the new data, so it's removed from the page.
- Lesson 17: the student is now the attention model (it falls back to the plain tiny LM if the stretch isn't done) and gets a robot column.
  - Distilling from a careful teacher: 10/12. Distilling from the word counter as teacher: no gain.
  - Quantising: 8-bit and 4-bit keep 8/12; 3-bit drops to 7/12; 2-bit to 4/12.
  - New brains: `attention`, `distilled` (10/12) and `tinylm-4bit` (10/12, 1,411 bytes vs 11,288).
- Lesson 19: bake-off ladder 5 / 8 / 8 / 10 / 10. Judge results: kappa 0.21 / 0.14 / −0.12. Paired comparisons: tiny LM vs word counter is too close to call (+25 [+0, +50]); distilled vs word counter is a real difference (+42 [+17, +67]).
- New `project/progress.py`, the robot's report card. One row per lesson, each measured with the learner's own code; rows not yet built say so. It has its own copy of the bake-off check, so early weeks work. Tested on the solutions (18 of 19 working; week 10 needs the Claude recordings), on blank homework, and on a simulated week-8 state.
- Fixed learning-order bugs found by a page helper: in the homework, lesson16 and lesson17 used brains or checks from later weeks. check.py: 100/100.
- Pages 08, 15, 16, 17 and 19 were rewritten from real runs, and their demos were re-verified in node. Also updated: the hub (new "report card" section), the README, lessons.txt and Module 19's Robo-Helper numbers.

## [2026-11-09] ingest | Six from-scratch repos: micrograd, minGPT, nanoGPT, llm.c, tinygrad, minimalRL
- The user sent 6 GitHub links, all MIT licensed. READMEs (plus nanochat's) are saved as `sources/20-*-readme.md`.
- Module 20 (LLM + Robotics) is a multi-part module, `topics/20-from-scratch/`: a hub plus 6 pages. The user approved cloning and running the code on the Mac in a scratch venv.
- Every page has a tested "Run it" section and an experiment that tries to make Robo-Helper better, measured in the simulator:
  - micrograd: gradients match our hand-derived ones; the MLP helps only on a curved braking case (7 vs 17 missed stops).
  - minGPT: 7–8/12, too little data.
  - nanoGPT: 9/12, and 10/12 with teacher labels, equal to distilled; 100% vs 52% on colours buried in filler.
  - llm.c: GPT-2 (124M) takes 245–323 ms per decision on CPU, over the 0.2 s budget.
  - tinygrad: same plans; slower one at a time, 76–333× faster in batches of 4,096.
  - minimalRL: DQN vs A*; DQN fails when the cat moves.
- Fixes recorded:
  - gym 0.26.2 is broken on numpy 2, so we used gymnasium.
  - tinygrad needs `HCQ_RUNTIME_DEV=CPU:CLANG` without Homebrew LLVM.
  - llm.c on macOS has no OpenMP; built with NO_OMP or the libomp copy from the torch wheel.
  - minGPT is missing its regex and requests dependencies.
- The pages that measured against the first version of the training data carry a dated note.
- Verified: openpilot ships tinygrad models.

## [2026-11-09] ingest | Martin (@0x_meden): "Learn the math behind robots by playing with it" (X post) + his π0/GR00T guide
- Link: https://x.com/0x_meden/status/2119507343348212198 (8 Nov 2026). It lists 10 interactive explainers and quotes the author's X article "How π0, GR00T and Optimus actually think" (5 Nov 2026). Both saved as `sources/21-meden-*.json`. All 10 explainer links returned HTTP 200 on 9 Nov 2026.
- Module 21 (LLM + Robotics), `topics/21-robot-math.html`. Each section has: Play (what to try), the idea in plain words, the Robo-Helper lesson that uses it, real output from a tested experiment, and a challenge. Also included: an interactive Kalman demo (checked in node: at speed 0 the average matches Kalman, at 1 m/s the average is worse than the raw readings) and a summary of the π0/GR00T guide with its figures attributed.
- New `project/solutions/bonus_robot_math.py`, standard library only, runs in under 1 s. Results:
  - rotation: (2, 0) at 90° → (4, 5)
  - Bayes cat search: 50% → 92% → 100% after 1, 4 and 16 readings
  - Markov cat with a favourite bed: run-ins 0.83 → 0.06 per trip for +2 steps. The first version, a cat with no habits, gave no gain; recorded on the page.
  - Kalman: error 0.56 / 0.54 → 0.22 m
  - weighted A*: 40 / 35 → 13 squares searched, same 11-step path
  - Fourier wobble removal: 0.44 → 0.11 m
  - momentum: 73 → 35 steps, while 0.9 overshoots and lr 0.3 alone takes 24
  - Q-learning: epsilon 0 learns fastest in the tiny maze (optimistic starting values)
- Diffusion has no experiment, and the page says so. It ties action chunks to week 6's plan-writing tiny LM.

## [2026-11-09] ingest | Matheorems: "Gradient, Divergence and Curl" (X post with an animation)
- Link: https://x.com/matheorems/status/2119505986381901899 (8 Nov 2026). Saved as `sources/22-matheorems.json`, which stays local (third-party copy).
- Module 22 (LLM + Robotics), `topics/22-vector-fields.html`: a kid box, then the three examples from the post explained and checked numerically, then the robot.
- New `project/solutions/bonus_vector_fields.py` (standard library only):
  - Numerical gradient, divergence and curl reproduce all 6 values in the post.
  - Potential-field robot: Khatib-style attract and repel fields, plus a curl "swirl" (the repel field rotated 90°).
  - One box: gradient alone reaches the goal from 10/11 starts (9.1 m); with swirl, 11/11 (10.0 m).
  - A sofa wall: gradient alone reaches 2/11 (9.8 m); with swirl, 11/11 (11.2 m). Straight line is 8 m.
- Interactive demo of the fields and robot runs. Checked in node: identical counts and average lengths to the Python.
- Fix, course-wide: `style.css` had no `pre` rule, so long output lines made pages wider than the screen. Added `pre { overflow-x: auto; max-width: 100%; }`. Module 22 checked in the browser: page width now equals the viewport.

## [2026-11-10] enhance | Module 18 for a 12-year-old: a clear path, and one robot that grows every week
- An independent "12-year-old" review found the home page hid the course: it was the 18th card, labelled "ages 15+". It also found that from week 6, lessons referred forward to things not yet built, contradicted each other (week 10 said the tiny LM can't do two blocks), and piled up adult jargon.
- Fixes:
  - home: a start-here banner (Module 18, then 21 and 22 after week 4, then 20 after the course)
  - "ages 12+" with honest weekly timing and install notes
  - every lesson opens with a "Step N of 21 · so far your robot… · today… · next…" strip, plus "ask an adult today" notes (00, 14, 18, 20)
  - pagers labelled by week and topic
  - forward references removed, bridges added at the jumps, hard kid boxes simplified (grade 3–5)
- New `project/my_robot.py`: the learner's own named robot, built only from the lessons they've finished.
  - It detects each ability by running their code: moves, senses, brakes, stops, routes, typos, words, plans, safety, the whole RoboHelper with its test score, speed, teacher, Claude (with a key), exam, taste.
  - Commands: arrows, `look`, `goto`, sentences, `exam`, `claude:`, with an animated room.
  - Tested by simulating homework at weeks 1, 3, 4, 5, 6 and 7. Week 1 bumps the cat, week 3 stops in time, week 4 replans, week 5 bins one block only, week 6 bins both, week 7 shows its capstone score (83%).
  - `--show` is the week-12 capstone: a demo of every ability, then the 12-task exam (10/12), then the learner's own tests from `my_tasks.txt` (example provided). About 10 s.
- Pages: hub ("Your robot, week by week" table with real output), each lesson's strip (a "try this on your robot" line), Lesson 11 (your assembled robot's score), Lesson 14 (the capstone show, with real output). README updated. check.py 100/100; 112 pages validated.

## [2026-11-10] enhance | Module 18: the learner builds their own robot, one gap a week
- The user asked whether a 12-year-old would really feel they're building something step by step. Honest answer: no. They filled in functions in separate files, and the robot was put together for them (except in the week-7 capstone).
- `my_robot.py` is now the learner's own file: `homework/my_robot.py`, with the worked version in `solutions/`.
  - It starts with the robot's name, the room and the provided glue (drawing, typing loop, showcase).
  - It has one gap per week, 13 methods in all: arrows (1), look (2), should_stop_for (3), route + goto (4), clean + understand_words + do (5), understand_plans (6), is_safe (7), think_time (8), teacher_brain (9), ask_claude (10, optional), exam (11), nicest_route (12).
  - Each gap is written in simple code that calls the learner's lesson functions.
  - Until a gap is filled, the robot says "I can't do that yet: week N". Built pieces are detected from the source (the TODO is gone).
- `make_starters.py` turns `# BEGIN ROBOT week=N lessons=X` blocks into TODO gaps and copies `my_tasks_example.txt`.
- `check.py robot` drives the learner's robot, with 12 week-labelled checks (112/112 on the solutions; 0/12 on blank homework).
- Tested by building the kid's file with gaps filled up to each week. Robot checks passed: week 1 → 1, week 3 → 3, week 4 → 4, week 5 → 6, week 6 → 7, week 7 → 8, week 9 → 10. Behaviour week by week:
  - week 1 bumps into the cat
  - week 3 stops for it
  - week 4 goes round it
  - week 5 puts away one block
  - week 6 puts away both
  - week 7 shows the capstone score
  - week 8 reports its thinking time
  - week 9 understands "where's"
- `--show` (the week-12 capstone) scores 10/12 on the exam and 6/6 on the example tests.
- Pages:
  - every lesson has an "Add it to your robot" section: the task, a hint ladder, its check name, real output
  - the journey strips link to it
  - the hub section is rewritten ("Your robot, built by you")
  - Lesson 11 explains its capstone is the same robot, written as a class
  - Lesson 14's show uses `homework/my_tasks.txt`
  - README updated
- Also: the course home page exported as a PDF for the user, via headless Chrome, outside the repo.

## [2026-11-10] fix | Everything the three persona swarms found (Maya the careful reader, Leo the impatient gamer, Sam the builder)
- Reviews: `kid-reviews.md` (101 issues) and `kid-review-summary.md` (top 10, quick wins, builder bugs). Both are kept outside the repo.
- Code, all tested at every week's state:
  - Lowercase arrows work. A friendly crash message names the method and line.
  - Before week 7, bad or unknown actions give an "Uh oh … week 7's safety check" message.
  - Unknown intents raise ValueError in `do()`. Bonk shows the position.
  - Week 2 `look` averages 16 noisy readings.
  - Week 3 shows the stop chance and threshold.
  - `json:` command, so week 7's safety check is visible.
  - `slowbrain on` really bumps the cat. Week 8 `think_time` flags when it's too slow, using `fits_budget`.
  - Week-12 boss gap `see_and_plan`: the exam goes 10/12 → 12/12.
  - The banner greets via `introduce()`, uses weeks only, and skips the optional week-10 Claude piece.
  - The showcase opens with the banner and ends with an "N of 14 pieces built" certificate.
  - `check.py`:
    - new robot checks: lowercase, the averaged look, safe speed (Part B, yellow), safest threshold (week 3 Part B), json refusal, the boss;
    - a friendly TypeError hint;
    - the L11 check now requires the find-the-green-block failure (`==`, not `<=`);
    - clearer lesson-15 wording.
  - Starter TODOs say "week N".
  - Totals: 115/115 on the solutions. The robot passes 0, 1, 3, 5, 6, 8, 9, 10, 11, 12, 13, 15 of 15 checks after weeks 0–9, 11 and 12.
- Pages, done by 5 helpers with separate file ownership and then a consistency pass:
  - Home page: a hero "Start the course" box, with the grown-up modules collapsed.
  - Hub: weeks 1A–12B and a week-by-week robot table from real runs.
  - Every lesson:
    - "Week N of 12 · Part A/B" numbering, with lesson numbers only as file names;
    - "Add it to your robot" sections where Hint 1 gives the exact import line and the last hint is fill-in-the-blank;
    - "New Python this time" boxes;
    - "On your own" challenge versions;
    - changelog notes removed;
    - false promises of recorded Claude runs removed;
    - real outputs everywhere.
  - Lesson 0: a drive-the-robot warm-up and a "How your robot file works" box.
  - Lesson 15 split: the attention stretch moved to new `15b-attention.html`.
  - L11: hints now consistent (`==`), and RoboHelper explained as the simpler twin.
  - L18: fixed the Hint 3 truthy-tuple bug.
  - L14: the boss section, plus a finale around the learner's own `--show` reaching 12/12.
  - Quick wins all applied.
- Not done (needs the user's API key): recorded Claude runs. The pages say Claude's rows appear after a grown-up records them.

## [2026-11-10] review | Visual, intuition-first pass on Robot Brain
- Asked for: every concept explained with an everyday idea and a picture before any code, code only as clear practical steps, readable room pictures (not character drawings), colour, concise pages, and a checkpoint after every step.
- Four reviewers read all 28 Module 18 pages as a 12-year-old (most at phone width in the browser). Verdict: "mostly", with about 20 ranked fixes.
- A builder did weeks 3, 6, 9, 11 and 12 for real. Every checkpoint matched except two:
  - week 6: an invented closing line;
  - week 11: the cat swap was missing from the robot snippet.
  Both are fixed.
- Fixes:
  - Old letter-sprite canvases (weeks 1–2) redrawn in the room.js style.
  - New pictures:
    - moving average, magnitude triangle and three-phone real tilts (21);
    - gradient tilt/lift and MSE squares (03);
    - train/test drawer (05);
    - BFS vs A* shaded rooms (06);
    - sampling strip, nested-dictionary boxes and the "cat" edits (08);
    - safe_parse flow (10);
    - failure score bars (11);
    - route-Q room and S-curve (12);
    - compass short/long way and x/y split (23);
    - failure-to-week chips (19).
  - Formulas moved out of the 💡 boxes and into the 🛠 steps.
  - New checkpoints on 08 (one per function), 12, 14 (README) and 19.
  - New `box world` (🌍) and `box safety` (⚠️) styles.
  - Transcripts wrap on phones.
  - SVG labels are at least 12px at 375px.
- Checks: validator 120 pages, 0 problems. `check.py`: 147/147 on the solutions, robot 21/21. `_kit-test.html` deleted.
