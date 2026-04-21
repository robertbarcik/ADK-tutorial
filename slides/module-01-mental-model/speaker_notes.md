# M01 — Speaker notes

---

## Slide 1 — Title

Welcome to module one of the Google ADK course. This is the first of fourteen modules, and the goal of this one is narrow: by the end of the next fifteen minutes, you should be able to name four things without hesitation — Agent, Runner, Event, and Session. Those four show up in every module after this one. Get them clear now, and the rest of the course is a series of small refinements. Let's get into it.

---

## Slide 2 — What ADK is

ADK is Google's Agent Development Kit. It's a Python framework. Google open-sourced it, the 1.0 release shipped in May 2025, and we're on version 1.31 as I record this. The reference implementation is Python; there are Java, Go, and TypeScript SDKs if you need them, but Python is where the features land first and where this course lives.

Four things ADK is not, because these come up. It's not a model — you bring your own, and we'll use Claude, GPT, and Gemma before we use any Gemini model. It's not a cloud — it runs on your laptop today and on Cloud Run tomorrow. It's not a UI — there's a development UI we'll see in a minute, but the output is code. And it's not a graph DSL. You write typed Python, not a JSON DAG.

---

## Slide 3 — Why a framework at all

The honest test for whether any framework is worth learning is: what do you stop writing when you adopt it? With ADK the answer is sixty lines you'd otherwise write every time.

The retry loop when the model fails. The JSON parser that crashes on the fourth edge case. The manual conversation history that you have to truncate yourself before the context window blows up. The switch statement that maps tool names to Python functions. The error path when the model hallucinates a tool that doesn't exist.

Frameworks earn their keep when they stop you writing boilerplate, and let you write the things that are actually yours — the instruction, the tools, the business logic. That's the deal ADK offers.

---

## Slide 4 — The agent equation

Before the primitives, the picture. An agent is an LLM, plus an instruction telling it how to behave, plus some tools it can call, plus some memory of what happened before, plus a loop that ties it all together. That's the whole equation.

ADK gives you the loop and the plumbing. You bring the other four. Keep this picture in your head as we go through the primitives — every one of them is a piece of this equation.

---

## Slide 5 — The four primitives

These four. I'm going to repeat them a lot, because they are the whole mental model.

Agent is the thing the LLM lives in — a name, a model, an instruction, and optionally some tools. Runner drives the conversation forward; it's the event loop. Event is every single thing that happens inside a run — every message, every tool call, every state change. And Session is the conversation's memory: the history of events and a state dictionary, keyed by application, user, and session ID.

Everything else in ADK — workflow agents, multi-agent hierarchies, callbacks, memory, evaluation — composes on top of these four. Get them clear and the rest unfolds.

---

## Slide 6 — Agent

Here's an agent. Four lines of configuration. The name is how ADK refers to it internally. The model is wrapped in the LiteLlm helper — we'll come back to this, but that wrapper is what makes ADK vendor-neutral. The description is what other agents will see if this one becomes a sub-agent. The instruction is the system prompt.

If you wanted to give this agent tools, you'd add a `tools=[...]` argument with a list of Python functions. No tools on this one yet. Just a greeter.

---

## Slide 7 — Runner

An agent on its own is inert. It doesn't do anything. The Runner wires it to a session service, and hands you back an asynchronous event stream.

The mental model for the Runner is a game engine's main loop. Your agent is the entity that gets ticked. On each tick, the Runner sends the current conversation state into the model, reads what the model produces, and emits events for everything it observes. You iterate over those events and make decisions.

If you've used Node.js middleware, or an Express request pipeline, the shape is familiar.

---

## Slide 8 — Event

Event is the primitive that sets ADK apart from most agent frameworks. Every single communication inside a run produces an event. User message in: event. Model text response: event. Model decides to call a tool: event. Tool executes and returns a value: event. An agent hands off to a sub-agent: event. The state dictionary changes: event.

Read the events and you can reconstruct exactly what the agent did and why. This is the debugger for agent work. When I'm teaching people ADK and they ask "how do I debug this thing", the answer is always the same — read the events.

---

## Slide 9 — Session

The fourth primitive. A session holds the event history and the state dict for one conversation, keyed by a triple: application name, user ID, session ID.

Three session services ship with ADK. In-memory, for demos and tests. DatabaseSessionService, which runs on SQLAlchemy — Postgres, MySQL, SQLite — for self-hosted production. And VertexAiSessionService if you happen to be on Google Cloud.

We'll use in-memory through module seven. In module eight, when we make memory the point, we'll swap to the database one and a student on a laptop can run a Postgres container on the side.

---

## Slide 10 — Live: one agent, one event

All right. Time to show you this. We're switching to the notebook now. We'll run through cells one to seven — the setup, the simplest agent, and one run that produces a single event.

---

## Slide 11 — The simplest event stream

Back on the slide. This is what you just saw in the notebook. One event, marked `FINAL`, containing the greeter's response.

This is the minimum a conversation can produce. User turn in, one model turn out, stream ends. Nothing interesting — but it establishes the baseline for what we're about to see when we add a tool.

---

## Slide 12 — Add a tool

Tools are Python functions. That's the whole tool model at this layer of abstraction.

You write a function with a docstring and type hints. ADK reads the docstring and type hints to build the JSON schema the model will see. No decorators, no config files, no tool-registration dance.

Here, `get_weather` takes a city string and returns a dict. That's a tool. Add it to the agent's `tools=` list and the model can call it.

One thing worth flagging: the docstring matters. The model reads it to decide when to call this tool. A vague docstring leads to misuse. A specific docstring leads to correct usage. When you write tools, write the docstring for the model to read, not for a human to read.

---

## Slide 13 — Live: three events appear

Switch to the notebook. Cells eight, nine, ten. Same chat helper, but now the agent has a tool. Watch the output grow from one event to three.

---

## Slide 14 — The event stream with a tool

Back on the slide. This is what three events look like.

First, a tool call. The model decided a tool was needed, and emitted a structured call — the tool name, the arguments. ADK intercepted it before it left the agent. The model did not execute the tool; it asked to.

Second, the tool response. ADK executed the Python function with those arguments, and fed the return value back into the conversation as a tool-response event.

Third, the final text response. The model read the tool output and wrote a natural-language answer.

Three distinct events, all visible, all inspectable. If the model had called the wrong tool, you'd see it. If it had called two tools in sequence, you'd see both. This is the shape of agent behavior — and the reason the event stream is the agent-development debugger.

---

## Slide 15 — adk web

Everything you just printed can be browsed visually. Run `adk web` from a folder containing your agent, and it opens a chat UI in your browser, with the same event stream rendered as a clickable timeline. Same data, nicer to explore.

Keep `adk web` open while you're developing. When an agent does something unexpected — returns the wrong answer, calls a tool with the wrong argument, refuses to do a thing — the reason is almost always obvious from the timeline. A tool returned the wrong shape. An instruction was ambiguous. A state key was stale.

We'll rely on the text printouts for the rest of the course because they drop cleanly into a video recording. But in your own work, `adk web` is the best debugger you get for free.

---

## Slide 16 — ADK vs. the alternatives

Fair comparison. LangGraph is the market leader, thirty-four million monthly downloads, and it wants you to draw your control flow as an explicit graph — nodes and edges. That's the right tool for complex orchestration, and heavy for anything simple. CrewAI is the opposite: a role-playing DSL, you declare a Researcher and a Writer and let the framework put them together. Fast on demos, opinionated on metaphor, forty-four thousand stars.

ADK sits in the middle. Smaller community — about eighteen thousand stars — but typed Python instead of a DSL, explicit primitives instead of metaphors, and the clearest event-level observability I've seen in any of them. If you want to read the reasoning of your own agent, ADK is the shortest path there.

---

## Slide 17 — Vendor lock-in, addressed

The single most common objection to ADK is: but it's a Google framework. Yes. Google wrote it, and Google uses it to sell Gemini and Vertex.

But the model abstraction is a one-line swap. Here it is. Gemini direct. Claude via OpenRouter. GPT via OpenRouter. Qwen running locally through Ollama. Same agent, same tools, same instruction, one line of configuration different.

Part 1 of this course — ten modules — uses OpenRouter the whole way. You can take every notebook, change the model string, and run it against Claude or GPT if you prefer. When we get to Part 2 in module eleven, we switch to Gemini because the features we teach then — search grounding, long-context caching, thinking budgets, the Live voice API — only exist on Gemini. Until then, ADK is as vendor-neutral as you want it to be.

---

## Slide 18 — The arc of the course

This is the map. Part 1, modules one through ten, is the vendor-agnostic spine. Agent, tools, sessions, workflow agents, multi-agent, callbacks, memory, evaluation, deployment. Runs on anything LiteLLM reaches.

Part 2, modules eleven through thirteen, is what you lose by not using Gemini. Search-grounded answers with citations. Long-context question-answering with caching. Thinking budgets that let you trade latency for reasoning quality. The Live voice API, which is the only genuinely jaw-dropping Gemini-only capability in this space.

And module fourteen is a short side step into A2A — the agent-to-agent protocol. Thirty minutes, because A2A is too new to teach as infrastructure but too important to skip.

---

## Slide 19 — Four artifacts per module

Every module ships four things that stay aligned with each other. These slides. Speaker notes — the ones I'm reading now, available to you as markdown, so you can re-record them in your own voice or translate them. A textbook chapter, the long-form prose version with examples. And a Jupyter notebook, the exact code you saw in the demo, runnable top-to-bottom against your own API key.

A term on a slide is the same term in the speaker notes, the same term in the textbook, the same term in the notebook. Pick the artifact that fits how you learn, and trust the others stay consistent.

---

## Slide 20 — Write these down

Agent. Runner. Event. Session. If you can say them out loud right now without looking, you're ready for module two. If you hesitated on any of them, open the notebook, re-read the event-stream output of the weather agent, and watch what each primitive is doing. Then come back.

Module two unpacks tools — we had one flavor today, a plain Python function. ADK has three more, and we'll build each. See you there.
