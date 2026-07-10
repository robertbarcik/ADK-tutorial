# Google ADK — A Practical Course

A vendor-agnostic course on Google's Agent Development Kit. Fourteen modules, four aligned artifacts each: **slides**, **speaker notes**, **textbook chapter**, **Jupyter notebook**.

Part 1 teaches the portable spine of ADK — the agent mental model, tools, state, workflow agents, multi-agent hierarchies, callbacks, memory, evaluation, deployment — running against any model via LiteLLM (OpenRouter by default). Part 2 covers what only unlocks with Gemini: search grounding, long context with caching, thinking budgets, and the Live voice API. A short side step on the A2A agent-to-agent protocol closes the course.

The course runs on the **ADK 2.x line** (`google-adk==2.4.0` pinned in `requirements.txt`). ADK 2.0 (May 2026) added a graph-based workflow runtime for advanced compositions; the classic agent API taught throughout this course carried over from 1.x unchanged, so everything here applies to both lines.

---

## Two ways to take the course

Pick the path that matches what you have time for.

### ⚡ Quick path — ~1 hour

For the impatient, or for a course preview before committing. Four modules, in order, give you the core ADK mental model plus the most-demonstrated wow capabilities.

| # | Module | Why it's on the quick path |
|---|---|---|
| **M01** | Why agents, why ADK | The four primitives (Agent, Runner, Event, Session). Non-negotiable foundation. |
| **M02** | Tools as verbs | Tools are what make an agent useful. Four flavors in 20 minutes. |
| **M05** | Workflow agents | The canonical Generator+Critic refinement loop — the "oh, this is what ADK is good at" moment. |
| **M11** | Gemini grounding + caching | A taste of what Part 2 adds on top of vendor-agnostic ADK. Real citations, 90% caching discount. |

Each quick-path module is marked with **⚡** on the portal, in slide-deck headers, and in the textbook sidebar. Everything else in the course is there for when you want to deepen a specific area.

**Suggested reading order for Quick path:**
1. Slides M01 + speaker notes — 15 min
2. Notebook M01 — skim the code, no need to run it fully — 5 min
3. Slides M02 — 20 min
4. Textbook chapter 5 (Workflow agents) — 15 min
5. Slides M11 — 10 min

That's ~65 minutes; you'll be able to explain what ADK is, what agent software looks like, and why Gemini is the vendor with the most to offer.

### Full path — 6–8 hours

The deep track. All 14 modules; all four artifacts per module. Build, test, deploy. This is the course as authored.

| # | Module | API key |
|---|---|---|
| **M01** ⚡ | Why agents, why ADK — the Agent + Runner + Event model | OpenRouter |
| **M02** ⚡ | Tools as verbs — FunctionTool, OpenAPI, MCP, AgentTool | OpenRouter |
| M03 | Sessions, State, Events, Artifacts | OpenRouter |
| M04 | The one-line model swap (LiteLLM) | OpenRouter |
| **M05** ⚡ | Workflow agents — Sequential, Parallel, Loop | OpenRouter |
| M06 | Multi-agent hierarchies — `sub_agents` vs `AgentTool` | OpenRouter |
| M07 | Callbacks as middleware | OpenRouter |
| M08 | Memory — sessions, long-term recall, `load_memory` | OpenRouter |
| M09 | Evaluation — trajectories, EvalSets | OpenRouter |
| M10 | Deployment — Cloud Run and vanilla Docker | OpenRouter |
| **M11** ⚡ | Google Search grounding, long context, context caching | Google AI Studio |
| M12 | Thinking budgets | Google AI Studio |
| M13 | Live API — voice agent with interruption | Google AI Studio |
| M14 | A2A protocol — agent-to-agent | OpenRouter |

Rows marked **⚡** are the quick-path modules. If you're on the full path, the marker is just a cue that those four carry the highest-density content — pay special attention.

Every notebook opens directly in Google Colab via the "Open in Colab" badge on its first cell — no local setup needed to read along, since each is committed executed with outputs already in place.

---

## Getting started

```bash
git clone https://github.com/robertbarcik/ADK-tutorial
cd ADK-tutorial

python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in at least OPENROUTER_API_KEY for Part 1.
# Add GOOGLE_API_KEY when you reach Part 2 (M11).

jupyter notebook notebooks/
```

### Open the slides portal

The course front page — a compact grid of all 14 decks plus the Quick-path callout — lives at the repo root:

```bash
open index.html
```

Each module's slide deck is self-contained and opens standalone too:

```bash
open slides/module-01-mental-model/index.html
```

### Open the textbook

Single-page HTML booklet, 15 chapters (introduction plus one per module):

```bash
# Generate if not already built
python3 textbook/_sources/tools/build_html.py

open textbook/index.html
```

Quick-path chapters are marked with **⚡** in the sidebar and chapter headers.

### Render slides as images (for video editing)

If you're recording a voiceover and need per-slide 1920×1080 stills for a video editor, `slides/render_slides.py` generates them in a headless browser via Playwright. Takes under a minute for all 14 decks (~274 slides).

```bash
# One-time setup
pip install playwright
python3 -m playwright install chromium

# Render all decks as JPG at 1920×1080 → slides-jpg/module-NN-slug/NN.jpg
python3 slides/render_slides.py

# Just one module
python3 slides/render_slides.py --module 05

# PNG instead of JPG (lossless, bigger)
python3 slides/render_slides.py --format png

# Different resolution
python3 slides/render_slides.py --width 1280 --height 720
```

The progress strip and on-screen controls are hidden in rendered output so each frame uses the full canvas. Output is `.gitignore`'d by default (re-generating is cheap); remove the entry if you want to commit stills alongside the source.

---

## Repository layout

```
index.html                  slides portal / course front page (deployable to S3)
slides/shared/              canonical CSS/JS — edit here
slides/build_slides.py      inlines shared/*.{css,js} into each deck (run after edits)
slides/render_slides.py     renders every slide as a 1920×1080 JPG/PNG for video editing
slides/module-NN-slug/      per-module deck (self-contained) + speaker_notes.md
slides-jpg/                 (generated; gitignored) per-slide image renders
textbook/_sources/chapters/ chapter markdown (canonical)
textbook/_sources/tools/    build_html.py
textbook/index.html         generated booklet (do not hand-edit)
notebooks/                  14 runnable exercises, one per module
notebooks/legacy/           earlier notebooks, kept for reference during transition
mcp_servers/                reusable MCP servers used in M02 and M14
scripts/                    python helpers for notebooks
DEMOS_BROKEN.md             running log of demos that need fixing
CLAUDE.md                   project conventions for AI collaborators
```

## Cost notes

All exercises are designed to run on cheap models. Default to `openrouter/google/gemini-2.5-flash-lite` or `openrouter/openai/gpt-4o-mini` on OpenRouter (typical module cost: under $0.05 when running all cells). On Google AI Studio, default to `gemini-2.5-flash`; the Live API demo in M13 uses `gemini-3.1-flash-live-preview` for short smoke tests only.

A full Quick path costs under **$0.10** total on OpenRouter + Google AI Studio free tier combined.

## License

Materials © Robert Barcík / LearningDoe s.r.o. Code samples Apache 2.0.
