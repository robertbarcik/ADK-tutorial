# M12 — Speaker notes

---

## Slide 1 — Title

Thinking budgets. The simplest of the three Gemini unlocks: one knob, one number, and a clear effect on reasoning-heavy tasks. This module covers what the knob does, how to set it inside an ADK agent, and when to bother.

---

## Slide 2 — What thinking is

Gemini 2.5 and later models do an internal reasoning pass before producing the final answer. That reasoning is invisible: it doesn't appear in the output, but it shows up in the usage metadata as `thoughts_token_count`, and it costs real wall-clock time.

You set a budget: a ceiling on how many reasoning tokens the model can spend. Gemini uses up to that many tokens thinking before it writes the answer. The diagram shows the flow. A prompt goes in. Up to N invisible reasoning tokens get consumed. Then the final answer comes out. The reasoning is billed separately.

---

## Slide 3 — The knob

The API is `ThinkingConfig(thinking_budget=N)`. Setting it to zero turns reasoning off. Setting it to 2048 or higher enables meaningful reasoning. `include_thoughts=True` makes the reasoning tokens visible in the output, which is useful when you want to debug what the model was working through.

Gemini 3 and later also offer `thinking_level`, with four presets: MINIMAL, LOW, MEDIUM, and HIGH. On 2.5, use the numeric budget. On 3+, either works.

---

### Notebook break — Budget comparison

[Switch the screen to the notebook.]

Cell seven runs the same multi-step profit-margin problem twice: once with `thinking_budget=0`, and once with `thinking_budget=4096`. Same prompt, same model.

Watch three things: the latency, the `thoughts_token_count` in the usage metadata, and the answer quality. The numbers differ between the two runs.

[Switch back to the slide deck.]

---

## Slide 4 — Direct comparison

The numbers confirm the trade-off. Same input: 158 tokens on both runs. Same output length: 702 tokens on both runs.

Budget=0: latency under a second, zero thought tokens. Budget=4096: eleven seconds, 1109 thought tokens consumed. Those 1109 tokens are reasoning the model did internally and never surfaced to the user.

Same prompt, same model, same output length. Different reasoning depth, different latency, different cost.

---

## Slide 5 — The even-better demo

The prime-sum problem makes the quality gap concrete. The question: what is the sum of all primes between 20 and 50?

The fast agent, with thinking=0, answers in under a second and says 255. Wrong.

The thinking agent, with thinking=2048, takes ten seconds. It enumerates 23, 29, 31, 37, 41, 43, 47, sums them, and arrives at 251. Correct.

Same question, same model. Different budget, different answer. The quality delta is visible, not just theoretical.

---

## Slide 6 — BuiltInPlanner code

`BuiltInPlanner(thinking_config=...)` is the ADK wrapper for thinking budgets. Pass it as the `planner` argument on any `LlmAgent`. Everything else stays the same: the name, model, instruction, and tools are unchanged.

The `planner` argument is how ADK exposes features that affect how the model reasons, without bloating the agent constructor.

---

## Slide 7 — When to use thinking

Crank the budget when the problem requires step-by-step working: multi-step calculations, logic puzzles, scheduling, code debugging, dependency analysis, or hard math.

Skip thinking for factual lookups. The model already knows the capital of France; reasoning adds only latency. Skip it for text transformations like summarization, translation, or style rewriting. Skip it for classification tasks.

The heuristic: does the task require the model to work something out, or to retrieve something it already knows? Work it out: crank the budget. Retrieve: skip.

---

## Slide 8 — Production pattern

A practical production pattern routes on query type.

A cheap router agent with `thinking_budget=0` inspects the question and delegates. For hard problems, it calls a thinking-heavy specialist. For easy ones, it calls a fast specialist.

This is the same coordinator-plus-specialists pattern from earlier in the course. Use `AgentTool` so the coordinator stays in charge of the conversation while each specialist handles one class of problem.

You get reasoning quality where you need it, and fast responses where you don't.

---

## Slide 9 — Gemini 3+ levels

Gemini 3 and later offer a preset API alongside the numeric budget. MINIMAL is roughly off. LOW is around a thousand thought tokens. MEDIUM is around four thousand. HIGH is unlimited, with the model deciding how much to think.

Use `thinking_level` when you want a rough setting and don't care about the exact number. Use `thinking_budget` when you want precise control. Both APIs work on 3+.

---

## Slide 10 — Thought signature persistence

Thought signatures persist across multi-turn tool calls in Gemini. If the model reasoned through a problem in turn one and turn two involves a follow-up on the same problem, Gemini carries the reasoning context forward without re-thinking from scratch. The thinking budget isn't spent again.

OpenAI's `reasoning_effort` starts fresh each turn. Claude's extended thinking resets between turns. No other frontier model ships this as of May 2026.

For multi-turn conversations on hard problems, like coding assistants or research agents, this is meaningful. You pay the reasoning cost once per session, not once per turn.

---

## Slide 11 — LiteLLM parity

Other providers ship similar knobs with different vocabularies.

OpenAI GPT-5 and o3 use `reasoning_effort`: a low-medium-high preset. It passes through LiteLLM cleanly.

Anthropic Claude 4.5 and later use extended thinking via `thinking={"type": "enabled", "budget_tokens": N}`. It works through LiteLLM for basic calls, but breaks on tool-call turns. If you need thinking on Claude with tools, check the LiteLLM issue tracker before shipping.

Qwen and DeepSeek offer reasoning-variant models where reasoning is on by default, with some accepting a `reasoning.effort` parameter.

None match the reliability of Gemini's `ThinkingConfig` for tool-heavy agents. If reasoning control is a first-class requirement, native Gemini is where the API is most consistent.

---

## Slide 12 — Carry forward

Thinking is a knob, not a default. Crank it for hard problems. Leave it at zero for easy ones. Route per query using the coordinator-plus-specialists pattern from earlier in the course.

---

## Slide 13 — Next

Next up: the Live API. Bidirectional audio streaming, voice in and voice out, with voice activity detection and interruption handling. The most differentiated Gemini capability on the market as of May 2026. Fair warning: the Live API is the most fragile of the three unlocks. If the demo doesn't run in your environment, check `DEMOS_BROKEN.md` for the fallback path.
