# M11 — Speaker notes

---

## Slide 1 — Title

Grounding and context caching. Both are Gemini-specific, neither translates through LiteLLM, and together they cover the first two unlocks Part 2 is about. You get real capability in exchange for real lock-in, and this module makes the trade-off concrete.

---

## Slide 2 — Part 1 vs Part 2 framing

Part 1 was vendor-neutral ADK. Any model, any provider, everything running through LiteLLM. Part 2 shows what native Gemini unlocks that the wrapper can't provide. Three capabilities are in scope. This module covers the first two. The others follow in the coming modules.

---

## Slide 3 — The switch is mechanical

The code change from Part 1 to Part 2 is one line. Instead of wrapping the model in `LiteLlm(...)`, you pass a plain string: `model="gemini-2.5-flash"`. Everything else is identical: tools, sessions, workflow agents, callbacks, memory services, eval. Only the model argument changes.

---

## Slide 4 — Three unlocks

Three Gemini-specific capabilities are in scope for Part 2. This module covers the first two.

Google Search grounding: real citations with real URLs, handled by Gemini's grounding infrastructure. No external search API to manage.

Long context plus caching: one-million-token windows, with a 75 to 90 percent discount when the same content is reused across queries.

The other two unlocks follow in the coming modules. Thinking budgets: a knob that controls how much internal reasoning the model does before answering. And the Live API: bidirectional voice streaming with interruption handling.

All four require native Gemini and a Google AI Studio key. None translate through LiteLLM.

---

## Slide 5 — Grounding header

First unlock: Google Search grounding. A built-in tool that returns real citations.

---

## Slide 6 — Add google_search

`google_search` is a function you import from `google.adk.tools` and add to the agent's `tools=` list. That's the full integration.

Notice what's absent. There's no API key to manage, no client library to install, and no result-parser function to write. Gemini handles Search internally because `google_search` is a built-in tool, not a Python function that ADK dispatches. You declare intent, and Gemini does the work.

---

### Notebook break — Grounding in action

[Switch the screen to the notebook.]

Open cell eight. The agent is already configured with `google_search` in its tools list. Run cell nine to send a factual question about a capital city and its current population, then watch the event stream.

Two things to notice. First, there's no `tool_call` event for `google_search`. It's a built-in, so Gemini handles the dispatch internally rather than through ADK's tool-call loop. Second, look at the grounding metadata at the bottom of the output. Those are real URLs that Gemini consulted to back the response. Seven sources for one population query.

[Switch back to the slide deck.]

---

## Slide 7 — What you saw

The output shows what citation-grade sourcing looks like. The capital city, population figures from multiple sources, and seven grounding sources with real URLs pointing to Wikipedia, Britannica, and others.

In production, you surface these to your users. A line like "Source: Wikipedia" underneath each paragraph. The user sees where each claim came from and can verify it. That's the difference between AI-confident guessing and grounded output.

---

## Slide 8 — Cost reality

Two cost-adjacent gotchas before moving to caching.

First, Search is billed separately from tokens. Roughly thirty-five dollars per thousand grounded requests, charged per-request rather than per-token. For an agent doing a hundred grounded queries a day, that's over a hundred dollars a month. Budget accordingly.

Second, built-in tools (`google_search`, `BuiltInCodeExecutor`, Vertex AI Search) cannot coexist with regular function tools in the same agent. The Gemini API rejects the request. Two workarounds: wrap each built-in as a sub-agent via `AgentTool`, with each sub-agent holding one built-in. Or, on ADK 1.16 and later, `google_search` accepts `bypass_multi_tools_limit=True`, which lets it mix with regular tools.

---

## Slide 9 — Caching header

Second unlock: long context plus context caching.

---

## Slide 10 — 1M tokens

Gemini 2.5 and later models handle up to one million input tokens, with two million on the Pro variants. A 500-page PDF manual, an entire codebase, or months of email history all fit in one context window. The capability is real. The economics, though, need attention.

---

## Slide 11 — Economics problem

Here are the numbers. A 100-page PDF is roughly fifty thousand tokens. Twenty questions against it, which is a normal rate for a support agent over a PDF manual, means re-sending those fifty thousand tokens on every question. At Gemini 2.5 Flash's standard input rate, that's seven-and-a-half cents per hour per user. Cheap at one user, expensive at scale.

Context caching fixes this by letting you pay once to cache the document, then reuse it at a steep discount.

---

## Slide 12 — Two caching flavors

Caching comes in two flavors.

Implicit caching is automatic. Zero code change. Gemini detects repeated prefixes and applies a seventy-five-percent discount to the cached portion. You don't control what gets cached or for how long. It's free for all 2.5 models.

Explicit caching requires a `client.caches.create` call with the content and a TTL. You get a ninety-percent discount on the cached portion, full control over what's cached and for how long, and a small storage fee per cached token per hour.

Implicit wins when you're not sure you'll reuse the content. Explicit wins when you know you'll ask many questions against the same content over a defined window.

---

## Slide 13 — Explicit caching API

The `client.caches.create` call takes your content and a TTL, and returns a cache handle. Subsequent `generate_content` calls pass `cached_content=cache.name`, and the cached content is billed at the discounted rate.

Two constraints to keep in mind. First, the minimum cache size is around thirty-two thousand tokens. Below that, the storage cost exceeds the savings. Second, explicit caching requires a paid Gemini API tier. The free tier has a zero-token storage quota. The notebook cell demonstrating this will return a 429 error on a free key. The code is correct; it just won't execute without a paid account.

---

## Slide 14 — Worked example

The worked example uses 100 pages and 20 queries per hour. Without caching: seven-and-a-half cents per hour. With explicit caching: about one-and-a-third cents, combining the one-time cache-creation cost, the per-query discounted read, and one hour of storage. That's a six-times cost reduction.

The savings scale. At 100 queries per hour against the same document, the gap widens to thirty times or more.

Break-even: below three-to-five queries per document per hour, implicit caching is free and covers most of the benefit. Above that, explicit is worth the setup code.

---

## Slide 15 — Native vs LiteLLM header

Native Gemini versus LiteLLM-wrapped. The trade-off is real, and worth making explicit.

---

## Slide 16 — Feature matrix

The feature matrix on the slide splits into two columns. Basic chat and tool calls work either way. `google_search`, context caching, thinking budgets, and the Live API are native-only. LiteLLM can't surface features that don't exist in the OpenAI-shaped interface it wraps.

LiteLLM's advantage is one-line model swaps. Swap to Claude, GPT, or Qwen by changing a string. That's the vendor-neutrality pattern from earlier in the course.

The two are not alternatives. Use native Gemini when you need a feature that doesn't translate through LiteLLM. Use LiteLLM-wrapped for everything else.

---

## Slide 17 — Production pattern

The production pattern is to have both.

Routine user-facing queries go through a LiteLLM-wrapped agent. Portable, with multi-model failover. When a provider has an outage, you swap models without touching the agent code.

Search, long-context, and voice queries go through a native Gemini agent. Locked to Google, and in return you get grounding, caching, and the Live API, which nothing else provides.

You combine them with `sub_agents` or `AgentTool`. The coordinator routes each query to the right specialist. The architecture is the same multi-agent pattern from earlier in the course.

---

## Slide 18 — Next

Next up: thinking budgets. A Gemini-only control that trades latency for reasoning quality. The same question at minimum budget gets an instant response that may be wrong. At maximum budget, it gets a slower response that's much more likely to be right. The next module runs the same math problem at both settings and measures the difference.
