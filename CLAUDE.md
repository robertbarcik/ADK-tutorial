# ADK Course — Claude instructions

> **Picking up speaker-notes work?** Read [`SPEAKER_NOTES_STATUS.md`](SPEAKER_NOTES_STATUS.md) first. It tracks which modules have been rewritten, the conventions established (notebook breaks, slide-deck structure, prose rules), and a final-pass checklist. Janka and Claude have been iterating module by module; that file is the cross-session source of truth.

A full course on Google's Agent Development Kit (ADK). Four aligned components per module: slides, speaker notes, textbook chapter, Jupyter notebook.

## Course shape

- **Part 1 — Vendor-agnostic spine (M01–M10).** ADK as a generic agent framework. Tested against **OpenRouter** so students can use Claude / GPT / Qwen / Gemma via LiteLLM.
- **Part 2 — Gemini unlocks (M11–M13).** What you lose if you don't use Gemini. Tested against **Google AI Studio**.
- **Side step — A2A protocol (M14).** 30 min on agent-to-agent communication. Tested against OpenRouter.
- **Agentic Design Patterns interludes.** Selected concepts from `barcik-training-publications/_sources/agentic-design-patterns/` appear as 1–2 slide interludes embedded in relevant modules, not standalone.

## Two learner paths

The README now exposes two paths. Any ⚡ marker you see — in the portal, in slide decks, in textbook chapters, in notebooks — is part of this.

- **Full path** — all 14 modules, 6-8 hours.
- **Quick path (~1 hour)** — **M01 → M02 → M05 → M11**. These four modules are marked ⚡ throughout the artifacts. If asked to modify the Quick path selection, update consistently across:
  - `README.md` (tables + suggested reading order)
  - `index.html` (portal — `.quick-path` classes + the amber callout)
  - `slides/module-*/index.html` (progress-strip badge)
  - `textbook/_sources/tools/build_html.py` → `QUICK_PATH_FILES` set
  - `notebooks/*.ipynb` (first-cell blockquote)

## Video-recording workflow (why `render_slides.py` exists)

Robert's production workflow for the course videos:

1. Record audio only, reading from `slides/module-*/speaker_notes.md`.
2. Import into a video editor (Premiere / Resolve / etc.).
3. Drop the matching slide image from `slides-jpg/module-*/NN.jpg` onto the timeline at each slide transition.
4. No on-screen presenter, no browser capture — just clean 1920×1080 stills timed to narration.

This means:
- **Speaker notes must read like spoken delivery.** One section per slide, no filler, no "let's look at this slide now" meta-language. Token Economics voice.
- **Slide stills need to be production-clean.** The progress strip and font controls are hidden during render — no UI chrome to crop out in post.
- **Slides should be information-complete.** The audio narrates what's on the slide; the slide carries the content. No speaker-notes-only information.

## Folder conventions

```
index.html                  # slides portal / course front page (self-contained, deployable to S3)
slides/shared/              # CANONICAL shared.css + slides.css + slides.js — edit here
slides/build_slides.py      # inlines shared/*.{css,js} into each deck's index.html
slides/module-NN-slug/      # index.html (generated, self-contained) + speaker_notes.md
textbook/_sources/chapters/ # NN-slug.md — markdown canonical
textbook/_sources/tools/    # build_html.py
textbook/index.html         # generated output — do NOT hand-edit
notebooks/                  # NN_slug.ipynb — one per module, plus legacy/ for the pre-course version
mcp_servers/                # reusable MCP servers for M02 tools demos
scripts/                    # python helpers loaded by notebooks when inline code would be too long
```

## Why the slide deck HTMLs are "built"

Safari — and some Chrome strict-mode configurations — block `file://`-path loads of relative CSS and JS as a security measure. That turns every double-click-to-open into a wall of unstyled text.

Fix: each `slides/module-NN-slug/index.html` has the shared CSS/JS **inlined** by `slides/build_slides.py`. Each deck becomes a single self-contained HTML file that opens cleanly via `file://` in any browser, and still deploys cleanly over HTTPS.

**Workflow**:
1. Edit the canonical sources in `slides/shared/` (shared.css, slides.css, slides.js).
2. Run `python3 slides/build_slides.py` — it walks every `slides/module-*/index.html` and re-inlines.
3. Commit the regenerated deck HTMLs alongside the shared-source change.

A banner comment at the top of each generated deck says: `<!-- Built by slides/build_slides.py — shared CSS/JS inlined for file:// portability. -->`. Don't hand-edit the inlined blocks; edit the shared source and re-run the builder.

## Rendering slides as images

`slides/render_slides.py` drives a headless Chromium (via Playwright) to produce per-slide JPG/PNG stills at 1920×1080, for video-editor workflows. Output goes to `slides-jpg/module-NN-slug/NN.jpg` (gitignored by default).

One-time: `pip install playwright && python3 -m playwright install chromium`.
Then: `python3 slides/render_slides.py` renders all 14 decks in ~45 seconds.

CLI flags: `--module 05`, `--format png`, `--width 1280 --height 720`, `--quality 88`.

The renderer hides the progress strip so each frame is a clean full-viewport slide.

## Writing voice — read this before writing content

Two voices. Use the right one for the artifact.

### Slides + speaker notes + textbook → Token Economics voice
Reference: `barcik-training-publications/_sources/token-economics/chapters/01_genai_moment.md`.

- Short declarative sentences. Reversals as one-line paragraphs.
- Specific over generic: "~18K GitHub stars" not "popular", "$2 per million tokens" not "cheap".
- Skeptical of hype. Name gotchas out loud.
- Analogies to known domains (HTTP, middleware, databases) — not abstract metaphors.
- No "it's important to note", no "let's explore", no "in this module we will learn about". Open with the content, not the meta.
- **No emojis in slides, speaker notes, or textbook.**
- Speaker notes are spoken delivery — readable straight into a microphone. No "let's take a look at...". Just say the thing.

### Notebooks → hybrid voice
Reference: the existing `notebooks/legacy/*.ipynb` — particularly after the
April 2026 "notebook guidelines" updates — for the target tone.

- **Colab-first.** `!pip install -q` at the top, `userdata.get(...)` + `getpass` fallback + optional `.env` load. Notebooks must run unchanged on Colab and on a local Jupyter.
- **Use `LlmAgent`** (the user-facing class name), not `Agent` (which is an alias).
- **Friendly "Your Turn" framing for exercises** — keep this.
- **Status emojis are fine and encouraged in code output**: ✅ for success, ❌ for error, 💡 for tips, 🔑 for key-setup. They aid visual parsing in a scrolling notebook. *Do not* use decorative emojis in markdown headings (no 🎯, 🛠️ in an `## Our Agent Goals` header).
- **Verbose, use-case-framed docstrings** on tool functions are a strength — keep them.
- **Markdown-cell content** still leans Token Economics in voice (direct, specific, no filler) — the friendly structure is in the scaffolding, not in padded prose.
- **Pinned dependencies at install**: match `requirements.txt` versions exactly in `!pip install` lines, so Colab and local get identical environments.

### Slides + speaker notes + textbook → Token Economics voice
*(unchanged — no emojis, no filler, no "let's explore")*

## Keys and model choice

Two environment variables students (and Claude) load from `.env` (copy from `.env.example`):

| Variable | Powers | Cost strategy |
|---|---|---|
| `OPENROUTER_API_KEY` | M01–M10 + M14 via `LiteLlm("openrouter/<provider>/<model>")` | Default to cheap models when testing: `openrouter/google/gemini-2.5-flash-lite` or `openrouter/openai/gpt-4o-mini`. |
| `GOOGLE_API_KEY` | M11–M13 via direct `google-genai` / ADK Gemini | Default to `gemini-2.5-flash` for text, `gemini-live-2.5-flash-native-audio` only where the Live API is the point. |

`GOOGLE_GENAI_USE_VERTEXAI=FALSE` in `.env` keeps ADK on the AI Studio path (no GCP billing).

## Running and testing notebooks

Before committing a module change, the notebook must run top-to-bottom against a fresh kernel:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then fill in keys
jupyter nbconvert --to notebook --execute notebooks/NN_slug.ipynb --output-dir /tmp/adk-smoke
```

If a demo cannot be made to run, do not skip the material — write the slides / chapter / notebook against the intended design, and log the failure in `DEMOS_BROKEN.md` with reproduction steps and a workaround for students.

Notebooks are committed **executed, with outputs** — they read like an article, not a blank template. Refresh outputs by re-running headless (`jupyter nbconvert --to notebook --execute --inplace`); do not blank cell outputs before committing. Each of the 14 current notebooks carries an Open-in-Colab badge as its first markdown cell.

## Known gotchas (pre-empt these in code)

- **LiteLLM + streaming + tool calls** is flaky on non-Gemini models. Default all OpenRouter demos to `stream=False`.
- **Ollama**: use `ollama_chat/` prefix, not `ollama/` — the plain prefix causes infinite tool-call loops.
- **Structured output** breaks when `google-adk` and `litellm` versions drift. Pin them together; bump as a pair.
- **Google Search / code execution / Vertex Search** can't coexist with other tools in the same agent. Split via `bypass_multi_tools_limit=True` (ADK ≥ 1.16) or wrap each in its own sub-agent.
- **`adk eval`** hits PermissionError on read-only filesystems. Flag in M09; not a classroom blocker.
- **A2A on ADK is `@a2a_experimental`.** Pin `a2a-sdk 0.3.24`, use `RemoteA2aAgent(..., use_legacy=False)`.
- **Windows**: `PYTHONUTF8=1` — documented in `.env.example`.

## Building the textbook

```bash
python3 textbook/_sources/tools/build_html.py
# writes textbook/index.html
```

`textbook/_sources/chapters/*.md` are canonical. Never hand-edit `textbook/index.html`.

## Git workflow

- Commit directly to `main` and push. No feature branches, no pull requests for this repo.
- No force-pushes, no `--no-verify`, no amending published commits.

## Reference repos (style only — do not modify from here)

- Slide format: `/Users/robertbarcik/git-repos/barcik-training-exin-ai-foundation/slides/`
- Textbook build + voice: `/Users/robertbarcik/git-repos/barcik-training-publications/_sources/token-economics/`
- Agentic Design Patterns source: `/Users/robertbarcik/git-repos/barcik-training-publications/_sources/agentic-design-patterns/chapters/`

## Deployment (deferred)

Materials are static. When ready, wire up like `barcik-training-publications`: S3 bucket + CloudFront distribution, `aws s3 sync` + invalidation. Not in scope yet — ship content first.
