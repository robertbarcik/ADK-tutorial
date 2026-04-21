# M01 — Speaker notes

---

## Slide 1 — Title

Welcome to module one of the Google ADK course. This is the first of fourteen modules, and the goal of this one is narrow: by the end of the next fifteen minutes, you should be able to name four things without hesitation — Agent, Runner, Event, and Session. Those four show up in every module after this one, so if you get them clear now, the rest of the course becomes a series of small refinements on top. Let's get into it.

---

## Slide 2 — What ADK is

ADK is Google's Agent Development Kit, and it's a Python framework. Google open-sourced it, the 1.0 release shipped in May 2025, and as I record this we're on version 1.31. The reference implementation is Python, but there are also SDKs for other languages like Java, Go, and TypeScript if you need them. That said, Python is where the features land first, and it's where this course lives.

There are also four things ADK is NOT, and these come up a lot — so worth naming them up front. First, it's not a model — you bring your own. In this course, for example, we'll use Claude, GPT, and Gemma before we touch any Gemini model. Second, it's not a cloud — it runs on your laptop today, and on something like Cloud Run tomorrow. Third, it's not a UI — there's a development UI we'll see in a minute, but the output is code. And finally, it's not a graph DSL — you write typed Python, not a JSON DAG.

---

## Slide 3 — Why a framework at all

The honest test for whether any framework is worth learning is this: what do you stop writing when you adopt it? With ADK, the answer is roughly sixty lines of code you'd otherwise end up writing every single time.

Things like the retry loop when the model fails. Or the JSON parser that crashes on the fourth edge case. Or the manual conversation history that you have to truncate yourself, before the context window blows up. The switch statement that maps tool names to Python functions. And the error path for when the model hallucinates a tool that doesn't actually exist.

Frameworks earn their keep when they stop you writing this kind of boilerplate, and let you write the things that are actually yours — the instruction, the tools, the business logic. That's the deal ADK offers.

---

## Slide 4 — The agent equation

Before we meet the primitives one by one, here's the picture. An agent is really just an LLM with a few things around it — an instruction telling it how to behave, some tools it can call, a bit of memory of what happened before, and a loop that ties it all together. That's the whole equation.

ADK gives you the loop and the plumbing, while you bring the other four. Keep this picture in your head as we go through the primitives, because every one of them is a piece of this equation.

---

## Slide 5 — The four primitives

These are the four primitives I just mentioned. I'll repeat them a lot, because they are the whole mental model.

Agent is the thing the LLM lives in — so a name, a model, an instruction, and optionally some tools. Runner is what drives the conversation forward; think of it as the event loop. Event is every single thing that happens inside a run, like a message, a tool call, or a state change. And Session is the conversation's memory — the history of events, plus a state dictionary, keyed by application, user, and session ID.

Everything else in ADK — so workflow agents, multi-agent hierarchies, callbacks, memory, evaluation — composes on top of these four. Get them clear, and the rest unfolds.

---

## Slide 6 — Agent

Here's an agent. Four lines of configuration. The name is how ADK refers to it internally. The model is wrapped in the LiteLlm helper — we'll come back to this, but that wrapper is what makes ADK vendor-neutral. The description is what other agents will see if this one becomes a sub-agent. The instruction is the system prompt.

If you wanted to give this agent tools, you'd add a `tools=[...]` argument with a list of Python functions. No tools on this one yet. Just a greeter.

---

## Slide 7 — Runner

An agent on its own is inert — it doesn't do anything until the Runner picks it up. The Runner wires it to a session service, and hands you back an asynchronous event stream.

The mental model for the Runner is a game engine's main loop. Your agent is the entity that gets ticked — so on each tick, the Runner sends the current conversation state into the model, reads back what the model produces, and emits events for everything it observes. You, as the developer, then iterate over those events and make decisions from there.

If you've used something like Node.js middleware, or an Express request pipeline, the shape is familiar.

---

## Slide 8 — Event

Event is the primitive that sets ADK apart from most agent frameworks. Every single communication inside a run produces an event — and by every, I really do mean every. User message in: event. Model text response: event. Model decides to call a tool: event. Tool executes and returns a value: event. An agent hands off to a sub-agent: event. The state dictionary changes: event.

Read the events, and you can reconstruct exactly what the agent did and why. This is the debugger for agent work. When I'm teaching people ADK and they ask "how do I debug this thing", the answer is always the same — read the events.

---

## Slide 9 — Session

Session is the fourth primitive. It holds the event history, plus the state dict for one conversation, and it's keyed by a triple: application name, user ID, and session ID.

Three session services ship with ADK. The first is the in-memory one, great for demos and tests. The second is DatabaseSessionService, which runs on SQLAlchemy — so Postgres, MySQL, or SQLite — and it's what you'd use for self-hosted production. And finally there's VertexAiSessionService, if you happen to be on Google Cloud.

We'll use in-memory through module seven. In module eight, when we make memory the point, we'll swap to the database one, and a student on a laptop can run a Postgres container on the side.

---

## Slide 10 — Live: one agent, one event

All right — time to show you this in action. We're switching to the notebook now, and we'll run through cells one to seven: the setup, the simplest possible agent, and one run that produces a single event.

---

## Slide 11 — The simplest event stream

Back on the slide. This is what you just saw in the notebook: one event, marked `FINAL`, and it contains the greeter's response.

This is really the minimum a conversation can produce — the user turn goes in, one model turn comes out, and the stream ends. Nothing interesting on its own, but it establishes the baseline for what we're about to see when we add a tool.

---

## Slide 12 — Add a tool

Tools are just Python functions. That's really the whole tool model at this layer of abstraction.

You write a function with a docstring and type hints, and ADK reads both of those to build the JSON schema that the model will see. No decorators, no config files, no tool-registration dance.

Here, for example, `get_weather` takes a city string and returns a dict. That's all you need for it to count as a tool. Add it to the agent's `tools=` list, and the model can start calling it.

One thing worth flagging: the docstring really matters here. The model reads it to decide when to call this tool — so a vague docstring leads to misuse, while a specific one leads to correct usage. When you write tools, write the docstring for the model to read, not for a human to read.

---

## Slide 13 — Live: three events appear

Switch back to the notebook — cells eight, nine, ten. Same chat helper as before, but now the agent has a tool. Watch the output grow from one event to three.

---

## Slide 14 — The event stream with a tool

Back on the slide. This is what three events look like.

First, you see a tool call. The model decided a tool was needed, and emitted a structured call — so the tool name, plus the arguments. ADK intercepted that before it left the agent. Notice the model did not execute the tool itself — it only asked to.

Second, you see the tool response. ADK executed the Python function with those arguments, and then fed the return value back into the conversation as a tool-response event.

And third, the final text response. The model read the tool output, and wrote a natural-language answer.

So three distinct events, all visible, all inspectable. If the model had called the wrong tool, you'd see it. If it had called two tools in sequence, you'd see both. This is the shape of agent behavior — and the reason the event stream is the agent-development debugger.

---

## Slide 15 — adk web

Everything you just printed can also be browsed visually. Just run `adk web` from a folder that contains your agent, and it opens a chat UI in your browser, with the same event stream rendered as a clickable timeline. Same data, just nicer to explore.

Keep `adk web` open while you're developing. When an agent does something unexpected — like returning the wrong answer, calling a tool with the wrong argument, or refusing to do a thing — the reason is almost always obvious from the timeline. Maybe a tool returned the wrong shape. Maybe an instruction was ambiguous. Maybe a state key was stale.

We'll rely on the text printouts for the rest of the course because they drop cleanly into a video recording. But in your own work, `adk web` is the best debugger you get for free.

---

## Slide 16 — ADK vs. the alternatives

Here's a fair comparison with the alternatives. LangGraph is the market leader, with thirty-four million monthly downloads, and it wants you to draw your control flow as an explicit graph — so nodes and edges. It's the right tool for complex orchestration, but heavy for anything simple. CrewAI takes the opposite approach — it's a role-playing DSL, where you declare, say, a Researcher and a Writer, and let the framework put them together. It's fast on demos, opinionated on metaphor, and sits at about forty-four thousand stars.

ADK sits somewhere in the middle. It's a smaller community — about eighteen thousand stars — but you get typed Python instead of a DSL, explicit primitives instead of metaphors, and the clearest event-level observability I've seen in any of them. If you want to actually read the reasoning of your own agent, ADK is the shortest path there.

---

## Slide 17 — Vendor lock-in, addressed

The single most common objection to ADK is this: "but it's a Google framework." Yes. Google wrote it, and Google uses it to sell Gemini and Vertex.

But the model abstraction is really a one-line swap. Here it is — for example, Gemini direct. Or Claude via OpenRouter. Or GPT, also via OpenRouter. Or Qwen, running locally through Ollama. It's the same agent, same tools, same instruction — just one line of configuration different.

Part 1 of this course — so modules one through ten — uses OpenRouter all the way through. You can take every notebook, change the model string, and run it against Claude or GPT if you prefer. When we get to Part 2 in module eleven, we switch to Gemini, because the features we teach from then on — things like search grounding, long-context caching, thinking budgets, and the Live voice API — only exist on Gemini. But until then, ADK is as vendor-neutral as you want it to be.

---

## Slide 18 — The arc of the course

This is the map of the course. Part 1, modules one through ten, is the vendor-agnostic spine — so agents, tools, sessions, workflow agents, multi-agent setups, callbacks, memory, evaluation, and deployment. It runs on anything LiteLLM can reach.

Part 2, modules eleven through thirteen, is about what you lose by NOT using Gemini. Think search-grounded answers with citations. Long-context question-answering with caching. Thinking budgets that let you trade latency for reasoning quality. And the Live voice API, which is really the only genuinely jaw-dropping Gemini-only capability in this space.

And then module fourteen is a short side-step into A2A — the agent-to-agent protocol. Just thirty minutes, because A2A is too new to teach as infrastructure, but too important to skip entirely.

---

## Slide 19 — Four artifacts per module

Every module ships four things that stay aligned with each other. First, these slides you're watching now. Second, the speaker notes — the ones I'm reading right now, available to you as markdown, so you can re-record them in your own voice, or translate them if you'd like. Third, a textbook chapter, which is the long-form prose version with examples. And fourth, a Jupyter notebook — the exact code you saw in the demo, runnable top-to-bottom against your own API key.

And one key property: a term on a slide is the same term in the speaker notes, the same term in the textbook, and the same term in the notebook. So pick whichever artifact fits how you learn, and trust that the others stay consistent.

---

## Slide 20 — Write these down

Agent. Runner. Event. Session. If you can say those out loud right now without looking, you're ready for module two. If you hesitated on any of them, open the notebook, re-read the event-stream output of the weather agent, and watch what each primitive is actually doing. Then come back.

Module two is where we unpack tools. We had one flavor today — the plain Python function. ADK actually has three more flavors, and we'll build one of each. See you there.
