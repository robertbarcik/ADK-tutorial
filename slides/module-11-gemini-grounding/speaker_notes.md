# M11 — Speaker notes

---

## Slide 1 — Title

Module eleven. Part 2 of the course starts here. Google Search grounding, context caching. The first two of three Gemini unlocks — features that don't translate through LiteLLM, features that give you real capability in exchange for real lock-in.

---

## Slide 2 — Part 1 vs Part 2 framing

The framing. Part 1 taught vendor-neutral ADK. Everything ran on whichever model you picked. Part 2 is honest about what you give up by staying neutral — three specific Gemini capabilities that nothing else in the market replicates. Today: grounding and context caching. Module twelve: thinking budgets. Module thirteen: Live API voice.

---

## Slide 3 — The switch is mechanical

The code change from Part 1 to Part 2 is one line. Instead of wrapping the model in `LiteLlm(...)`, you pass a plain string. `model="gemini-2.5-flash"`. Done. Everything else — tools, sessions, workflow agents, callbacks, memory services, eval — works exactly the same. Only the model argument changes.

---

## Slide 4 — Three unlocks

Three Gemini unlocks the course covers.

Google Search grounding — today. Real citations with real URLs, handled by Gemini's grounding infrastructure, not a search API you call yourself.

Long context plus caching — today. One-million-token windows; 75-90% discount on cached content.

Thinking budgets — module twelve. A knob that trades latency for reasoning quality.

Live API voice — module thirteen. Bidirectional audio streaming with interruption handling.

None of these translate through LiteLLM. All require native Gemini via google-genai. That means switching your API key from OpenRouter to Google AI Studio. Free tier is enough for the first two features; caching needs paid tier; Live API has its own quotas.

---

## Slide 5 — Grounding header

First unlock. Google Search grounding. Built-in tool. Real citations.

---

## Slide 6 — Add google_search

Here's the code. Import `google_search` from `google.adk.tools`. Add it to the agent's `tools=` list. That's the entire integration.

Notice what's NOT there. No search API key. No client library for Google's Custom Search API. No function that parses results. Gemini handles Search internally — the tool is *built-in*, not a Python function ADK dispatches. You register intent; Gemini does the work.

---

## Slide 7 — Live: grounding

Switch to the notebook. Cell nine. Ask about the capital of Slovakia and its current population. Watch the event stream. Notice two things: no explicit `tool_call` for google_search — because it's a built-in, handled internally. And the grounding metadata at the bottom — the real URLs Gemini consulted. Seven sources for a population query.

---

## Slide 8 — What you saw

Back on the slide. Bratislava — the capital. Multiple population figures from different sources. Seven grounding sources attached to the event — Wikipedia, Britannica, and others. Real URLs. Not hallucinations.

In production, you surface these to your users. "Source: Wikipedia (see full article at ...)" underneath each paragraph. That's what transparent grounding looks like — the user sees where the claims came from and can verify them.

---

## Slide 9 — Cost reality

Two cost-adjacent gotchas worth flagging.

Search is billed separately from tokens. Roughly thirty-five dollars per thousand grounded requests. Not per-token; per-request. For a search-heavy agent doing a hundred grounded queries a day, that's three-fifty a day, over a hundred a month. Budget accordingly.

Second gotcha. Built-in tools — google_search, BuiltInCodeExecutor, Vertex AI Search — cannot coexist with regular function tools in the same agent. If you try to add `get_weather` alongside `google_search`, the Gemini API rejects the request.

Two workarounds. One — wrap each built-in tool as a sub-agent via AgentTool. The parent has only AgentTool wrappers; each sub-agent has one focused built-in. Two — on ADK one-point-sixteen and later, `google_search` specifically accepts `bypass_multi_tools_limit=True`, which lets it mix with regular tools. Check your ADK version.

---

## Slide 10 — Caching header

Second unlock. Long context plus context caching.

---

## Slide 11 — 1M tokens

Gemini 2.5 and later models handle up to one million input tokens. Two million on the Pro variants. Enough for a 500-page PDF manual. Enough for an entire codebase. Enough for months of email history.

The capability is impressive. The economics are the issue.

---

## Slide 12 — Economics problem

Here's the economics problem, concretely. A 100-page PDF is roughly fifty thousand tokens. Twenty questions against it — normal for a support agent over a PDF manual — means twenty times fifty thousand input tokens, which is one million input tokens per hour. At Gemini 2.5 Flash's standard input rate, that's seven-and-a-half cents per hour per user. Cheap at one user; adds up fast at scale.

The obvious fix: don't re-pay for the PDF on every question. Cache it once, reuse cheaply. That's what context caching does.

---

## Slide 13 — Two flavors

Two flavors. Implicit and explicit.

Implicit caching. Automatic. Zero code change. Gemini detects repeated prefixes in your requests and applies a seventy-five-percent discount to the cached portion. You don't control what's cached or for how long; Gemini decides. Free to everyone on 2.5 and later.

Explicit caching. You call `client.caches.create` with the content you want cached and a TTL. Ninety-percent discount on the cached portion. You control what's in the cache, how long it lives, when to delete. Costs a small storage fee per cached token per hour.

Implicit wins for "I might ask more questions about this document later." Explicit wins for "I know for certain I'll ask many questions about this specific document over the next five minutes."

---

## Slide 14 — Explicit caching API

Here's the API. `client.caches.create` takes your content and a TTL. Returns a cache handle. Subsequent `generate_content` calls pass `cached_content=cache.name`, and the cached content is billed at the discounted rate.

Minimum cache size is around thirty-two thousand tokens. Below that, caching won't happen — the break-even against the storage cost doesn't work.

And one crucial caveat. Explicit caching requires a paid Gemini API tier. The free tier has a zero-token storage quota. The notebook cell demonstrating this runs, gets a 429 rate-limit error, and explains the billing gate. The code itself is correct; it just won't execute on a free key.

---

## Slide 15 — Worked example

The numbers, concretely. 100-page PDF. 20 questions per hour.

No caching — seven-and-a-half cents per hour.

With explicit caching — about one-and-a-third cents per hour, combining the one-time cache-creation cost, the per-query cached-read cost, and the one-hour storage cost.

Roughly six-times cost reduction at 20 queries per hour. The savings scale as you ask more questions. At 100 queries per hour per PDF, the gap widens to thirty times or more.

The break-even. Below three-to-five queries per document per hour, implicit caching — which is free and automatic — gets you most of the savings. Above that, explicit is clearly worth the extra code.

---

## Slide 16 — Native vs LiteLLM header

Pick your battle. Native Gemini versus LiteLLM-wrapped. An honest trade-off.

---

## Slide 17 — Feature matrix

The matrix. Basic chat and tool calls work either way. Everything else — google_search, BuiltInCodeExecutor, caching, thinking budgets from module twelve, Live API from module thirteen — is native-only. LiteLLM can't translate features that don't exist in the OpenAI-shaped interface.

The one thing LiteLLM wins at: swapping to Claude, GPT, or Qwen in a single line. That's the whole vendor-neutrality story from module four.

The rule. Native Gemini when you need a feature that doesn't translate. Otherwise LiteLLM. The two are not alternatives; they're different tools for different jobs.

---

## Slide 18 — Production pattern

The production pattern, on one slide. Have both.

Your routine user-facing queries go through a LiteLLM-wrapped agent. Portable. Multi-model failover. When OpenAI has an outage, you swap to Claude or Gemini; your code doesn't know. When a particular task benefits from a particular model, you route per-task.

Your search, long-context, voice queries go through a native Gemini agent. Locked to Google. But you get grounding, caching, Live API — capabilities nothing else provides.

Combine them with sub_agents or AgentTool from module six. The coordinator decides which kind of agent to reach for based on the query. The architecture is already familiar from Part 1.

---

## Slide 19 — Next

Module twelve. Thinking budgets. A Gemini-only knob that trades latency for reasoning quality. Same question, minimum thinking budget — instant response, maybe wrong. Maximum thinking budget — slower response, probably right. We'll run the same math problem at both and see the answer quality change along with the latency cost.
