# M04 — Speaker notes

---

## Slide 1 — Title

Module four. The one-line model swap. Three modules in, every demo has used one model string. Now we open that up. By the end of the next fifteen minutes, the exact same agent code will have run on Claude, GPT, Gemini, Qwen, and Llama. One line of configuration will change each time. The rest — the instruction, the tools, the session, the runner — will not.

---

## Slide 2 — Three modules in

Three modules in, every demo used `openrouter/google/gemini-2.5-flash-lite` — that specific string. This module opens it up. What does that string actually do, what are the alternatives, and when do you swap.

---

## Slide 3 — What LiteLlm actually is

ADK was written by Google. It speaks Gemini natively — you can pass `model="gemini-2.5-flash"` and it just works, because ADK is talking directly to Google's SDK.

Every other model needs a translation layer. That layer is LiteLLM — an independent open-source library maintained by a separate team. It sits between your code and roughly a hundred LLM providers. Requests come in shaped like OpenAI's API; LiteLLM translates them to whatever the target expects; responses come back translated the other way.

ADK's `LiteLlm` wrapper is a thin adapter that exposes LiteLLM as an ADK-compatible model. Google wrote this adapter so they didn't have to write a custom shim per vendor. Every time someone ships a new LLM provider, the LiteLLM team adds support, and ADK inherits it for free.

---

## Slide 4 — Request flow

The picture. Your agent builds an OpenAI-shaped request. That hits the LiteLlm wrapper, which hands it to the LiteLLM library. LiteLLM translates it into the shape the target provider wants — Anthropic's format, OpenAI's format, Google's format. It sends the request to OpenRouter, which routes to the actual provider. The response comes back through the same pipe, getting translated again on the way.

Two translations per call. Small overhead. The catch: the translation is version-sensitive. If you bump `google-adk` independently of `litellm`, the shape of tool-call payloads can drift — the wrapper and the library stop agreeing on what an OpenAI-shaped tool call looks like. That's the reason `requirements.txt` pins both versions together. Bump them as a pair, never one alone.

---

## Slide 5 — OpenRouter model string convention

The format. Slash, slash, colon-optional. `openrouter/provider/model`. An optional `:tier` suffix for free/beta/nitro, which you should almost always skip — free tiers on OpenRouter are aggressively rate-limited and unreliable.

The table on the slide is the most useful reference in this module. Five providers, one OpenRouter key. One key replaces five. Per-token prices are within five percent of the underlying providers, so you're not paying a meaningful markup for the convenience.

---

## Slide 6 — Live: one agent, five providers

Switch to the notebook. Cells eight through eleven. We define an agent factory — one function that takes a model string and returns an LlmAgent — and a loop that runs the same question through five models. Watch the answers scroll by.

---

## Slide 7 — What to notice

Three observations worth calling out.

First, the answers vary in style but converge on content. Every model explains tool-calling reasonably; none of them hallucinate badly. On a vanilla concept, the difference is texture, not correctness. Quality differences only show up on hard prompts.

Second, latency varies by about three times across the providers. Open-weight models through their current providers tend to be slower than hosted frontier ones. For a tool-heavy agent making ten calls per turn, this compounds — three-times-slower turns into unusable. For question-answering it's barely noticeable.

Third, reasoning traces leak from some models. Qwen and DeepSeek-R1 variants emit their thought process even when you don't ask. You can suppress it with a specific extra-body parameter, or pick a non-reasoning variant. In production, be aware of this so your users don't see the chain-of-thought in their UI.

---

## Slide 8 — Ollama section header

Bonus. Local models via Ollama. If you want to run open-weight models on your own hardware, Ollama is the easy path. Zero cost per call. No network. Fully offline. One prefix to get right.

---

## Slide 9 — Ollama setup

Setup is three commands. Install Ollama. Start the Ollama server, which runs a local API on port 11434. Pull whatever model you want — Qwen 3 is great for tool-calling on a laptop with 16 gigs of RAM.

Then in your ADK code, swap the model string. `LiteLlm(model="ollama_chat/qwen3:8b")`. If your Ollama is on a non-standard port, set `OLLAMA_API_BASE=http://localhost:11434` — but the default works for most people.

---

## Slide 10 — The Ollama gotcha

The most important slide in this module. LiteLLM supports two prefixes for Ollama, and they do completely different things.

`ollama_chat/qwen3:8b` — use this. It hits Ollama's chat-completions API, which has real function-calling support. Tool calls work.

`ollama/qwen3:8b` — do not use this. It hits Ollama's completions API. Tool calls get rendered as text the model has to produce verbatim, the model fails, it retries, the tool call gets re-rendered, it fails again. Infinite loop.

You won't see the bug on the plain prefix until you give the agent tools. Without tools, they behave identically. The first time you add a tool is when it breaks, and the error message doesn't tell you what's wrong. This is the single most reported issue in the adk-python repository. Memorize the prefix.

---

## Slide 11 — Native vs LiteLLM-wrapped Gemini

Quick clarification that comes up often. You can use Gemini two ways in ADK.

Native: `model="gemini-2.5-flash"` — plain string, no LiteLlm wrapper. ADK goes direct to the google-genai SDK. All Gemini-specific features are available: search grounding, thinking budgets, the Live API, long-context caching. This is what Part 2 of this course uses.

LiteLLM-wrapped: `LiteLlm(model="openrouter/google/gemini-2.5-flash-lite")` — goes through OpenRouter, OpenAI-shaped request. Gemini-specific features are not reachable — LiteLLM can't translate features that don't exist in the OpenAI shape.

The rule of thumb: LiteLLM-wrapped for Part 1, vendor-agnostic work. Native for Part 2, Gemini-specific features. In this course we use LiteLLM-wrapped throughout the vendor-agnostic modules precisely so your code is portable.

---

## Slide 12 — Interlude header

Two-minute interlude. From the Agentic Design Patterns publication, Chapter 5. Prompt priority tiers. Relevant to model swapping because different models handle long instructions differently, and because instructions sometimes get truncated.

---

## Slide 13 — The problem

When you swap models, instructions that worked on Claude sometimes partially fail on GPT. Not because GPT is worse — because models weight different parts of the prompt differently. Claude reads all the way through; GPT prioritizes the earliest tokens; Gemini has its own pattern.

And long instructions get truncated under context pressure. A long system prompt plus long tool descriptions plus a long chat history can force ADK to drop parts of what you wrote. The parts you lose first are the ones at the bottom.

The pattern: structure your instruction so the most important bits survive. Put them first.

---

## Slide 14 — Three tiers

Three tiers.

Tier one: invariants. Rules the agent must obey under any circumstance. Safety gates, hard refusals, format constraints. Top of the prompt. Short, declarative. "Never include credit card numbers." "Refuse financial advice." "Always respond in JSON."

Tier two: core behavior. The main job description. What the agent is for, what its goals are. "You help engineers debug build failures by reading logs and suggesting fixes."

Tier three: preferences. How the agent communicates. Length, tone, markdown or plaintext, bullet points or paragraphs. Lowest priority, and it's OK to lose this first. "Prefer bullet points over paragraphs when listing."

Read top to bottom: invariants → purpose → style.

---

## Slide 15 — Priority-tiered instruction example

Here's what it looks like as an actual instruction string. Three sections, labeled with headers that help both humans and the model parse the structure. Invariants first — never execute, never generate credentials, admit ignorance instead of guessing. Core behavior next — the job. Preferences last — markdown for code, short prose.

If ADK ever truncates this — because the context filled up with tool descriptions and chat history — the preferences go first. Then core behavior. Invariants survive the longest. That ranking is intentional.

Run the notebook cell that demonstrates this. Then try to jailbreak it: ask for an AWS access key after setting up the agent. It refuses, every time, across all five models. Tier one survives pressure that Tier three wouldn't.

---

## Slide 16 — When to swap in production

Vendor-neutrality is a capability, not a habit. Three scenarios where swapping actually helps.

Failover. A provider has an outage — Claude's API goes down, which happens every few months — you need to keep serving. A one-line config change sends traffic to GPT or Gemini. This is the main reason most production ADK deployments bother with LiteLLM at all.

Per-task capability. Different models are good at different things. GPT-5 reasons better through obscure math. Claude Opus writes slightly cleaner code. Gemini grounds in live web results natively. Pick the right tool for each task; compose them with sub-agents or AgentTool from module six.

Cost optimization. Route cheap queries to Haiku, GPT-4o-mini, or Flash-lite. Route hard queries to Opus, GPT-5, or Pro. The agent's model can be different per sub-agent. Callbacks from module seven and evaluation from module nine give you the hooks to measure which queries are "hard" and route them accordingly.

---

## Slide 17 — The rule

The rule. Vendor-neutrality is a capability, not a habit. You don't swap models because you can; you swap for a specific reason — failover, capability, cost. And you swap with evaluation, not on hunches. Different models have different refusal patterns, different formatting biases, different accuracy on your specific task. Module nine is where we make "swap with evaluation" concrete.

---

## Slide 18 — Next

Module five. Workflow agents. One agent is enough for toy demos; real work needs composition. Sequential, Parallel, Loop — three first-class composition primitives. And the canonical ADK wow demo: a Generator+Critic pair refining a draft in a loop until the critic says it's good enough. See you there.
