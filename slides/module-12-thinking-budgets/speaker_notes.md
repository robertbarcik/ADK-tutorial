# M12 — Speaker notes

---

## Slide 1 — Title

Welcome to module twelve — thinking budgets, the second Gemini-only unlock in Part 2. This one is simpler than grounding and caching. It's really just one knob, but that knob has a big effect on reasoning-heavy tasks. Let's get into it.

---

## Slide 2 — What thinking is

Let me walk through what thinking actually is. Gemini 2.5 and later models do an internal reasoning pass before they produce the final answer. You don't see that reasoning in the text — it's not part of the output field. Instead, it's counted separately as `thoughts_token_count` in the usage metadata, and it takes real wall-clock time.

So you set a budget — a ceiling on how many internal reasoning tokens the model can spend — and Gemini spends up to that much thinking before it writes its answer.

The picture looks like this. A user prompt goes in. Up to N invisible reasoning tokens get consumed internally. Then the final answer comes out. The reasoning is billed separately, and it never appears in what the user reads.

---

## Slide 3 — The knob

In code, the API looks like this — `ThinkingConfig(thinking_budget=N, include_thoughts=False)`. Setting `thinking_budget=0` turns reasoning off, while `thinking_budget=2048` or higher enables real reasoning. And `include_thoughts=True` makes the reasoning tokens visible in the output, which is useful for debugging.

Gemini 3 and later also add a coarser control called `thinking_level`, with four presets — MINIMAL, LOW, MEDIUM, and HIGH. So on 3-plus, use whichever fits your preference for explicit control versus preset simplicity.

---

## Slide 4 — Live: budget comparison

Time to see it in action. Switch to the notebook, cell seven. We run the same multi-step profit-margin problem twice — once with `thinking_budget=0`, and once with `thinking_budget=4096`. Same prompt, same model. Watch the latency, the thought-token count, and the answer quality.

---

## Slide 5 — Direct comparison

Back on the slide. This is what you just saw. Same input tokens — 158 on both runs. Same output tokens — 702 on both runs.

With budget=0, the latency is under a second, and zero thought tokens get consumed.

With budget=4096, on the other hand, latency jumps to eleven seconds, and 1109 thought tokens get consumed — well within the budget, but still substantial reasoning.

So same inputs, same outputs, but a big latency and token gap between them. Those 1109 thought tokens are reasoning the model did internally that never reached the user.

---

## Slide 6 — Prime-sum demo

The even better demo comes from cell ten. A simple question — what's the sum of primes between 20 and 50?

First, fast_agent, with thinking=0. It answers in under a second and says 255. That's wrong.

Second, thinking_agent, with thinking=2048. It takes ten seconds. It enumerates the primes — 23, 29, 31, 37, 41, 43, 47 — sums them, and arrives at 251. Correct.

So one agent got the right answer, and the other got a wrong answer. The only difference between them was the thinking budget. That's the reasoning quality delta, made visible.

---

## Slide 7 — BuiltInPlanner code

In code, wiring this into an ADK agent looks like this — `BuiltInPlanner(thinking_config=...)` passed as the `planner` argument. Everything else about the agent — the name, the model, the instruction, the tools — works the same way we've been doing it for twelve modules.

The planner is how ADK exposes features that affect how the model thinks, without bloating the agent constructor. Future planners can add other pre-reasoning patterns; for today, it's the thinking budget.

---

## Slide 8 — When to use thinking

So when does thinking earn its keep? Crank the budget for multi-step reasoning — things like the profit-margin problem, logic puzzles, scheduling, or dependency-aware planning. Crank it for code debugging, where the model has to trace logic. And crank it for hard math, proofs, or arithmetic problems.

On the other hand, skip thinking for factual lookups like "capital of France" — the model already knows, so no reasoning is needed. Skip it for text transformations such as summarization, translation, or style rewriting — those are pattern matches, not reasoning. And skip it for simple classification, like spam detection.

So the heuristic is this — does the problem require the model to work something out step by step? Crank the budget. Does it require the model to retrieve something it already knows? Skip.

---

## Slide 9 — Production pattern

A practical production pattern looks like this — route on query type.

A cheap, fast router agent with thinking=0 inspects the user's question. It doesn't answer; it just decides which specialist to call. Then it delegates — to a thinking-heavy agent for hard problems, or to a fast agent for easy ones.

You already know how to build this — it's really the M06 composition pattern. A coordinator, plus two specialists: one thinking-heavy, one fast. Use `AgentTool` so the coordinator calls them like functions and stays in charge of the conversation.

The payoff is that you get the reasoning quality of a thinking-heavy agent for the queries that need it, and the latency of a fast agent for the queries that don't. Best of both worlds, per query.

---

## Slide 10 — Gemini 3+ levels

On Gemini 3 and later, there's a coarser preset-based API. `thinking_level=MINIMAL` is roughly off. LOW is about a thousand thought tokens. MEDIUM is about four thousand. And HIGH is unlimited — the model decides how much to think on its own.

So the rule of thumb is this. Use levels on 3+ when you don't care about the exact number. Use budgets on 2.5 or 3+ when you want precise control. Both APIs coexist on 3+.

---

## Slide 11 — Thought signature persistence

There's one more Gemini-only property worth naming — thought signatures persist across multi-turn tool calls in a conversation.

What that means practically is this. If the model reasoned through a problem in turn one, and turn two involves a follow-up question that depends on the same reasoning, Gemini preserves the reasoning context without re-thinking from scratch. As a result, the thinking budget isn't spent again — the prior reasoning just carries through.

No other frontier model ships this as of April 2026. OpenAI's reasoning_effort starts fresh each turn. Claude's extended thinking resets. Gemini, on the other hand, carries forward.

So for agents that have multi-turn tool-heavy conversations on hard problems — things like coding assistants, research agents, or debugging bots — this is meaningful. You pay the reasoning cost once per session, and not per turn.

---

## Slide 12 — LiteLLM parity

Other providers ship similar knobs, just with different vocabularies.

First, OpenAI GPT-5 and o3 have `reasoning_effort` — a low-medium-high preset. It passes through LiteLLM cleanly, so you set it in the same place you'd set thinking_level on Gemini.

Second, Anthropic's Claude 4.5 and later have extended thinking via `thinking={"type": "enabled", "budget_tokens": N}`. It's partial through LiteLLM — which means it works for basic reasoning calls, but it breaks on calls that involve tools. If you need thinking on Claude with tool calls, check the LiteLLM issue tracker.

And finally, Qwen and DeepSeek have reasoning-variant models where reasoning is on by default. Some accept a `reasoning.effort` parameter; it varies.

None of these are as clean as Gemini's `ThinkingConfig`. So if reasoning control is a first-class requirement for your agent, native Gemini is where you get the most reliable API for it.

---

## Slide 13 — Carry forward

So what should you carry forward from today? Thinking is a knob, not a default. Crank it for hard problems. Leave it at zero for easy ones. And route per query via M06 composition.

---

## Slide 14 — Next

Up next in module thirteen — the third and final Gemini unlock, the Live API voice agent. Bidirectional audio streaming — voice in, voice out — with voice activity detection and interruption handling. Genuinely the most differentiated capability on the market as of April 2026. Fair warning, though: the Live API is the most fragile of the three unlocks. If the demo doesn't run in your environment, there's a DEMOS_BROKEN.md entry with the fallback path. See you there.
