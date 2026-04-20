# Thinking budgets

The second Gemini-only unlock. Simpler than grounding and caching; one knob, big effect.

Gemini 2.5+ models support **thinking** — an internal reasoning pass the model does before producing the final answer. The tokens consumed during thinking don't appear in the output text; they're billed as a separate category (`thoughts_token_count`) and they take real wall-clock time.

`ThinkingConfig.thinking_budget` is the knob. Set it to 0 for instant responses (no internal reasoning); set it to 2048+ for hard problems where reasoning pays off. The trade-off is explicit — you spend tokens and latency in exchange for answer quality on reasoning-heavy tasks.

## How thinking works

When you give Gemini 2.5+ a `thinking_budget` greater than zero, the model internally does a reasoning pass before generating the visible response. That reasoning is a real LLM operation — tokens are consumed, time is spent — but it's kept separate from the output text. The usage-metadata object ADK returns surfaces three token counts:

- `prompt_token_count` — what you sent in.
- `thoughts_token_count` — internal reasoning (only present when thinking was enabled).
- `candidates_token_count` — visible output text.

All three are billed at the respective model rates. Thought tokens bill at the output-token rate (e.g., $0.30/M on Flash). Modest per-invocation cost; worth it for hard problems.

Two ways to control thinking:

| Setting | Type | Use |
|---|---|---|
| `thinking_budget=0` | int | Disable thinking. Instant response. |
| `thinking_budget=N` | int | Allow up to N thought tokens. Gemini may use less. |
| `thinking_level=LOW/MEDIUM/HIGH` | enum | Gemini 3+ only; coarser preset. |

The `thinking_level` form is the Gemini-3 addition. Use it when you don't want to pick a number; use `thinking_budget` when you want precise control.

## Direct comparison — same problem, two budgets

The notebook runs a reasoning-heavy problem through Gemini twice — once with `thinking_budget=0`, once with `thinking_budget=4096`.

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=GOOGLE_API_KEY)

PROBLEM = """A small bakery sells three types of bread with different revenue,
labor time, and flour cost. Which has the highest profit margin? ..."""

for budget in [0, 4096]:
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROBLEM,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=budget),
        ),
    )
    print(f"budget={budget}: latency={...}s, thoughts={resp.usage_metadata.thoughts_token_count}")
```

Typical output:

```
── thinking_budget=0 ──
latency: <1s
tokens — input: 158, thoughts: 0, output: 702

── thinking_budget=4096 ──
latency: 11.06s
tokens — input: 158, thoughts: 1109, output: 702
```

Same inputs, same outputs in size — 702 tokens both times. Big latency and thought-token gap. The 1109 thought tokens are reasoning the model did internally that never reached the user's screen.

## The even better demo — visible quality delta

For a tighter example, ask both a thinking-disabled agent and a thinking-enabled agent:

> What is the sum of all prime numbers between 20 and 50?

The correct answer is `251` (primes are 23, 29, 31, 37, 41, 43, 47).

Typical results:

```
── fast_agent (thinking=0)    0.76s
   Answer: 255   ← wrong

── thinking_agent (thinking=2048)    9.98s
   Answer: enumerated primes, sum = 251   ← correct
```

One agent got the right answer; one got a wrong answer. The difference was the thinking budget. Quality delta made visible.

This doesn't happen every time — sometimes `thinking=0` gets reasoning problems right by accident. But in a statistically meaningful sample, the thinking-enabled agent is reliably better on tasks that require step-by-step work. That's the property you're paying for.

## Wiring thinking into an ADK agent — `BuiltInPlanner`

ADK exposes thinking via a `planner=` argument on `LlmAgent`. The concrete planner class is `BuiltInPlanner`, which wraps a `ThinkingConfig`:

```python
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types

thinking_agent = LlmAgent(
    name="thinking_agent",
    model="gemini-2.5-flash",
    description="Reasoning agent with a generous thinking budget.",
    instruction="Answer user questions. Reason carefully for multi-step problems.",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(thinking_budget=2048),
    ),
)
```

Everything else about the agent — tools, sub-agents, callbacks, memory, output_key — works the same. The planner is a plug-in point for features that affect how the model thinks, without expanding the constructor signature. Future planners may add other pre-reasoning patterns; today, the built-in one exposes the thinking budget.

## When thinking earns its keep

Thinking budgets are not free. Tokens cost money; latency costs user patience. Crank the budget for:

- **Multi-step reasoning.** The bakery profit-margin problem. Logic puzzles. Chain-of-inference questions.
- **Code debugging.** The model has to trace through code logic; thinking helps significantly.
- **Hard math.** Arithmetic, algebra, proofs, combinatorics.
- **Multi-constraint planning.** Itinerary-building, resource allocation, scheduling with dependencies.

Skip thinking for:

- **Factual lookups.** "Capital of France", "weather in Prague". The model already knows — no reasoning needed.
- **Text transformations.** Summarization, translation, style rewriting. These are pattern-matches, not reasoning.
- **Simple classification.** "Is this email spam?" Usually pattern-recognition, rarely benefits from step-by-step thought.

The simple heuristic: **does the problem require the model to work something out step by step?** Crank the budget. Does it require retrieving something the model already knows? Skip.

## Production pattern — route on query type

The practical composition: a cheap, fast **router agent** with `thinking=0` inspects the user's query. It doesn't answer; it classifies. Based on the classification, it delegates to either:

- A **thinking-heavy specialist** for reasoning-intensive queries (math, debugging, planning).
- A **fast specialist** for retrieval-style queries (facts, definitions, simple chat).

This is the M06 composition pattern applied to thinking. Use `AgentTool` so the router calls the specialists like functions and stays in charge of composition. The result: reasoning quality on the queries that need it, low latency on the ones that don't.

```python
# Sketch
router = LlmAgent(
    model="gemini-2.5-flash",
    planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(thinking_budget=0)),
    instruction="Classify the query. Call fast_specialist for lookups, "
                "thinking_specialist for reasoning problems.",
    tools=[AgentTool(agent=fast_specialist),
           AgentTool(agent=thinking_specialist)],
)
```

The router spends zero thinking tokens — its job is pattern-recognition — and delegates the hard problems to the specialist with the budget to solve them.

## Gemini-only property — thought-signature persistence

One more Gemini-only fact worth naming. **Thought signatures persist across multi-turn tool calls** within a conversation.

What that means practically: if the model reasoned through a problem in turn one, and turn two involves a follow-up that depends on the same reasoning, Gemini preserves the reasoning context without re-thinking from scratch. The thinking budget isn't consumed again; the prior reasoning carries through.

No other frontier model ships this as of April 2026. OpenAI's `reasoning_effort` starts fresh each turn. Claude's extended thinking resets. Gemini carries forward.

For agents that have multi-turn tool-heavy conversations on hard problems — coding assistants, research agents, debugging bots — this is meaningful. You pay the reasoning cost once per session, not per turn.

## LiteLLM parity — partial

Other providers ship similar knobs. None are as clean as Gemini's `ThinkingConfig`:

| Provider | Equivalent | Works through LiteLLM? |
|---|---|---|
| **OpenAI** (GPT-5, o3) | `reasoning_effort=low/medium/high` | ✅ Passes through |
| **Anthropic** (Claude 4.5+) | `thinking={"type": "enabled", "budget_tokens": N}` | ⚠️ Works basic; breaks on tool calls |
| **Qwen / DeepSeek** | Reasoning-variant models; some accept `reasoning.effort` | ⚠️ Varies by variant |

If reasoning budgets are a first-class requirement for your agent architecture, native Gemini is where you get the most reliable API. For everything else, LiteLLM's partial parity is fine.

## What to carry forward

- **Thinking is a knob, not a default.** Crank it for hard problems; leave it at 0 for easy ones.
- **`thinking_budget`** (int) is Gemini 2.5's control; **`thinking_level`** (enum) is Gemini 3+'s coarser preset.
- **Cost**: thought tokens billed at the output-token rate. Modest per-invocation cost.
- **`BuiltInPlanner`** plumbs `ThinkingConfig` through to an `LlmAgent` via the `planner=` argument.
- **Production pattern**: router with thinking=0 delegates to specialists (thinking-heavy or fast) per query type.
- **Gemini-only property**: thought signatures persist across multi-turn tool calls. No other frontier model does this.
- **LiteLLM parity is partial.** OpenAI's `reasoning_effort` works cleanly; Claude's thinking breaks on tool calls.

## Your turn

1. **A problem where thinking matters.** Pose a 4-step logic puzzle to both `fast_agent` and `thinking_agent`. Does the fast one miss steps?
2. **Scale the budget.** Agents at budgets 0, 512, 2048, 8192. Hard math problem. At what budget does quality stop improving?
3. **Include thoughts.** Set `include_thoughts=True` in a `ThinkingConfig` and inspect the response. What does the model's internal reasoning look like?

Module 13 — the last of the three Gemini unlocks — covers the **Live API**: bidirectional voice streaming with voice activity detection and interruption. It's the single most differentiated Gemini-only capability on the market as of April 2026. Fair warning: the Live API is genuinely fragile in some environments. If the notebook demo doesn't run end-to-end on your machine, the course's `DEMOS_BROKEN.md` logs the fallback path.
