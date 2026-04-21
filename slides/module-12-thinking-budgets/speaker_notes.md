# M12 — Speaker notes

---

## Slide 1 — Title

Module twelve. Thinking budgets. The second Gemini-only unlock in Part 2. Simpler than grounding and caching; one knob, big effect on reasoning-heavy tasks.

---

## Slide 2 — What thinking is

Gemini 2.5 and later models do an internal reasoning pass before they produce the final answer. You don't see the reasoning in the text — it's not part of the output field. It's counted separately as `thoughts_token_count` in the usage metadata, and it takes real wall-clock time.

You set a budget — a ceiling on how many internal reasoning tokens the model can spend — and Gemini spends up to that much thinking before writing its answer.

The picture: user prompt goes in. Up to N invisible reasoning tokens get consumed internally. Then the final answer comes out. The reasoning is billed separately and doesn't appear in what the user reads.

---

## Slide 3 — The knob

The API. `ThinkingConfig(thinking_budget=N, include_thoughts=False)`. `thinking_budget=0` turns reasoning off; `thinking_budget=2048` or higher enables real reasoning. `include_thoughts=True` makes the reasoning tokens visible in the output — useful for debugging.

Gemini 3 and later add a coarser control, `thinking_level`, with MINIMAL, LOW, MEDIUM, HIGH presets. On 3-plus use whichever fits your preference for explicit control versus preset simplicity.

---

## Slide 4 — Live: budget comparison

Switch to the notebook. Cell seven. We run the same multi-step profit-margin problem twice — once with `thinking_budget=0`, once with `thinking_budget=4096`. Same prompt. Same model. Watch the latency, the thought-token count, and the answer quality.

---

## Slide 5 — Direct comparison

Back on the slide. Here's what you saw. Same input tokens — 158 both runs. Same output tokens — 702 both runs. 

With budget=0: latency under a second, zero thought tokens.

With budget=4096: eleven seconds of latency, 1109 thought tokens consumed — well within the budget but still substantial reasoning.

Same inputs, same outputs, big latency and token gap. The 1109 thought tokens are reasoning the model did internally that never reached the user.

---

## Slide 6 — Prime-sum demo

The even better demo, from cell ten. Simple question: what's the sum of primes between 20 and 50?

fast_agent with thinking=0: answers in under a second. Says 255. That's wrong.

thinking_agent with thinking=2048: takes ten seconds. Enumerates the primes — 23, 29, 31, 37, 41, 43, 47 — sums them, arrives at 251. Correct.

One agent got the right answer; the other got a wrong answer. The difference was the thinking budget. That's the reasoning quality delta, made visible.

---

## Slide 7 — BuiltInPlanner code

Wiring it into an ADK agent. `BuiltInPlanner(thinking_config=...)` passed as the `planner` argument. Everything else about the agent — name, model, instruction, tools — works the same way we've been doing it for twelve modules.

The planner is how ADK exposes features that affect how the model thinks, without adding them to the agent constructor. Future planners can add other pre-reasoning patterns; today, it's the thinking budget.

---

## Slide 8 — When to use thinking

When thinking earns its keep. Crank the budget for multi-step reasoning — the profit-margin problem, logic puzzles, scheduling, dependency-aware planning. Crank it for code debugging where the model has to trace logic. Crank it for hard math, proofs, arithmetic problems.

Skip thinking for factual lookups — "capital of France" — the model already knows; no reasoning needed. Skip it for text transformations — summarization, translation, style rewriting — those are pattern matches, not reasoning. Skip it for simple classification like spam detection.

The heuristic: does the problem require the model to work something out step by step? Crank the budget. Does it require the model to retrieve something it already knows? Skip.

---

## Slide 9 — Production pattern

The production pattern on one slide. Route on query type.

A cheap, fast router agent with thinking=0 inspects the user's question. It doesn't answer; it just decides which specialist to call. Then it delegates — to a thinking-heavy agent for hard problems, to a fast agent for easy ones.

You already know how to build this. It's the M06 composition pattern. A coordinator, two specialists — one thinking-heavy, one fast. Use `AgentTool` so the coordinator calls them like functions and stays in charge of the conversation.

Payoff: you get the reasoning quality of a thinking-heavy agent for the queries that need it, and the latency of a fast agent for the queries that don't. Best of both worlds, per query.

---

## Slide 10 — Gemini 3+ levels

On Gemini 3 and later, a coarser preset-based API. `thinking_level=MINIMAL` is roughly off. LOW is about a thousand thought tokens. MEDIUM is about four thousand. HIGH is unlimited — the model decides how much to think.

Use levels on 3+ when you don't care about the exact number. Use budgets on 2.5 or 3+ when you want precise control. Both APIs coexist on 3+.

---

## Slide 11 — Thought signature persistence

One more Gemini-only property worth naming. Thought signatures persist across multi-turn tool calls in a conversation.

What that means practically: if the model reasoned through a problem in turn one, and turn two involves a follow-up question that depends on the same reasoning, Gemini preserves the reasoning context without re-thinking from scratch. The thinking budget isn't spent again; the prior reasoning carries through.

No other frontier model ships this as of April 2026. OpenAI's reasoning_effort starts fresh each turn. Claude's extended thinking resets. Gemini carries forward.

For agents that have multi-turn tool-heavy conversations on hard problems — coding assistants, research agents, debugging bots — this is meaningful. You pay the reasoning cost once per session, not per turn.

---

## Slide 12 — LiteLLM parity

Other providers ship similar knobs with different vocabularies.

OpenAI GPT-5 and o3 have `reasoning_effort` — a low-medium-high preset. Passes through LiteLLM cleanly; you set it in the same place you'd set thinking_level on Gemini.

Anthropic's Claude 4.5 and later have extended thinking via `thinking={"type": "enabled", "budget_tokens": N}`. Partial through LiteLLM — works for basic reasoning calls, breaks on calls that involve tools. If you need thinking on Claude with tool calls, check the LiteLLM issue tracker.

Qwen and DeepSeek have reasoning-variant models where reasoning is on by default. Some accept a `reasoning.effort` parameter; varies.

None are as clean as Gemini's `ThinkingConfig`. If reasoning control is a first-class requirement for your agent, native Gemini is where you get the most reliable API for it.

---

## Slide 13 — Carry forward

What to carry forward. Thinking is a knob, not a default. Crank it for hard problems. Leave it at zero for easy ones. Route per query via M06 composition.

---

## Slide 14 — Next

Module thirteen. The third and final Gemini unlock. Live API voice agent. Bidirectional audio streaming — voice in, voice out — with voice activity detection and interruption handling. Genuinely the most differentiated capability on the market as of April 2026. Fair warning: the Live API is the most fragile of the three unlocks. If the demo doesn't run in your environment, there's a DEMOS_BROKEN.md entry with the fallback path. See you there.
