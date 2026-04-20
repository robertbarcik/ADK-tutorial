# Gemini unlocks — grounding and context caching

**Part 2 of the course starts here.**

Ten chapters of vendor-neutral ADK. Everything ran on whichever model you picked — Claude, GPT, Qwen, Gemma, Gemini — via the `LiteLlm` wrapper. Part 2 is honest about what you give up by staying neutral. Three Gemini-specific capabilities earn their own chapters because nothing else in the market replicates them:

- **Google Search grounding** (this chapter) — Gemini calls Google Search as a built-in tool, returns cited answers with real URLs, surfaces grounding metadata on the event.
- **Long context + context caching** (this chapter) — 1M-token input windows (2M on Pro), with 75–90% discount on cached content.
- **Thinking budgets** (Chapter 12) — a knob that trades latency for reasoning quality.
- **Live API voice** (Chapter 13) — bidirectional audio streaming with interruption.

The switch from Part 1 is mechanical. Replace `LiteLlm(model="openrouter/google/...")` with the bare string `"gemini-2.5-flash"`. Everything else — tools, sessions, workflow agents, callbacks, memory, eval — stays identical. One line changes; the agent keeps working.

You'll need a `GOOGLE_API_KEY` from [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Free tier is enough for most of Part 2. Context caching (this chapter, second half) and some Live API features (Chapter 13) require a paid tier.

## Part 1 — Google Search grounding

In Part 1, every agent had a knowledge cutoff. Ask about today's news and you got a refusal or a hallucinated answer. The workaround was to write your own search tool — call an external API, parse JSON, feed results back to the model.

Gemini ships this differently. `google_search` is a **built-in tool**. You import it, add it to your agent's `tools=` list, and every query with a current-information question triggers a real Google Search, returns cited results, and ADK populates a `grounding_metadata` field on the event with the source URLs.

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

grounded_agent = LlmAgent(
    name="grounded_agent",
    model="gemini-2.5-flash",                    # ← native string, not LiteLlm(...)
    description="Answers questions with up-to-date Google Search results.",
    instruction="Use google_search for current-information questions. Cite sources.",
    tools=[google_search],
)
```

Run a query and the event stream shows the answer with attached grounding:

```
USER: What is the capital of Slovakia and its current population?

[grounded_agent] The capital of Slovakia is Bratislava. Regarding its population:
                 — about 479,000 in the city proper, with the wider region
                 exceeding 732,000 inhabitants...

── Grounding metadata: 7 source(s) ──
  1. wikipedia.org     https://...
  2. britannica.com    https://...
  ...
```

Two things to notice.

**The agent does not call `google_search` as a regular tool.** You won't see a `[tool_call]` in the event stream. `google_search` is a *built-in* — handled internally by Gemini's grounding infrastructure, not as a Python function ADK dispatches. You see the *effects* of grounding (the text answer, the metadata), not a function-call/function-response pair.

**The `grounding_metadata` lists real URLs.** These are actual sources, not hallucinations. In a production user interface, you'd surface them as citations under each paragraph — "Source: Wikipedia (view article at ...)". That makes the agent's claims verifiable; users can check primary sources directly.

### Cost — billed separately from tokens

Google charges roughly **$35 per 1,000 grounded requests**. Not per token; per request. For an agent that grounds 100 queries a day, that's $3.50/day, over $100/month. Budget accordingly — and consider whether every query really needs grounding, or whether cached knowledge plus grounding-only-on-unknowns is more efficient.

### The mixing gotcha — built-in tools don't combine

A sharp edge worth naming before you build on this. **Gemini's built-in tools cannot coexist with regular function tools in the same agent.** If you mix them, the Gemini API rejects the request.

```python
# This FAILS — google_search is built-in; get_weather is regular
BAD = LlmAgent(
    model="gemini-2.5-flash",
    tools=[google_search, get_weather],   # mixing built-in + regular
)
```

The usual workaround is to wrap each built-in tool as a sub-agent via `AgentTool` (from M02/M06):

```python
# GOOD — grounding goes through its own specialist
search_agent = LlmAgent(
    model="gemini-2.5-flash",
    tools=[google_search],   # just the built-in
)

weather_agent = LlmAgent(
    model="gemini-2.5-flash",
    tools=[get_weather],     # just the regular tool
)

coordinator = LlmAgent(
    model="gemini-2.5-flash",
    tools=[AgentTool(agent=search_agent), AgentTool(agent=weather_agent)],
)
```

For Search specifically, ADK ≥ 1.16 supports `bypass_multi_tools_limit=True` on the `google_search` tool, which lets it coexist with regular tools in the same agent. Check your ADK version; the general rule (wrap as sub-agent) still applies for code executor and Vertex AI Search.

## Part 2 — Long context + context caching

Gemini 2.5+ handles up to **1M input tokens** (2M on the Pro variants). You can paste a 500-page technical manual, an entire medium-sized codebase, or months of email history into a single request.

The capability is impressive. The economics are the issue.

### The problem

A 100-page PDF is roughly 50K tokens. If your agent is asked 20 questions against it per hour — normal for a support agent over a manual — you pay for the PDF 20 times:

```
20 × 50K input = 1M input tokens/hour
  → ~$0.075/hour at the Gemini 2.5 Flash standard rate
  → $54/month per user at that query rate
```

Cheap at one user; scales brutally. And it's waste — you're re-paying for the same content on every query.

### The fix — caching

Gemini supports two caching flavors:

| Type | Setup | Discount | Control |
|---|---|---|---|
| **Implicit caching** | Automatic; zero code | ~75% on repeated prefixes | None; Gemini decides |
| **Explicit caching** | `client.caches.create(...)` with TTL | ~90% on cached portion | You pick content and lifetime |

**Implicit caching** is free and automatic. Gemini detects repeated prefixes across requests and applies the discount. You don't name a cache; you don't pick TTLs; it just works whenever the same prefix appears multiple times. Good for opportunistic savings.

**Explicit caching** gives you control. You call `client.caches.create(...)` with the content you want cached and a TTL. You get a named cache handle; subsequent `generate_content` calls pass `cached_content=cache_handle.name` and the cached portion is billed at the 90% discount. Small storage fee per cached token per hour (~$0.01 per 1M tokens/hour on Flash).

### Explicit caching API

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=GOOGLE_API_KEY)

cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        contents=[types.Content(role="user", parts=[types.Part(text=big_manual)])],
        system_instruction="Answer questions about the manual.",
        ttl="300s",   # 5 minutes; billed by the second
    ),
)
# cache.name is a resource ID you can reuse for subsequent requests

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the default wake word?",
    config=types.GenerateContentConfig(cached_content=cache.name),
)
# resp.usage_metadata.cached_content_token_count shows what hit the cache
```

Minimum cache size: around **32,768 tokens**. Smaller content won't cache — the break-even against storage fees doesn't work.

### The free-tier gotcha

**Explicit caching requires a paid Gemini API tier.** The free tier has `TotalCachedContentStorageTokensPerModelFreeTier = 0`, which blocks caching entirely.

The notebook for this chapter demonstrates the API and catches the 429 `RESOURCE_EXHAUSTED` error gracefully — the code is correct, it fails at the billing gate, not at the API surface. On a paid key, the same cell completes; on a free key, you see the error and the explanation.

### Worked example

100-page PDF at 50K tokens. 20 questions per hour.

**No caching:**
```
20 × 50K input       = 1M input tokens
  × $0.075 / 1M      = $0.075/hour
```

**Explicit caching** (create the cache once, hit it 20 times, hold storage for 1 hour):
```
create:  50K × $0.075 / 1M   = $0.00375
hits:    20 × 50K cached × ~10% rate = 20 × 50K × $0.0075/1M ≈ $0.0075
storage: 50K × 1h × $0.01/1M = $0.0005
                                -------
                                ≈ $0.013/hour
```

**~6x cost reduction** at 20 queries/hour. Scales further — at 100 queries/hour the gap widens to ~30x.

The break-even is around **3–5 queries per document per hour**. Below that, implicit caching (free, automatic) gets you most of the benefit. Above, explicit is clearly worth the extra code.

## When to pick native Gemini over LiteLLM-wrapped

An honest trade-off matrix:

| Feature | Native (`model="gemini-..."`) | LiteLLM (`LiteLlm(...)`) |
|---|---|---|
| Basic chat / tool calls | ✅ | ✅ |
| `google_search` built-in tool | ✅ | ❌ |
| `BuiltInCodeExecutor` (sandboxed Python) | ✅ | ❌ |
| Context caching (implicit + explicit) | ✅ | ❌ |
| `ThinkingConfig` / thinking budgets (M12) | ✅ | ⚠️ partial (`reasoning` param) |
| Live API / voice agents (M13) | ✅ | ❌ |
| One-line swap to Claude / GPT / Qwen | ❌ | ✅ |

**The practical rule: native Gemini when you need a feature that doesn't translate through LiteLLM.** Otherwise LiteLLM keeps your code portable. The two are not alternatives; they're different tools for different jobs.

In a production system, it's common to have *both*:

- **LiteLLM-wrapped agents** for routine queries — portable, multi-model failover, per-task model routing.
- **Native Gemini agents** for tasks that need grounding, long context, or Live API — locked to Gemini, but with capabilities nothing else provides.

Compose them with `sub_agents` or `AgentTool` from M06. The top-level coordinator routes to whichever agent fits the query.

## What to carry forward

- **Switch is one line**: `LiteLlm(model="openrouter/...")` → `"gemini-2.5-flash"`. Everything else unchanged.
- **`google_search` is a built-in tool.** Add it to `tools=`; Gemini handles Search internally. `grounding_metadata` on the event surfaces real citation URLs. ~$35 per 1,000 grounded requests, billed separately from tokens.
- **Built-in tools don't mix** with regular tools in the same agent. Wrap each as a sub-agent via `AgentTool`, or `bypass_multi_tools_limit=True` on Search (ADK ≥ 1.16).
- **Long context**: Gemini 2.5+ = 1M input tokens; Pro = 2M.
- **Implicit caching**: automatic, ~75% discount on repeated prefixes, zero code.
- **Explicit caching**: `client.caches.create(...)` with TTL, ~90% discount, ~32K-token minimum, **paid tier only**.
- **Break-even**: implicit below 3–5 queries per document per hour; explicit above.
- **Production pattern**: LiteLLM-wrapped for portable routine work, native Gemini for grounding/caching/Live. Compose them with `sub_agents` or `AgentTool`.

Module 12 picks up the third Gemini-only capability: **thinking budgets**. A knob you set on the model that trades latency for reasoning quality. Same problem at `thinking_budget=0` (instant, maybe wrong) versus `thinking_budget=8192` (slower, probably right). We'll run the same math problem at both and watch the answer change along with the latency.
