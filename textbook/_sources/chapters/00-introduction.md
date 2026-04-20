# Introduction

This is a course on Google's Agent Development Kit, and it is going to work hard to earn your time.

Most agent tutorials you'll find online teach one of two things. Either they teach a framework's surface — "here's how to spell `tool_calling` in LangChain, here's how to spell it in CrewAI, here's how to spell it in ADK" — and leave you with a file full of pastable snippets and no mental model. Or they teach a walled-garden demo that only works with one vendor's model, one vendor's cloud, and one vendor's billing dashboard, and the moment you try to deploy against anything else, nothing translates.

This course does neither.

## What you'll build

Fourteen modules, each shipping four aligned artifacts — slides, speaker notes, a textbook chapter, and a runnable Jupyter notebook. The modules are not independent. Module one builds the mental model. Module two puts tools on it. Module three adds sessions. Every module after that composes on the primitives of the first three. By module ten you have an agent that calls tools, holds state, writes its own critiques in a loop, delegates to specialists, short-circuits itself in a callback, remembers across conversations, passes an evaluation suite, and ships to production — and it does so while running on any model you can route through LiteLLM.

Modules eleven through thirteen are the Gemini-specific part of the course. Search grounding with citations. Long context with caching. Thinking budgets. The Live voice API. Three hours of material you can't replicate with Claude or GPT. These modules are honest about the trade: you get real capability and real lock-in, in that order.

Module fourteen is thirty minutes on A2A — the agent-to-agent protocol that Google launched in April 2025 and handed over to the Linux Foundation two months later. It is nowhere near infrastructure-grade yet, but the shape of the protocol is already settling, and being ahead of it by thirty minutes is worth the investment.

## Why ADK, honestly

ADK is not the most popular agent framework. LangGraph has four times the community, CrewAI has twice the stars, the OpenAI Agents SDK has more marketing money behind it. If you're picking a framework for political reasons — "nobody got fired for choosing LangChain" — ADK is not the safe pick.

But there are three things ADK does genuinely better than the competition.

The first is **observability**. Every communication inside an agent run is an Event — a tool call, a tool response, a state change, a sub-agent handoff — and the event stream is the primary object you work with. Read the events, see what the agent did. No framework gets this as cleanly as ADK does. Not LangGraph, where nodes and edges obscure what the model actually emitted. Not CrewAI, where the role metaphor hides the underlying call sequence. If you have ever shipped an agent to production and spent three hours trying to figure out why it made a particular decision, you will feel the difference in the first five minutes.

The second is **workflow agents as first-class primitives**. ADK ships three of them out of the box — Sequential, Parallel, and Loop — and they behave exactly the way their names suggest. A Sequential agent runs its children like a shell pipeline. A Parallel agent fans out like `asyncio.gather`. A Loop agent repeats until a child calls `exit_loop` or the iteration limit is reached. No graph DSL, no nodes-and-edges vocabulary. You write Python that looks like Python.

The third is **vendor-neutrality that actually works**. The `LiteLlm` wrapper turns any OpenRouter-routable model into an ADK model in one line. We'll use this from module one onward. By module four you will have swapped Claude, GPT, and a locally-hosted Qwen into the same agent without changing anything else.

Everything else — deployment, evaluation, memory services, A2A — is competitive but not differentiating. ADK's case lives in those three.

## Who this course is for

Software engineers who have written Python before, who have used at least one LLM API (OpenAI or Anthropic is enough), and who want to build agents as real software rather than as prompt strings glued together with regex.

If you've been writing agents for a year, you'll find module one too slow and module seven — on callbacks as middleware — surprisingly dense. If this is your first agent framework, every module earns its thirty minutes. If you're coming from LangGraph or CrewAI, pay attention to the vocabulary: we'll call the same things by different names, and getting the mapping right early saves confusion later.

## How to use this course

Read the textbook chapter first — this one, and the matching one for every module. It is designed to be readable on a train without a computer. Then open the slide deck for the module, which compresses the chapter into a lecture you can follow passively. Then run the notebook, which is the material made concrete. Three passes at the same content, in three shapes. Each one reinforces what the others taught.

If you only have time for one pass, pick the notebook — because the thing you actually want to leave this course with is the ability to build an agent, not the ability to describe one.

## What you'll need

A Python 3.10 or newer environment. An API key from OpenRouter for Part 1 (sign up at openrouter.ai, pay-as-you-go, typically under five cents per module if you stick to the defaults). An API key from Google AI Studio for Part 2 (aistudio.google.com, free tier is enough for the demos we'll run). And roughly six to eight hours of focused time across all fourteen modules.

That's it. Let's build something.
