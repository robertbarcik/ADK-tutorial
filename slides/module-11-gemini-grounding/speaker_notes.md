# M11 — Speaker notes

---

## Slide 1 — Title

Welcome to module eleven, and this is where Part 2 of the course starts. We're going to cover Google Search grounding and context caching — the first two of three Gemini unlocks. These are features that don't translate through LiteLLM, which means they give you real capability in exchange for real lock-in.

---

## Slide 2 — Part 1 vs Part 2 framing

Let me frame Part 1 against Part 2 before we dive in. Part 1 taught vendor-neutral ADK, so everything ran on whichever model you picked. Part 2, on the other hand, is honest about what you give up by staying neutral — so three specific Gemini capabilities that nothing else in the market replicates. Today we'll do grounding and context caching. Module twelve is thinking budgets. And module thirteen is the Live API for voice.

---

## Slide 3 — The switch is mechanical

The code change from Part 1 to Part 2 is really just one line. Instead of wrapping the model in `LiteLlm(...)`, you pass a plain string — `model="gemini-2.5-flash"`. Done. Everything else works exactly the same — tools, sessions, workflow agents, callbacks, memory services, eval. Only the model argument changes.

---

## Slide 4 — Three unlocks

There are three Gemini unlocks the course covers, so let me walk through them.

First, Google Search grounding — that's today. You get real citations with real URLs, handled by Gemini's grounding infrastructure, rather than a search API you call yourself.

Second, long context plus caching — also today. So one-million-token windows, and a 75 to 90 percent discount on cached content.

And third, thinking budgets — that's module twelve. A knob that trades latency for reasoning quality.

On top of those three, the Live API for voice lands in module thirteen — bidirectional audio streaming with interruption handling.

None of these translate through LiteLLM. They all require native Gemini via google-genai, which means switching your API key from OpenRouter to Google AI Studio. The free tier is enough for the first two features; caching needs paid tier; and the Live API has its own quotas.

---

## Slide 5 — Grounding header

On to the first unlock — Google Search grounding. Built-in tool, and real citations.

---

## Slide 6 — Add google_search

In code, the integration is really just two steps. You import `google_search` from `google.adk.tools`, and add it to the agent's `tools=` list. That's the entire integration.

Notice what's NOT there. There's no search API key. No client library for Google's Custom Search API. And no function that parses results. Gemini handles Search internally — the tool is *built-in*, which means it's not a Python function that ADK dispatches. You register intent, and Gemini does the work.

---

## Slide 7 — Live: grounding

Switch to the notebook, cell nine. We'll ask about the capital of Slovakia and its current population, and watch the event stream. Notice two things. First, there's no explicit `tool_call` for google_search — because it's a built-in, so it's handled internally. And second, look at the grounding metadata at the bottom — those are the real URLs Gemini consulted. Seven sources just for a population query.

---

## Slide 8 — What you saw

Back on the slide, let's unpack what that output actually contained. Bratislava — the capital. Multiple population figures from different sources. Seven grounding sources attached to the event — things like Wikipedia, Britannica, and others. Real URLs. Not hallucinations.

In production, you surface these to your users. Something like "Source: Wikipedia (see full article at ...)" underneath each paragraph. That's what transparent grounding looks like — the user sees where the claims came from, and can verify them.

---

## Slide 9 — Cost reality

Before we move on, there are two cost-adjacent gotchas worth flagging.

First, Search is billed separately from tokens. Roughly thirty-five dollars per thousand grounded requests. Not per-token; per-request. So for a search-heavy agent doing a hundred grounded queries a day, that's three-fifty a day, over a hundred a month. Budget accordingly.

Second, built-in tools — so google_search, BuiltInCodeExecutor, and Vertex AI Search — cannot coexist with regular function tools in the same agent. If you try to add `get_weather` alongside `google_search`, the Gemini API rejects the request.

There are two workarounds. First, wrap each built-in tool as a sub-agent via AgentTool. The parent has only AgentTool wrappers, and each sub-agent has one focused built-in. Second, on ADK one-point-sixteen and later, `google_search` specifically accepts `bypass_multi_tools_limit=True`, which lets it mix with regular tools. So check your ADK version.

---

## Slide 10 — Caching header

On to the second unlock — long context plus context caching.

---

## Slide 11 — 1M tokens

Gemini 2.5 and later models handle up to one million input tokens. Two million on the Pro variants. That's enough for a 500-page PDF manual. Enough for an entire codebase. Enough for months of email history.

The capability is impressive. The economics, on the other hand, are the issue.

---

## Slide 12 — Economics problem

Let me put concrete numbers on that economics problem. A 100-page PDF is roughly fifty thousand tokens. Twenty questions against it — which is normal for a support agent over a PDF manual — means twenty times fifty thousand input tokens, so one million input tokens per hour. At Gemini 2.5 Flash's standard input rate, that's seven-and-a-half cents per hour per user. Cheap at one user; adds up fast at scale.

The obvious fix is to not re-pay for the PDF on every question. Cache it once, and reuse it cheaply. That's what context caching does.

---

## Slide 13 — Two flavors

Caching comes in two flavors — implicit and explicit.

Implicit caching is automatic. Zero code change. Gemini detects repeated prefixes in your requests, and applies a seventy-five-percent discount to the cached portion. You don't control what's cached or for how long; Gemini decides. And it's free to everyone on 2.5 and later.

Explicit caching, on the other hand, is where you call `client.caches.create` with the content you want cached and a TTL. You get a ninety-percent discount on the cached portion. You control what's in the cache, how long it lives, and when to delete. It does cost a small storage fee per cached token per hour.

So the rule of thumb is this. Implicit wins for "I might ask more questions about this document later." Explicit wins for "I know for certain I'll ask many questions about this specific document over the next five minutes."

---

## Slide 14 — Explicit caching API

In code, the explicit caching API looks like this. `client.caches.create` takes your content and a TTL, and returns a cache handle. Subsequent `generate_content` calls pass `cached_content=cache.name`, and as a result the cached content is billed at the discounted rate.

The minimum cache size is around thirty-two thousand tokens. Below that, caching won't happen — the break-even against the storage cost just doesn't work.

And one crucial caveat. Explicit caching requires a paid Gemini API tier. The free tier has a zero-token storage quota. So the notebook cell demonstrating this runs, gets a 429 rate-limit error, and explains the billing gate. The code itself is correct; it just won't execute on a free key.

---

## Slide 15 — Worked example

Let me put concrete numbers on the savings. 100-page PDF, 20 questions per hour.

With no caching — seven-and-a-half cents per hour.

With explicit caching — about one-and-a-third cents per hour, combining the one-time cache-creation cost, the per-query cached-read cost, and the one-hour storage cost.

So roughly a six-times cost reduction at 20 queries per hour. And the savings scale as you ask more questions. At 100 queries per hour per PDF, the gap widens to thirty times or more.

Now for the break-even. Below three-to-five queries per document per hour, implicit caching — which is free and automatic — gets you most of the savings. Above that, explicit is clearly worth the extra code.

---

## Slide 16 — Native vs LiteLLM header

Time to pick your battle — native Gemini versus LiteLLM-wrapped. An honest trade-off.

---

## Slide 17 — Feature matrix

What you see on this slide is the feature matrix. Basic chat and tool calls work either way. Everything else — so google_search, BuiltInCodeExecutor, caching, thinking budgets from module twelve, and the Live API from module thirteen — is native-only. LiteLLM can't translate features that don't exist in the OpenAI-shaped interface.

The one thing LiteLLM wins at is swapping to Claude, GPT, or Qwen in a single line. That's the whole vendor-neutrality story from module four.

So the rule is this. Native Gemini when you need a feature that doesn't translate. Otherwise LiteLLM. The two are not alternatives; they're different tools for different jobs.

---

## Slide 18 — Production pattern

If you remember one thing about the production pattern, remember this — have both.

Your routine user-facing queries go through a LiteLLM-wrapped agent. It's portable, with multi-model failover. When OpenAI has an outage, you swap to Claude or Gemini, and your code doesn't know. When a particular task benefits from a particular model, you route per-task.

Your search, long-context, and voice queries, on the other hand, go through a native Gemini agent. It's locked to Google — but in turn you get grounding, caching, and the Live API, capabilities that nothing else provides.

You combine them with sub_agents or AgentTool from module six. The coordinator decides which kind of agent to reach for, based on the query. The architecture is already familiar from Part 1.

---

## Slide 19 — Next

Up next is module twelve — thinking budgets. A Gemini-only knob that trades latency for reasoning quality. Same question, minimum thinking budget — instant response, maybe wrong. Maximum thinking budget — slower response, probably right. We'll run the same math problem at both, and see the answer quality change along with the latency cost.
