# Google ADK — A Practical Course

A vendor-agnostic course on Google's Agent Development Kit. Fourteen modules, four aligned artifacts each: **slides**, **speaker notes**, **textbook chapter**, **Jupyter notebook**.

Part 1 teaches the portable spine of ADK — the agent mental model, tools, state, workflow agents, multi-agent hierarchies, callbacks, memory, evaluation, deployment — running against any model via LiteLLM (OpenRouter by default). Part 2 covers what only unlocks with Gemini: search grounding, long context with caching, thinking budgets, and the Live voice API. A short side step on the A2A agent-to-agent protocol closes the course.

## Course map

| # | Module | API key needed |
|---|---|---|
| M01 | Why agents, why ADK — the Agent + Runner + Event model | OpenRouter |
| M02 | Tools as verbs — FunctionTool, OpenAPI, MCP, AgentTool | OpenRouter |
| M03 | Sessions, State, Events, Artifacts | OpenRouter |
| M04 | The one-line model swap (LiteLLM) | OpenRouter |
| M05 | Workflow agents — Sequential, Parallel, Loop | OpenRouter |
| M06 | Multi-agent hierarchies — `sub_agents` vs `AgentTool` | OpenRouter |
| M07 | Callbacks as middleware | OpenRouter |
| M08 | Memory — sessions, long-term recall, `load_memory` | OpenRouter |
| M09 | Evaluation — trajectories, EvalSets | OpenRouter |
| M10 | Deployment — Cloud Run and vanilla Docker | OpenRouter |
| M11 | Google Search grounding, long context, context caching | Google AI Studio |
| M12 | Thinking budgets | Google AI Studio |
| M13 | Live API — voice agent with interruption | Google AI Studio |
| M14 | A2A protocol — agent-to-agent | OpenRouter |

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

Each module's slide deck opens directly in a browser:

```bash
open slides/module-01-mental-model/index.html
```

To build the textbook as a single-page HTML booklet:

```bash
python3 textbook/_sources/tools/build_html.py
open textbook/index.html
```

## Repository layout

```
slides/shared/              shared CSS/JS used by every deck
slides/module-NN-slug/      per-module deck + speaker_notes.md
textbook/_sources/chapters/ chapter markdown (canonical)
textbook/_sources/tools/    build_html.py
textbook/index.html         generated booklet (do not hand-edit)
notebooks/                  runnable exercises, one per module
notebooks/legacy/           earlier notebooks, kept for reference during transition
mcp_servers/                reusable MCP servers used in M02 and M14
scripts/                    python helpers for notebooks
DEMOS_BROKEN.md             running log of demos that need fixing
CLAUDE.md                   project conventions for AI collaborators
```

## Cost notes

All exercises are designed to run on cheap models. Default to `openrouter/google/gemini-2.5-flash-lite` or `openrouter/openai/gpt-4o-mini` on OpenRouter (typical module cost: under $0.05 when running all cells). On Google AI Studio, default to `gemini-2.5-flash`; the Live API demo in M13 uses `gemini-live-2.5-flash-native-audio` for short smoke tests only.

## License

Materials © Robert Barcík / LearningDoe s.r.o. Code samples Apache 2.0.
