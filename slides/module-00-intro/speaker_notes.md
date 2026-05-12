# Course intro — Speaker notes

---

## Slide 1 — Title

Welcome to this course on Google's Agent Development Kit, or ADK for short. AI agents are everywhere right now: in job descriptions, product roadmaps, and startup pitch decks. But there's a wide gap between calling an LLM API once and having something running in production that reads a database, hits other services, and holds memory across weeks. Over the next fourteen modules, you're going to cross it.

---

## Slide 2 — What you'll build

By the end of the course, you'll have shipped agents across all five categories on the slide. Two of them stand out: persistent memory that survives a server restart, and voice-first conversation through Gemini's Live API. The other three round out what a production agent needs: tools, multi-agent orchestration, and HTTP deployment. All Python, all in runnable notebooks against your own key.

---

## Slide 3 — Three parts

OK, so here's how the course unfolds, in three parts. Part one is the foundation, and it's the bulk of the work: ten modules where the same agent code runs on Claude, GPT, Gemini, Qwen, or even a local Llama, all through a thin abstraction called LiteLLM. Along the way you'll give agents tools, persistent memory, multi-agent orchestration, evaluation, and HTTP deployment. Part two is the Gemini-only stretch, three modules on capabilities you genuinely cannot replicate on any other provider: search grounding straight from inside the model, long-context caching that turns million-token prompts into cheap reads, thinking budgets you can dial up or down, and the Live voice API for real-time conversation. And the final module is a short side step into A2A, the new Linux Foundation protocol that lets your agent talk to someone else's agent, even when the two were built in completely different frameworks.

---

## Slide 4 — Why this course

There's no shortage of agent courses out there, so here's why this one is worth your time. The first thing is that every single module ships a runnable notebook, so from minute one you're hands-on, not watching slides. The second is that everything you write stays portable: you pick the provider, and if you want to swap Gemini for Claude, or for a model running on your laptop, you change one line. And the third is that nothing here stops at the demo. We cover memory, evaluation, deployment, and guardrails, so what you build can actually go to production. If you write Python and you're serious about shipping agents, let's start.
