# Build Production-Ready AI Agents in Python with Google ADK: From First Agent to Voice, Multi-Agent Systems, and A2A

Everyone is talking about AI agents, but very few people can actually ship one. Calling an LLM API once is a long way from having an agent that reads a database, calls other services, holds memory across conversations, and runs behind an HTTPS endpoint. This course takes you from one to the other.

Across 14 hands-on modules, you'll go from writing your first agent in Python to building multi-agent orchestrations, voice-first conversational agents, and agents that talk to other agents over the new A2A protocol. Every concept is paired with a Jupyter notebook you run against your own API key, so you try each idea the moment you learn it, not in some vague "future project".

By the end of the course, you'll have built real working agents, and you'll know exactly how to take them into production.

## Why This Course is Different

**Hands-on from the first minute.** Every module ships a Jupyter notebook that runs from start to finish. You don't watch someone code on a slide, you run the code yourself, break it, change it, and make it yours.

**Vendor-neutral by design.** Part 1 runs entirely through OpenRouter, which means you can complete ten full modules with Claude, GPT, or even a free local model, without ever touching Google Cloud. You keep your stack portable, your budget minimal, and your options open.

**Built for production, not demos.** Other courses stop at "here's a chatbot that answers one question". This one goes the full distance: memory, evaluation, deployment, guardrails, observability, and the production gotchas that only surface after you ship.

**Four aligned artifacts per module:** slides, speaker notes, a textbook chapter, and a runnable Jupyter notebook. Whichever way you learn best, watching, reading, or coding along, there's a version of every module for you.

**A one-hour quick path, for the impatient.** Four carefully chosen modules give you the mental model plus the most impressive demo in roughly sixty minutes. It's the fastest way to decide whether the full course is for you.

## What You Will Gain from This Course

- Build production agents in Python with Google's Agent Development Kit.
- Wire up four different kinds of tools: plain Python functions, REST APIs via OpenAPI specs, MCP servers, and specialist sub-agents.
- Compose multi-agent systems using Sequential, Parallel, and Loop workflow agents, plus the crucial distinction between `sub_agents` (delegation) and `AgentTool` (consultation).
- Swap LLM providers in a single line: the same agent code runs on Claude, GPT, Gemini, Qwen, or a local Llama model running through Ollama.
- Add memory that survives a server restart: persistent sessions in Postgres, MySQL, or SQLite, plus long-term cross-session recall patterns.
- Deploy agents as real HTTP services: package them into Docker, ship them to Cloud Run, or run them on Vertex AI Agent Engine.
- Evaluate agents with a test harness, not by eyeballing: trajectory testing, response scoring, and thresholds you can put into CI.
- Guard destructive operations the right way, with code-level confirmation tokens, not polite prompt instructions the model can ignore.
- Use Gemini's superpowers when you need them: Google Search grounding with real citations, long-context caching that cuts input costs by up to 90%, thinking budgets that trade latency for reasoning quality, and the Live voice API for real-time voice agents.
- Speak the emerging protocols: MCP (Model Context Protocol, now a Linux Foundation standard) and A2A (the agent-to-agent protocol) are rapidly becoming the way agents interoperate across vendors. This course takes both seriously.

## Course Structure

### Part 1: The Vendor-Agnostic Spine (Modules 1-10)

Ten modules that teach ADK as a general-purpose agent framework. It runs on any LLM provider LiteLLM supports: Claude, GPT, Gemini, Qwen, Llama, with OpenRouter as the default.

**Module 1: The Mental Model of an Agent.** The four primitives you'll use in every module that follows: Agent, Runner, Event, and Session. You build and run your first working agent.

**Module 2: Tools as Verbs.** The four flavors of tools in ADK: plain Python functions, REST APIs via OpenAPI specs, MCP servers, and specialist sub-agents exposed as tools. Plus a short interlude on risk-based tool design: why code-level guards beat prompt-level instructions when the stakes are high.

**Module 3: Sessions, State, Events, and Artifacts.** How conversation memory actually works inside an agent. State scoping with `user:`, `app:`, and `temp:` prefixes. Events as the agent developer's built-in debugger.

**Module 4: The One-Line Model Swap.** The same agent code, running on five different providers. You'll see Claude, GPT, Gemini, Qwen, and Llama produce the same behavior with a single configuration line changed. Plus a short interlude on priority-tiered instruction writing.

**Module 5: Workflow Agents.** Deterministic orchestration using SequentialAgent, ParallelAgent, and LoopAgent. The canonical Generator-Critic refinement loop: the "oh, so that's what ADK is really good at" moment.

**Module 6: Multi-Agent Hierarchies.** When you should actually reach for multiple agents, and when one agent with one more tool is the better answer. The practical distinction between `sub_agents` (delegation) and `AgentTool` (consultation), plus three tests for deciding which to use.

**Module 7: Callbacks as Middleware.** Six lifecycle hooks that let you intercept agent behavior. Think Django middleware, but for agents. Blocklist guardrails, PII redaction, response mocking for tests, and cost accounting, all enforced at the framework level.

**Module 8: Memory.** Cross-session persistence with `DatabaseSessionService` on Postgres, MySQL, or SQLite. Long-term memory patterns for recalling facts the agent has seen before. The staleness problem and how to defend against confidently wrong recall.

**Module 9: Evaluation.** Testing agents with trajectory checks and response scoring. Thresholds, pass/fail gates, and how to plug `adk eval` into your CI pipeline. The honest case against ROUGE-1 for anything open-ended.

**Module 10: Deployment.** Three real production paths: self-hosted containers with Docker, managed deployment on Cloud Run, and fully managed hosting on Vertex AI Agent Engine. Plus a production-readiness checklist covering auth, observability, and scaling.

### Part 2: The Gemini Unlocks (Modules 11-13)

Three modules on capabilities that only exist when you pick Gemini as your model. Tested against Google AI Studio with a free-tier key.

**Module 11: Grounding and Caching.** Search-grounded answers with genuine citations from the live web. Explicit context caching for long-context knowledge bases: up to 90% savings on input tokens when you reuse the same context across many calls.

**Module 12: Thinking Budgets.** Trade latency for reasoning quality with a single parameter. Learn when thinking earns its keep, and when it just burns tokens.

**Module 13: Live Voice API.** Real-time voice agents with sub-second latency. The most genuinely impressive Gemini-only capability in the entire LLM landscape right now.

### Side Step: A2A Protocol (Module 14)

A focused thirty-minute module on the agent-to-agent protocol. You'll see how one agent exposes itself over HTTP and another consumes it as if it were a tool. Too new to teach as infrastructure. Too important to skip.

## Are There Any Course Requirements or Prerequisites?

This is a technical course. To succeed, you should bring:

- **Comfortable Python skills.**
- **Basic familiarity with REST APIs and the command line.** You'll use curl, Docker, and read OpenAPI specs in later modules.
- **Experience calling an LLM API at least once before.** You don't need to be a machine learning expert, but the course assumes you've written at least a "hello world" against OpenAI, Anthropic, or Gemini.
- **One API key.** Either an OpenRouter key (recommended, unlocks all of Part 1 for just a few cents total) or a free-tier Google AI Studio key for Part 2.

You do NOT need:
- A GPU
- A paid Google Cloud account

## Who is this course for?

This course is built for people who are serious about AI agents. Not demo agents. Agents that get put in front of real users, read real data, and have to keep working when nobody is watching.

We've tailored the content for:

- **Software engineers** moving beyond single LLM calls, who need a framework for agents that reason over multiple steps, call external tools, and persist state.
- **ML and AI practitioners** comfortable with models, but who need a production-grade way to wire them to tools, memory, evaluation, and deployment.
- **Technical leads and architects** deciding between LangGraph, CrewAI, and ADK, and who want a hands-on basis for comparison instead of reading marketing pages.
- **Indie developers and builders** prototyping agent-based products on a tight budget. The vendor-neutral design keeps your experiments cheap, and your code portable across providers.
- **Anyone building with LLMs today** who wants to understand how voice agents, multi-agent orchestration, MCP, and A2A fit into the larger picture, and how to ship something real with them.

If "my next project involves agents" is somewhere in your near future, this course is built for you.
