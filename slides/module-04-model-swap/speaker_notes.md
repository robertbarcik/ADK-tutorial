# M04 — Speaker notes

---

## Slide 1 — Title

Welcome to module four: the one-line model swap. This is the module where we open up the model abstraction we've been treating as a black box. By the end of it, the exact same agent code will have run on Claude, GPT, Gemini, Qwen, and Llama. One line of configuration changes each time. The rest of the agent, the instruction, the tools, the session, and the Runner, doesn't change at all.

---

## Slide 2 — So far / This module

The set-up is on the slide. So far, every demo has used that one specific model string. This module opens it up. We'll cover what the string actually means under the hood, the four other providers it connects you to, and when swapping makes sense in practice.

---

## Slide 3 — What LiteLlm actually is

Let me explain what LiteLlm is and why it exists. ADK was written by Google, and it speaks Gemini natively. That means you can pass `model="gemini-2.5-flash"` and it just works, because ADK is talking directly to Google's SDK.

Every other model needs a translation layer, and that layer is LiteLLM. It's an independent open-source library maintained by a separate team, and it sits between your code and roughly a hundred LLM providers. Requests come in shaped like OpenAI's API. LiteLLM translates them to whatever the target expects, and responses come back translated the other way.

ADK's `LiteLlm` wrapper is really just a thin adapter that exposes LiteLLM as an ADK-compatible model. Google wrote this adapter so they didn't have to write a custom shim per vendor. As a result, every time someone ships a new LLM provider, the LiteLLM team adds support, and ADK inherits it for free.

---

## Slide 4 — Request flow

What you see on this slide is the full round trip of a single call. Your agent builds an OpenAI-shaped request. That hits the LiteLlm wrapper, which hands it to the LiteLLM library. LiteLLM then translates it into the shape the target provider wants: Anthropic's format, OpenAI's format, Google's format, or whichever applies. It sends the request to OpenRouter, which routes to the actual provider. The response comes back through the same pipe, getting translated again on the way.

So that's two translations per call. Small overhead. The catch is that the translation is version-sensitive. If you bump `google-adk` independently of `litellm`, the shape of tool-call payloads can drift. The wrapper and the library stop agreeing on what an OpenAI-shaped tool call looks like. That's why `requirements.txt` pins both versions together. Bump them as a pair, never one alone.

---

## Slide 5 — The OpenRouter model-string convention

Here on the slide we have the OpenRouter model string format, plus a reference table of five concrete examples. The format is straightforward: `openrouter`, then the provider, then the specific model name. There's an optional `:tier` suffix for free, beta, or nitro tiers, which you should almost always skip. Free tiers on OpenRouter are aggressively rate-limited and unreliable.

The table is really the most useful reference in this module. Five providers, one OpenRouter key. One key replaces five. Per-token prices are within five percent of what you'd pay going directly to each provider, which means you're not paying a meaningful markup for the convenience of consolidating.

---

### Notebook break — One agent, five providers

[Switch the screen to the notebook.]

Here in the notebook we have an agent factory. One function that takes a model string and returns an LlmAgent. Below it is a list of five model strings, one for each provider on the slide: Gemini-Flash-Lite, GPT-4o-mini, Claude-Haiku, Qwen-3, and Llama-3.1. The loop calls the factory once per string and asks the resulting agent the same question. [Run the cells.] Watch the answers scroll by, one model at a time. Same question. Same agent definition. Five different responses.

[Switch back to the slide deck.]

---

## Slide 6 — What to notice in the output

Three observations worth calling out from that run.

First, the answers vary in style but converge on content. Every model explains tool-calling reasonably, and none of them hallucinate badly. On a vanilla concept, the difference is texture, not correctness. Quality differences only really show up on hard prompts.

Second, latency varies by about three times across the providers. Open-weight models through their current providers tend to be slower than the hosted frontier ones. For a tool-heavy agent making ten calls per turn, this compounds: three-times-slower turns can become unusable. For straightforward question-answering, on the other hand, it's barely noticeable.

Third, reasoning traces leak from some models. Qwen and DeepSeek-R1 variants emit their thought process even when you don't ask. You can suppress it with a specific extra-body parameter, or just pick a non-reasoning variant. In production, be aware of this so your users don't see the chain-of-thought in their UI.

---

## Slide 7 — Local models via Ollama

Time for a bonus section: local models via Ollama. If you want to run open-weight models on your own hardware, Ollama is the easy path. Zero cost per call. No network round-trips. Fully offline. And one prefix to get right.

---

## Slide 8 — Setup

On the slide we have the full Ollama setup, top to bottom. It's two pieces: three one-time shell commands to get Ollama running locally, then one line of Python to use it from ADK.

The three shell commands install Ollama, start the Ollama server which runs a local API on port 11434, and pull whatever model you want. Qwen 3 is great for tool-calling on a laptop with sixteen gigs of RAM.

Then in your ADK code, you swap the model string to `LiteLlm(model="ollama_chat/qwen3:8b")`. That's it. If your Ollama is on a non-standard port, set `OLLAMA_API_BASE=http://localhost:11434`, but the default works for most people.

---

## Slide 9 — The gotcha

The Ollama prefix matters more than anything else in this module. LiteLLM supports two prefixes for Ollama, and they do completely different things.

The first is `ollama_chat/qwen3:8b`. Use this one. It hits Ollama's chat-completions API, which has real function-calling support. Tool calls work as you'd expect.

The second is `ollama/qwen3:8b`. Do not use this. It hits Ollama's older completions API. Tool calls there get rendered as text the model has to produce verbatim. The model fails, it retries, the tool call gets re-rendered, and it fails again. Infinite loop.

The trap is that you won't see the bug on the plain prefix until you give the agent tools. Without tools, the two prefixes behave identically. The first time you add a tool is when it breaks, and the error message doesn't tell you what's wrong. This is actually the single most reported issue in the adk-python repository. Memorize the prefix.

---

## Slide 10 — Native vs LiteLLM-wrapped Gemini

A quick clarification that comes up often: there are two ways to use Gemini in ADK.

The first is native: `model="gemini-2.5-flash"`, plain string, no LiteLlm wrapper. ADK goes directly to the google-genai SDK. All Gemini-specific features are available, including search grounding, thinking budgets, the Live API, and long-context caching. This is what Part 2 of this course uses.

The second is LiteLLM-wrapped: `LiteLlm(model="openrouter/google/gemini-2.5-flash-lite")`, which goes through OpenRouter as an OpenAI-shaped request. Gemini-specific features are not reachable here, because LiteLLM can't translate features that don't exist in the OpenAI shape.

So the rule of thumb is this. LiteLLM-wrapped for Part 1, vendor-agnostic work. Native for Part 2, Gemini-specific features. In this course we use LiteLLM-wrapped throughout the vendor-agnostic modules, precisely so your code stays portable.

---

## Slide 11 — Prompt priority tiers

Time for a quick interlude from the Agentic Design Patterns publication, chapter five. Prompt priority tiers. It's relevant to model swapping because different models handle long instructions differently, and because instructions sometimes get truncated under context pressure.

---

## Slide 12 — The problem

Here's the problem this interlude addresses. When you swap models, instructions that worked on Claude sometimes partially fail on GPT. Not because GPT is worse, but because models weight different parts of the prompt differently. Claude reads all the way through, GPT prioritizes the earliest tokens, and Gemini has its own pattern.

On top of that, long instructions get truncated under context pressure. A long system prompt plus long tool descriptions plus a long chat history can force ADK to drop parts of what you wrote. The parts you lose first are the ones at the bottom.

So the pattern is this: structure your instruction so the most important bits survive. Put them first.

---

## Slide 13 — Three tiers

The priority model has three tiers.

Tier one is invariants. These are rules the agent must obey under any circumstance: safety gates, hard refusals, format constraints. Top of the prompt. Short, declarative. For example, "never include credit card numbers", "refuse financial advice", "always respond in JSON".

Tier two is core behavior. This is the main job description: what the agent is for and what its goals are. For example, "you help engineers debug build failures by reading logs and suggesting fixes."

Tier three is preferences. This is how the agent communicates: length, tone, markdown or plaintext, bullet points or paragraphs. Lowest priority, and it's OK to lose this first. For example, "prefer bullet points over paragraphs when listing."

Read top to bottom: invariants, then purpose, then style.

---

## Slide 14 — A priority-tiered instruction

Here on the slide is what a priority-tiered instruction looks like in practice. Three sections, each labeled with a clear header that helps both humans and the model parse the structure.

Invariants come first: never execute code, never generate credentials, admit ignorance instead of guessing. Then core behavior: the job description for this particular agent. And preferences last: markdown for code blocks, short prose, things like that.

If ADK ever truncates this, because the context filled up with tool descriptions and chat history, the preferences go first. Then core behavior. Invariants survive the longest. That ranking is intentional.

---

### Notebook break — Try to jailbreak the priority instruction

[Switch the screen to the notebook.]

Here in the notebook the priority-tiered instruction is wired into a real agent. Now let me try to break it. I'll ask the agent for an AWS access key, which the invariants at the top of the prompt explicitly forbid. [Run the cell.] Notice the refusal. The model parses the structured prompt, sees the invariant, and refuses regardless of what comes later in the conversation. Run the same setup against any of the five providers we tried earlier and you get the same refusal pattern. Tier one survives pressure that tier three wouldn't.

[Switch back to the slide deck.]

---

## Slide 15 — When to swap models in production

So when should you actually swap models in production? There are three scenarios where swapping actually helps.

First, failover. A provider has an outage. Claude's API goes down, which happens every few months, and you need to keep serving traffic. A one-line config change sends requests to GPT or Gemini instead. This is really the main reason most production ADK deployments bother with LiteLLM at all.

Second, per-task capability. Different models are good at different things. GPT-5 reasons better through obscure math. Claude Opus writes slightly cleaner code. Gemini grounds in live web results natively. Pick the right model for each task, and compose them with sub-agents or AgentTool.

Third, cost optimization. Route cheap queries to Haiku, GPT-4o-mini, or Flash-lite. Route hard queries to Opus, GPT-5, or Pro. The agent's model can even be different per sub-agent. Callbacks and evaluation, both of which come up later in the course, give you the hooks to measure which queries are "hard" and route them accordingly.

---

## Slide 16 — The rule

The rule to carry forward is on the slide. Vendor-neutrality is a capability, not a habit. You don't swap models just because you can. You swap for a specific reason: failover, capability, or cost. And you swap with evaluation, not on hunches. Different models have different refusal patterns, different formatting biases, and different accuracy on your specific task. Later in the course we'll make "swap with evaluation" concrete.

---

## Slide 17 — Up next

Up next, we get into workflow agents. One agent is enough for toy demos, but real work needs composition. Sequential, Parallel, and Loop: three first-class composition primitives. Plus the canonical ADK wow demo: a Generator-plus-Critic pair refining a draft in a loop until the critic says it's good enough. See you there.
