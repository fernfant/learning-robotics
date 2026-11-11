"""Regenerate sources.html: every source behind every module. Run after each ingest."""
import html
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

# The link the user sent for each module, plus the primary sources followed through to.
MODULES = [
    ("01", "https://x.com/HamelHusain/status/2112588257104216294", "Hamel Husain & Antaripa Saha", "20 Oct 2026", "X article",
     [("Full post with interactive charts (hamel.dev)", "https://hamel.dev/blog/posts/decision-model-evals/")]),
    ("02", "https://www.tensortonic.com/", "TensorTonic", "fetched 21 Oct 2026", "Website",
     [("Study plans", "https://www.tensortonic.com/study-plans"), ("ML Math", "https://www.tensortonic.com/ml-math")]),
    ("03", "https://x.com/LinusEkenstam/status/2112526605189054844", "Linus Ekenstam", "20 Oct 2026", "X post + 2:45 video (not watched)",
     [("gakku.ai", "https://www.gakku.ai/")]),
    ("04", "https://x.com/MaximeRivest/status/2112156468212289887", "Maxime Rivest", "19 Oct 2026", "X post + chart",
     [("own-voice-stt repo (README, evaluation, pitfalls, next steps)", "https://github.com/MaximeRivest/own-voice-stt")]),
    ("05", "https://x.com/antiAIvo/status/2112510656037761095", "@antiAIvo, quoting Philip Kiely (Baseten)", "20 Oct 2026", "X post (Chinese) + 1h video (not watched)",
     [("Philip Kiely's post", "https://x.com/philipkiely/status/2112272656217297224"),
      ("Kimi K3 repo and technical report", "https://github.com/MoonshotAI/Kimi-K3"),
      ("Kimi K3 on Baseten", "https://www.baseten.co/library/kimi-k3/")]),
    ("06", "https://github.com/Ojhaharsh/30u30", "Ojhaharsh (30u30)", "fetched 21 Oct 2026", "GitHub repo (CC BY-NC-ND 4.0)",
     [("The 30 original papers: linked from each day page", "topics/06-30u30/index.html")]),
    ("07", "https://x.com/dongxi_nlp/status/2112767071926792566", "Dongxi (东锡)", "21 Oct 2026", "X article (Chinese)", []),
    ("08", "https://x.com/suraj_sharma14/status/2112876560629825734", "Suraj Sharma", "21 Oct 2026", "X post",
     [("62 mapped courses, docs and repos (verified 22 Oct 2026)", "topics/08-ai-research-engineer/index.html#courses")]),
    ("09", "https://x.com/vishalsingh2972/status/2113830444722741637", "Vishal Singh", "24 Oct 2026", "X post",
     [("NVIDIA product pages (GPU specs) and papers: linked from each page", "topics/09-inference-engineering/index.html")]),
    ("10", "https://x.com/yacinelearning/status/2113688068352004435", "Yacine Mahdid (with Seth Karten)", "23 Oct 2026", "X post + 2h36m video (not watched)",
     [("Prime Agent paper (arXiv 2608.23552)", "https://arxiv.org/abs/2608.23552"),
      ("Prime Agent repo", "https://github.com/PrimeIntellect-ai/prime-agent"),
      ("Prime Agent launch post", "https://www.primeintellect.ai/blog/prime-agent"),
      ("Recursive Language Models (arXiv 2512.24601)", "https://arxiv.org/abs/2512.24601"),
      ("Continual Harness (arXiv 2605.09998)", "https://arxiv.org/abs/2605.09998"),
      ("The video", "https://www.youtube.com/watch?v=znotMe8NaHc")]),
    ("11", "https://x.com/dongxi_nlp/status/2114597689228698006", "Dongxi (东锡)", "26 Oct 2026", "X post (Chinese)",
     [("Stanford CS336", "https://stanford-cs336.github.io/spring2025/"),
      ("Build a Reasoning Model (From Scratch): code", "https://github.com/rasbt/reasoning-from-scratch"),
      ("RLHF Book", "https://rlhfbook.com/"),
      ("凯圣王 × 谭成义 three-way split (Bilibili)", "https://www.bilibili.com/video/BV17ooLBUEqS/")]),
    ("12", "https://www.youtube.com/playlist?list=PLXrQ2OzD3YKA", "Jia-Bin Huang", "videos Oct 2024 – Oct 2026", "YouTube playlist, 9 videos (not watched; chapter lists used)",
     [("Each video's references (ZeRO, PPO, GRPO, LoRA, Muon, SGLang, PagedAttention …): listed on each guide", "topics/12-training-inference-videos/index.html")]),
    ("13", "https://github.com/pavelsimo/100-days-of-inference-engineering", "Pavel Simo", "started 29 Oct 2026", "GitHub learning journal (no licence; summarised, not copied)",
     [("Inference Engineering by Philip Kiely (Baseten)", "https://www.baseten.co/inference-engineering/")]),
    ("14", "https://www.deep-ml.com/deep-path/diagnostic", "Deep-ML", "read 31 Oct 2026", "Interactive learning route + placement test (test needs sign-in; not taken)",
     [("Deep-Path map: 103 concepts, 14 parts (rendered in browser)", "https://www.deep-ml.com/deep-path"),
      ("Deep-ML", "https://www.deep-ml.com/")]),
    ("15", "https://inferenceengineering.tech/", "Philip Kiely (book) · digitized by Swapnil", "read 3 Nov 2026", "Interactive book companion site",
     [("About / attribution page", "https://inferenceengineering.tech/about/"),
      ("Official book page (Baseten)", "https://www.baseten.co/inference-engineering/"),
      ("vLLM vs SGLang benchmark page", "https://inferenceengineering.tech/benchmarks/")]),
    ("16", "https://github.com/orca3/llm-model-inference", "Chi Wang & Peiheng Hu", "repo updated Aug 2026", "GitHub companion code for an O'Reilly book (no licence file; summarised)",
     [("Book website", "https://orca3.github.io/llm-model-inference/"),
      ("O'Reilly page", "https://www.oreilly.com/library/view/hands-on-llm-serving/9798341621480/")]),
    ("17", "https://x.com/shikamarutsai/status/2088918066310652358", "shikamaru (@shikamarutsai)", "16 Aug 2026", "X article (a reproduction of an uncredited GitHub list)",
     [("Original list: Deep Learning Drizzle (kmario23)", "https://github.com/kmario23/deep-learning-drizzle")]),
    ("18", "topics/18-robot-brain/index.html", "Written for this course (from modules 01-17)", "Nov 2026", "Original hands-on course + Python project",
     [("Project code: homework, solutions, check.py", "topics/18-robot-brain/project/README.md")]),
    ("19", "https://x.com/sermakarevich/status/2106453816757354947", "Sergii Makarevych", "3 Oct 2026", "X article (34 min read)",
     [("Miller (2024), Adding Error Bars to Evals", "https://arxiv.org/abs/2411.00640"),
      ("Husain & Shankar, AI Evals FAQ", "https://hamel.dev/blog/posts/evals-faq/")]),
    ("20", "https://github.com/karpathy/micrograd", "Andrej Karpathy; tiny corp; Seungeun Rho", "fetched 7 Nov 2026", "Six GitHub repos (all MIT), cloned and run",
     [("minGPT", "https://github.com/karpathy/minGPT"), ("nanoGPT", "https://github.com/karpathy/nanoGPT"),
      ("nanochat (nanoGPT's successor)", "https://github.com/karpathy/nanochat"), ("llm.c", "https://github.com/karpathy/llm.c"),
      ("tinygrad", "https://github.com/tinygrad/tinygrad"), ("minimalRL", "https://github.com/seungeunrho/minimalRL")]),
    ("21", "https://x.com/0x_meden/status/2119507343348212198", "Martin (@0x_meden)", "8 Nov 2026", "X post: 10 interactive explainers (all links checked 9 Nov 2026)",
     [("His guide: How π0, GR00T and Optimus actually think (X article)", "https://x.com/0x_meden/status/2118366063196774479"),
      ("Immersive Linear Algebra", "https://immersivemath.com/ila"), ("Seeing Theory", "https://seeing-theory.brown.edu"),
      ("Markov chains (Setosa)", "https://setosa.io/ev/markov-chains"), ("Kalman filter in pictures", "https://www.bzarg.com/p/how-a-kalman-filter-works-in-pictures"),
      ("A* (Red Blob Games)", "https://www.redblobgames.com/pathfinding/a-star/introduction.html"), ("Fourier (Jez Swanson)", "https://www.jezzamon.com/fourier"),
      ("Why Momentum Really Works (Distill)", "https://distill.pub/2017/momentum"), ("REINFORCEjs", "https://cs.stanford.edu/people/karpathy/reinforcejs"),
      ("Transformer Explainer", "https://poloclub.github.io/transformer-explainer"), ("Diffusion Explainer", "https://poloclub.github.io/diffusion-explainer"),
      ("openpi", "https://github.com/Physical-Intelligence/openpi"), ("Isaac-GR00T", "https://github.com/NVIDIA/Isaac-GR00T")]),
    ("22", "https://x.com/matheorems/status/2119505986381901899", "Matheorems", "8 Nov 2026", "X post with an animation",
     [("3Blue1Brown: Divergence and curl", "https://www.youtube.com/watch?v=rB83DpBJQsE")]),
    ("23", "https://x.com/DeRonin_/status/2095180126359105955", "Ronin (@DeRonin_)", "2 Sep 2026", "X article",
     [("Tinkercad Circuits", "https://www.tinkercad.com/circuits"), ("Falstad circuit simulator", "https://www.falstad.com/circuit/"),
      ("ROS 2 Jazzy tutorials", "https://docs.ros.org/en/jazzy/Tutorials.html"), ("LeRobot docs", "https://huggingface.co/docs/lerobot/index")]),
    ("24", "https://www.news.aakashg.com/p/ai-evals", "Aakash Gupta (with Hamel Husain, Colin Matthews)", "Mar 2025 – Feb 2026", "Five paid newsletter posts (read in full via a subscriber's account, 11 Nov 2026)",
     [("AI Testing for PMs", "https://www.news.aakashg.com/p/ai-testing"), ("AI prototyping tools", "https://www.news.aakashg.com/p/ai-prototyping-tutorial"),
      ("Practical AI agents for PMs", "https://www.news.aakashg.com/p/practical-ai-agents-pms"), ("PM OS in Claude Code", "https://www.news.aakashg.com/p/pm-os"),
      ("Shankar et al., Who Validates the Validators?", "https://arxiv.org/abs/2404.12272")]),
]

e = html.escape
strip = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
index = (ROOT / "index.html").read_text()


def card(n):
    m = re.search(rf'<a class="card module" href="([^"]+)">\s*<div class="n">{n}[^<]*</div>\s*<h3>(.*?)</h3>', index, re.S)
    href, h3 = m.group(1), m.group(2)
    badge = re.search(r'<span class="track[^"]*">[^<]*</span>', h3).group(0)
    return href, badge, strip(re.sub(r'<span class="track[^"]*">[^<]*</span>', "", h3))


def takeaway(n):
    m = re.search(rf"<tr><td>{n}</td><td>.*?</td><td>.*?</td><td>(.*?)</td></tr>", index, re.S)
    return strip(m.group(1)) if m else ""


def pages(href):
    p = ROOT / href
    return sorted(p.parent.glob("*.html")) if p.name == "index.html" and p.parent.name != ROOT.name else [p]


def refs(files):
    seen = {}
    for f in files:
        for url, text in re.findall(r'<a href="(https?://[^"]+)"[^>]*>(.*?)</a>', f.read_text(), re.S):
            seen.setdefault(url, strip(text) or url)
    return seen


rows, total_refs, total_files = [], set(), 0
for n, link, author, date, kind, followed in MODULES:
    href, badge, title = card(n)
    saved = sorted(p.name for p in (ROOT / "sources").glob(f"{n}-*"))
    total_files += len(saved)
    r = refs(pages(href))
    total_refs |= set(r)
    fol = "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in followed)
    ref_rows = "".join(
        f'<tr><td><a href="{e(u)}">{e(t[:110])}</a></td><td>{e(urlparse(u).netloc.replace("www.", ""))}</td></tr>'
        for u, t in sorted(r.items(), key=lambda kv: urlparse(kv[0]).netloc))
    rows.append(f'''
<section class="card" id="m{n}">
<div class="eyebrow">{badge}Module {n}</div>
<h3><a href="{href}">{e(title)}</a></h3>
<div class="facts">
  <div><b>Link you sent</b><a href="{e(link)}">{e(urlparse(link).netloc + urlparse(link).path)[:60]}</a></div>
  <div><b>Author</b>{e(author)}</div>
  <div><b>Date</b>{e(date)}</div>
  <div><b>Type</b>{e(kind)}</div>
</div>
<p><strong>Summary:</strong> {e(takeaway(n))}</p>
{f"<p><strong>Followed through to:</strong></p><ul>{fol}</ul>" if fol else ""}
<p class="meta"><strong>Saved in <code>sources/</code>:</strong> {", ".join(f"<code>{e(s)}</code>" for s in saved) or "none"}</p>
<details><summary>All {len(r)} external references cited in this module</summary>
<div class="table-wrap"><table><tr><th>Reference</th><th>Site</th></tr>{ref_rows}</table></div></details>
</section>''')

toc = "".join(f'<li><a href="#m{n}">Module {n}</a>: {e(card(n)[2])}</li>' for n, *_ in MODULES)
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sources &amp; Summaries</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
<nav class="crumbs"><a href="index.html">← LLMs &amp; Robotics</a> · Sources</nav>
<div class="eyebrow">Course reference</div>
<h1>Sources &amp; summaries</h1>
<p class="lede">Every link you've added, what it became, the primary sources followed through to, the files saved locally, and every external reference each module cites.</p>
<div class="stats">
  <div class="stat"><div class="k">Links added</div><div class="v">{len(MODULES)}</div></div>
  <div class="stat"><div class="k">Saved source files</div><div class="v">{total_files}</div></div>
  <div class="stat"><div class="k">Unique external references</div><div class="v">{len(total_refs)}</div></div>
</div>
<div class="toc"><strong>Modules</strong><ol>{toc}</ol></div>
{"".join(rows)}
<footer>Generated by <code>tools/build_sources.py</code> from the module pages and the course index. Re-run it after each ingest. · <a href="index.html">Back to course index</a></footer>
</main>
</body>
</html>
'''
(ROOT / "sources.html").write_text(page)
print(f"sources.html: {len(MODULES)} modules, {total_files} saved files, {len(total_refs)} unique references")
