# ADK Course — Claude instructions

> **Filming / course-plan work?** Read [`FILMING_PLAN.md`](FILMING_PLAN.md) first — it is the
> video-course plan (Skillmea, Slovak, free-talk notebook walkthroughs, 30 lectures, 2026-08-19)
> and mirrors the "ADK" tab of the Skillmea overview workbook (Management drive). Update both
> together when the plan changes.

A course on Google's Agent Development Kit (ADK). **The notebooks are the course**: 14 Jupyter
notebooks (one per module), executed with outputs, plus a textbook. The video course is filmed
by talking freely over the notebooks (Testing-GenAI style), not from a script.

## Course shape

- **Part 1 — Vendor-agnostic spine (M01–M10).** ADK as a generic agent framework. Tested against
  **OpenRouter** so students can use Claude / GPT / Qwen / Gemma via LiteLLM.
- **Part 2 — Gemini unlocks (M11–M13).** What you lose if you don't use Gemini. Tested against
  **Google AI Studio**.
- **Side step — A2A protocol (M14).** Agent-to-agent communication. Tested against OpenRouter.
- **Video MVP (2026-08-19):** Part 1 + M11 taster; M12–M14 stay in the materials as self-study.
- **Agentic Design Patterns interludes** appear as short markdown sections inside relevant notebooks
  (source: `barcik-training-publications/_sources/agentic-design-patterns/`).

## Two learner paths

- **Full path** — all 14 modules, 6-8 hours.
- **Quick path (~1 hour)** — **M01 → M02 → M05 → M11**, marked ⚡ in `README.md`, the notebooks'
  first cell, and the textbook (`textbook/_sources/tools/build_html.py` → `QUICK_PATH_FILES`).
  Keep them consistent if the selection changes.

## The archived scripted-voiceover format

`archive/scripted-voiceover/` holds the earlier production format intact: 15 HTML slide decks
(`slides/module-NN-slug/index.html`, built by `slides/build_slides.py`), EN + SK speaker notes
(`speaker_notes.md`, `speaker_notes_sk.md`), the 77-lecture `LECTURE_PLAN.md`, the slides portal
`index.html`, and the renderer `slides/render_slides.py` (writes `slides-jpg/` next to it, gitignored).
Robert parked it on 2026-08-19 in favour of free-talk notebook walkthroughs; it may come back if
the new style doesn't work for him — **do not delete or "clean up" the archive**, and do not
spend effort keeping it in sync with notebook changes unless asked. The build/render scripts still
work from inside the archive (paths are relative to the script).

## Folder conventions

```
FILMING_PLAN.md             video-course lecture plan (mirrors the Skillmea "ADK" tab)
notebooks/                  NN_slug.ipynb — one per module, executed with outputs; legacy/ = pre-course version
mcp_servers/                reusable MCP servers for M02 tools demos (and M14)
scripts/                    python helpers loaded by notebooks when inline code would be too long
textbook/_sources/chapters/ NN-slug.md — markdown canonical
textbook/_sources/tools/    build_html.py
textbook/index.html         generated output — do NOT hand-edit
archive/scripted-voiceover/ slides, speaker notes, portal, old lecture plan (see above)
```

Drive sync (`training-ops/drive-push`, course key `adk`): only `notebooks/` (minus `legacy/`),
`mcp_servers/` and `requirements.txt` go to the Courses drive folder
`5. Google ADK (SYNCED)/course_materials (shared)` — slides/textbook/archive never reach students
via Drive. Run `python3 training-ops/drive-push/push.py --status --course adk` before and after
touching notebooks.

## Writing voice — read this before writing content

Two voices. Use the right one for the artifact.

### Textbook (and the archived slides + speaker notes) → Token Economics voice
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

## Keys and model choice

Two environment variables students (and Claude) load from `.env` (copy from `.env.example`):

| Variable | Powers | Cost strategy |
|---|---|---|
| `OPENROUTER_API_KEY` | M01–M10 + M14 via `LiteLlm("openrouter/<provider>/<model>")` | Course default (since 2026-08-23): `openrouter/openai/gpt-5.6-luna` — deliberately a **non-Google** model so Part 1 demonstrates vendor neutrality. Fallback with zero known LiteLLM quirks: `openrouter/anthropic/claude-haiku-4.5`. M04 comparison lineup: gemini-3.7-flash / gpt-5.6-luna / claude-haiku-4.5 / qwen3.7-flash (leaks thinking as text — intentional teaching point) / llama-4-scout. Check `curl https://openrouter.ai/api/v1/models` before changing. |
| `GOOGLE_API_KEY` | M11–M13 via direct `google-genai` / ADK Gemini | Default to `gemini-2.5-flash` for text, `gemini-3.1-flash-live-preview` only where the Live API is the point (live models are audio-native — TEXT-only modality is rejected with 1007). |

`GOOGLE_GENAI_USE_VERTEXAI=FALSE` in `.env` keeps ADK on the AI Studio path (no GCP billing).

## Running and testing notebooks

venv: `.venv27` (py3.12, ADK 2.7.1 stack; created 2026-08-19 — the old `.venv` is the 2.4 stack,
delete it when convenient). `jupyter nbconvert --execute` runs the `!pip install` cells too, so
notebook pins must match `requirements.txt` or the kernel downgrades itself mid-run.

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
- **`google-adk[eval]` caps litellm** below 1.86 (via `google-cloud-aiplatform[evaluation]`). Pinning a newer litellm next to the eval extra makes pip's resolve fail — and `!pip install -q ... 2>/dev/null` hides that failure, so the crash surfaces later as "Eval module is not installed". Keep the course-wide litellm pin inside the cap.
- **Google Search / code execution / Vertex Search** can't coexist with other tools in the same agent. Split via `bypass_multi_tools_limit=True` (ADK ≥ 1.16) or wrap each in its own sub-agent.
- **`adk eval`** hits PermissionError on read-only filesystems. Flag in M09; not a classroom blocker.
- **A2A on ADK is `@a2a_experimental`.** ADK (through 2.7) requires `a2a-sdk >=0.3.4,<0.4` — the a2a-sdk 1.x proto rewrite is not yet supported. Use `RemoteA2aAgent(..., use_legacy=False)`.
- **ADK 2.x `DatabaseSessionService` is async-only.** It lives behind the `[db]` extra (sqlalchemy no longer a hard dep) and *requires* an async driver URL (`sqlite+aiosqlite://`); the plain sync `sqlite://` scheme is rejected. Exactly inverted from 1.28 — see `DEMOS_BROKEN.md` M08 entry.
- **Windows**: `PYTHONUTF8=1` — documented in `.env.example`.
- **LiteLLM 1.85 prints botocore/bedrock warnings at import** unless `LITELLM_LOG=ERROR` is set
  before `import litellm` — every notebook's import cell does this now; keep it.
- **ADK 2.7 logs a context_cache_config advisory on every sub_agent transfer** (M06) — silenced
  with `logging.getLogger("google_adk").setLevel(logging.ERROR)` in that notebook.
- **`gemini-2.5-flash-lite` (the pre-2026-08-23 default) was flaky on "what do I prefer?"-style recall** (M08): it answers
  "no preference" without calling the tool ~half the time. The demo now uses an explicit
  `recall_preference` tool + the prompt "What is my saved preference?", which is reliable. If a
  live demo misbehaves, re-run the cell once before blaming the code.
- **Port 8765 (M10 `adk api_server`)**: a stray local server on that port makes the notebook
  fail with 404 on `/list-apps` — `lsof -i :8765` first.

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
