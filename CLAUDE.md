# LLMs & Robotics: course schema

A personal HTML course built from links the user adds. The LLM writes and maintains everything. The user curates the links.

## Layout
- `index.html`: course home. Module cards, "Summaries at a glance" table, concept map.
- `topics/NN-slug.html`: one module per link or topic. NN is a zero-padded sequence.
- `sources/NN-slug.*`: raw fetched source (JSON/markdown/text). Immutable once saved.
- `style.css`: shared styles (light/dark tokens). Reuse its classes; don't inline new styles unless needed.
- `log.md`: append-only history, one entry per ingest.
- `sources.html`: generated list of every source and its summary (`tools/build_sources.py`). Don't edit it by hand.

## Ingesting a new link
1. Fetch the content. X/Twitter blocks direct fetches. Use `curl -s https://api.fxtwitter.com/<user>/status/<id>`. The `tweet.article.content.blocks` field holds long-form X articles. Follow through to the linked post when the tweet is only a pointer.
2. Save the raw content to `sources/NN-slug.*`.
3. Write `topics/NN-slug.html` with these sections, matching module 01:
   Summary (TL;DR card + bullets) → Why this matters for robotics → Deep dives (one per major idea) → Playbook → Self-check (`<details>` Q&A) → Glossary & further reading.
   Add an interactive demo when a concept is easy to show visually.
4. Assign a track: LLM, Robotics or LLM + Robotics. Put the badge (`<span class="track llm|robo|both">`) in the eyebrow and on the index card, title the page so its domain is clear, and add a `.note` card stating the track and how it connects to the other one. The course covers both fields; don't treat LLM content as off-topic.
5. Update `index.html`: add a module card, a row in "Summaries at a glance", update the concept map (add a new concept or append the module number), and update the module count and date.
6. Cross-link: if the new module relates to earlier ones, add links both ways.
7. Append to `log.md`: `## [YYYY-MM-DD] ingest | Title`.
8. Add the module to `MODULES` in `tools/build_sources.py` (link sent, author, date, type, primary sources followed), then run `python3 tools/build_sources.py` to regenerate `sources.html`.

## Multi-part sources
- A source with many sub-topics (e.g. a reading list) becomes a folder `topics/NN-slug/` with its own `index.html` hub and one page per item. See module 06.
- Respect source licences. If a source is no-derivatives (e.g. CC BY-NC-ND), write from the original papers and link to the source. Don't adapt its text or code.

## Beginner layer
- The user wants pages easy to follow for a 13-year-old. Every module 06 day opens with `<section class="kid" id="start">` ("Start here (no maths needed)": big idea, everyday analogy, simple steps, why robots care, try-it, words to know), then a `<p class="deeper">` line. Use the same pattern on new pages.

## Style
- Plain, direct language. Short sentences. Concrete numbers from the source.
- Never fabricate figures. If the source doesn't give a number, say so.
