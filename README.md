# Google ADK — A Practical Course

A vendor-agnostic course on Google's Agent Development Kit — and a **direct continuation of [Intro to GenAI in Python](https://github.com/robertbarcik/genai-in-python-tutorial)**: notebook 01 re-runs the function-calling loop you built there (one changed line) and maps it onto ADK's primitives, and every module opens with a "Where you are" block linking back to what you already know. You need no async, classes, or decorators coming in — each is explained at first encounter. Thirteen Jupyter notebooks, executed with outputs, plus a textbook. Part 1 (M01–M10) teaches the portable spine of ADK — the agent mental model, tools, state, workflow agents, multi-agent hierarchies, callbacks, memory, evaluation, deployment — running against any model via LiteLLM (OpenRouter by default). Part 2 (M11–M12) covers what only unlocks with Gemini: search grounding, long context with caching, thinking budgets. M13 is a side step on the A2A agent-to-agent protocol.

The course runs on the **ADK 2.x line** (`google-adk==2.7.1` pinned in `requirements.txt`, re-verified 2026-08-19; the classic agent API taught here is unchanged since 1.x — the graph workflow runtime added in 2.0 is additive).

**Video course (Skillmea, Slovak):** filmed as free-talk notebook walkthroughs. The video course covers Part 1 (M01–M10) plus a Gemini taster (M11); notebooks 12–13 are included in the materials for self-study.


---

## Two ways to take the course

### ⚡ Quick path — 2 to 2½ hours

Five notebooks, in order, on a single OpenRouter key: the core ADK mental model, tools, both ways of putting agents together, and your own code around every step.

| # | Module | Why it's on the quick path |
|---|---|---|
| **M01** | Why agents, why ADK | The four primitives (Agent, Runner, Event, Session). Non-negotiable foundation. |
| **M02** | Tools as verbs | Tools are what make an agent useful. Four flavors in 20 minutes. |
| **M05** | Workflow agents | The canonical Generator+Critic refinement loop — the "oh, this is what ADK is good at" moment. |
| **M06** | Multi-agent hierarchies | The promise the course opens with, kept: a sub-agent is just a function call. `sub_agents` vs `AgentTool`, side by side. |
| **M07** | Callbacks | Short and essential: six doors where your code runs before or after every step — guardrails, PII redaction, mocks. |

Quick-path modules are marked with **⚡** in the notebooks' first cell and in the textbook sidebar. Their files also carry a `_CORE` suffix (e.g. `05_workflow_agents_CORE.ipynb`), so you can pick them out of the folder on GitHub or Drive at a glance. Optional dessert if you have a Google AI Studio key: **M11** (search grounding with real citations — one import).

### Full path — 6–8 hours

| # | Module | API key |
|---|---|---|
| **M01** ⚡ | Why agents, why ADK — the Agent + Runner + Event model | OpenRouter |
| **M02** ⚡ | Tools as verbs — FunctionTool, OpenAPI, MCP, AgentTool | OpenRouter |
| M03 | Sessions, State, Events, Artifacts | OpenRouter |
| M04 | The one-line model swap (LiteLLM) | OpenRouter |
| **M05** ⚡ | Workflow agents — Sequential, Parallel, Loop | OpenRouter |
| **M06** ⚡ | Multi-agent hierarchies — `sub_agents` vs `AgentTool` | OpenRouter |
| **M07** ⚡ | Callbacks as middleware | OpenRouter |
| 07b | *Reading:* Can the Runner get stuck in a loop? — the `max_llm_calls` fuse, a ten-line circuit breaker, the retry plugin | none (stand-in model) |
| M08 | Memory — sessions, long-term recall, `load_memory` | OpenRouter |
| M09 | Evaluation — trajectories, EvalSets | OpenRouter |
| M10 | Deployment — Cloud Run and vanilla Docker | OpenRouter |
| M11 | Google Search grounding, long context, context caching | Google AI Studio |
| M12 | Thinking budgets | Google AI Studio |
| M13 | A2A protocol — agent-to-agent | OpenRouter |

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

### Open the textbook

Single-page HTML booklet, 14 chapters (introduction plus one per module):

```bash
python3 textbook/_sources/tools/build_html.py   # generate if not already built
open textbook/index.html
```

---

## Repository layout

```
notebooks/                  13 runnable exercises, one per module — THE course
notebooks/legacy/           earlier notebooks, kept for reference
mcp_servers/                reusable MCP servers used in M02 and M13
scripts/                    python helpers for notebooks
textbook/_sources/chapters/ chapter markdown (canonical)
textbook/_sources/tools/    build_html.py
textbook/index.html         generated booklet (do not hand-edit)
DEMOS_BROKEN.md             running log of demos that need fixing
CLAUDE.md                   project conventions for AI collaborators
```

## Cost notes

All exercises are designed to run on cheap models. Default to `openrouter/openai/gpt-5.6-luna` (the course default — deliberately not a Google model, to show ADK is vendor-neutral) or `openrouter/anthropic/claude-haiku-4.5` on OpenRouter (typical module cost: under $0.05 when running all cells). On Google AI Studio, default to `gemini-2.5-flash`.

A full Quick path costs under **$0.10** total on OpenRouter — no second key needed.

## License

Materials © Robert Barcík / LearningDoe s.r.o. Code samples Apache 2.0.
