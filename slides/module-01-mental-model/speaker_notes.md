# M01 — Speaker notes

---

## Slide 1 — Title

Welcome to module one. This is the foundation of the course, where we set up the mental model that everything else builds on. Our broader goal in this course is to learn how to build production-ready AI agents in Python using Google's Agent Development Kit. But before we touch any deep code, we'll spend some time meeting the four primitives that show up in every later module: Agent, Runner, Event, and Session.

These four primitives are the whole mental model of ADK. Once they're clear in your head, the rest of the framework, and the rest of the course, unfold as a natural progression on top of them. Let's get started.

---

## Slide 2 — What ADK is

ADK is Google's Agent Development Kit, a Python framework for building agents. Google open-sourced it, the 1.0 release shipped in May 2025, and as I'm recording this we're on version 1.31. There are SDKs for Java, Go, and TypeScript too, but Python is where the features land first, and it's where this course lives.

Now, four things ADK is NOT, because these come up a lot, and it's worth naming them up front. It's not a model. You bring your own, and in this course we'll be using Claude, GPT, and Gemma long before we touch a Gemini model. It's not a cloud either. It runs on your laptop today and on something like Cloud Run tomorrow, with no Google-Cloud dependency required. It's not a UI. There's a development UI called `adk web` that we'll see in a minute, but the deliverable is code, not screens. And finally, it's not a graph DSL. You write typed Python, not a JSON DAG.

---

## Slide 3 — Why a framework at all

The honest test for whether any framework is worth learning is this: what do you stop writing when you adopt it? With ADK, the answer is roughly sixty lines of code you'd otherwise end up writing every single time you build an agent by hand.

You stop writing the retry loop that wraps the LLM call when the network blinks. You stop writing the JSON parser that handles the first three tool responses fine and dies on the fourth, because the model decided to put a comment inside the JSON. You stop writing your own conversation-history bookkeeping, manually truncating it before the context window blows up. And you stop writing both halves of tool dispatch: the switch statement that maps tool names to functions, and the error path for when the model invents a tool that doesn't even exist.

Frameworks earn their keep when they stop you writing this kind of boilerplate, and let you write the things that are actually yours: the instruction, the tools, the business logic. That's the deal ADK is offering.

---

## Slide 4 — The agent equation

Before we meet them one by one, here's the picture in a single line. An agent is really just an LLM with a few things around it: an instruction telling it how to behave, some tools it can call, a bit of memory of what happened before, and a loop that ties it all together. That's the whole equation.

ADK takes care of the loop and the wiring around it. The four pieces you bring are the LLM, the instruction, the tools, and the memory, and you can see them right there on the slide. Keep that picture handy as we walk through the primitives, because the four primitives you'll meet are just ADK's way of packaging up this equation.

---

## Slide 5 — The four primitives

These are the four primitives I just mentioned. I'll repeat them a lot, because they are the whole mental model.

Agent is the thing the LLM lives in: a name, a model, an instruction, and optionally some tools. Runner is what drives the conversation forward, the event loop you can think of as a tick-by-tick game engine. Event is every single thing that happens inside a run: a user message, a model response, a tool call, a state change. And Session is the conversation's memory, the history of events plus a state dictionary, keyed by application, user, and session ID.

Everything else in ADK composes on top of these four primitives: workflow agents, multi-agent hierarchies, callbacks, memory services, evaluation, all of it. Get the four right, and the rest of the course unfolds.

---

## Slide 6 — Agent

Here on the slide we have an Agent called `greeter`, whose only job is to respond to users in a friendly one-sentence message. To define any Agent in ADK, you need four required arguments, and you can see all four right here. The name is how ADK refers to the agent internally and in events. The model is wrapped in the LiteLlm helper, and that wrapper is what makes ADK vendor-neutral, which we'll see in a few slides. The description is the one-liner that other agents see when this one becomes a sub-agent in a hierarchy. And the instruction is the system prompt, the text the model reads to decide how to behave.

If you wanted to give this agent tools, you'd add a `tools=[...]` argument with a list of Python functions. There aren't any here, because this agent is just a greeter.

---

## Slide 7 — Runner

Look at the slide for a moment. To actually run our greeter agent, we need a Runner. We create one, pass it the agent and a session service, then iterate over the events the run produces in an async loop. That's the actual machinery of an ADK conversation.

So why do we need a Runner at all? An agent on its own is inert. It doesn't do anything until something picks it up and drives the conversation forward. That something is the Runner. It wires the agent to a session service and hands you back an asynchronous event stream.

The mental model for the Runner is a game engine's main loop. Your agent is the entity that gets ticked. On each tick, the Runner pushes the current conversation state into the model, pulls back what the model produces, and emits an event for every observable step. You iterate over those events and decide what to do with each.

If you've worked with Node.js middleware or an Express request pipeline, the shape is familiar. Same idea: events flow through, you handle them, you act.

---

## Slide 8 — Event

Event is the primitive that sets ADK apart from most agent frameworks. Every single communication inside an agent run produces an event, and by every, I really do mean every. When the user sends a message in, that's an event. When the model writes a response, that's another event. When the model decides to call a tool, the call itself is an event, and so is the value the tool returns. When one agent hands off to a sub-agent in a hierarchy, you see that as an event too. Even a change to the state dictionary fires its own event.

Read the events, and you can reconstruct exactly what the agent did and why. This is the debugger for agent work. When students ask me how to debug an ADK agent, the answer is always the same: read the events.

---

## Slide 9 — Session

Session is the fourth primitive. It holds the event history plus a state dictionary for one conversation, and it's keyed by a triple: application name, user ID, and session ID. One conversation, one session.

Three session services ship with ADK. The first is `InMemorySessionService`, a Python dictionary that lives only as long as your process. It's great for demos and tests, and it's what we'll use for most of the course. The second is `DatabaseSessionService`, which runs on SQLAlchemy, so anything from SQLite on a laptop up to a managed Postgres in production. That's the one you'd reach for in a self-hosted ADK service. And finally there's `VertexAiSessionService`, the one you'd use if you're already running on Google Cloud and Vertex.

For most of this course we'll stay on the in-memory service. Later in the course, when persistent memory becomes the focus of an entire module, we'll swap to the database service, and you'll be able to run a Postgres container on the side of your laptop to follow along.

---

## Slide 10 — The simplest event stream

Here's what one event looks like in practice. The user sends in "Hi, what's your name?", and a single event comes back, marked `FINAL`, containing the greeter's response.

This is the minimum a conversation can produce. The user turn goes in, one model turn comes out, the stream ends. Nothing interesting on its own, but it establishes the baseline for what happens when we add a tool to the same agent.

---

## Slide 11 — Add a tool

Here we have a function called `get_weather` that takes a city name and returns a small dictionary with a weather report for that city. Below it, we have an agent that's been configured to call this function whenever the user asks about the weather. That's our tool example.

The point this slide is making is what counts as a tool in ADK. Tools are just Python functions. That's really the whole tool model at this layer of abstraction.

You write a function with a docstring and type hints, and ADK reads both of those to build the JSON schema that the model will see. No decorators, no config files, no tool-registration dance.

One thing worth flagging up front: the docstring really matters. The model reads it to decide when to call this tool, so a vague docstring leads to misuse, and a specific one leads to correct usage. The rule is simple: when you write tools, write the docstring for the model to read, not for a human to read.

---

## Slide 12 — The event stream with a tool

Here's what three events look like in practice, once the agent has a tool to call.

First, you see a tool call. The model decided a tool was needed and emitted a structured call: the tool name plus the arguments. ADK intercepted that before it left the agent. Notice the model did not execute the tool itself. It only asked to.

Second, you see the tool response. ADK executed the Python function with those arguments, and then fed the return value back into the conversation as a tool-response event of its own.

And third, the final text response. The model read the tool output, and wrote a natural-language answer for the user.

So three distinct events, all visible, all inspectable. If the model had called the wrong tool, you'd see it in the first event. If it had called two tools in sequence, you'd see both calls, both responses, and then the final answer. This is the shape of agent behavior, and it's the reason the event stream is the agent-development debugger.

---

## Slide 13 — adk web

Everything you just printed can also be browsed visually. Run `adk web` from a folder that contains your agent, and it opens a chat UI in your browser, with the same event stream rendered as a clickable timeline. Same data, just nicer to explore.

Keep `adk web` open while you're developing. When an agent does something unexpected, whether it's returning the wrong answer, calling a tool with the wrong argument, or refusing to do something it should, the reason is almost always obvious from the timeline. Maybe a tool returned the wrong shape. Maybe an instruction was ambiguous. Maybe a state key was stale.

We'll rely on the text printouts for the rest of the course because they drop cleanly into a video recording. But in your own work, `adk web` is the best agent debugger you get for free.

---

## Slide 14 — ADK vs. the alternatives

Here's a fair comparison with the alternatives. LangGraph is the market leader, with thirty-four million monthly downloads, and it wants you to draw your control flow as an explicit graph: nodes and edges. It's the right tool for complex orchestration, but it's heavy for anything simple. CrewAI takes the opposite approach. It's a role-playing DSL, where you declare a Researcher and a Writer, say, and let the framework put them together. Fast on demos, opinionated on metaphor, and it sits at about forty-four thousand stars.

ADK sits somewhere in the middle. It's a smaller community, about eighteen thousand stars, but you get typed Python instead of a DSL, explicit primitives instead of metaphors, and the clearest event-level observability I've seen in any of them. If you want to actually read the reasoning of your own agent step by step, ADK is the shortest path there.

---

## Slide 15 — Vendor lock-in, addressed

On the slide are four different model declarations, each pointing to a different LLM. Gemini directly from Google. Claude via OpenRouter. GPT via OpenRouter. And a Qwen model running locally on your laptop through Ollama. Same agent, same tools, same instruction, just a different `model=` line.

So why does this slide exist? The single most common objection to ADK is this: "but it's a Google framework." Yes. Google wrote it, and Google uses it to sell Gemini and Vertex. But that doesn't mean you have to use Gemini. The model abstraction is genuinely a one-line swap, and those four declarations on the slide are everything you need to change.

Part 1 of this course uses LiteLLM against OpenRouter all the way through. You can take every notebook, change the model string, and run it against Claude or GPT or Gemma if you prefer. Once we get to Part 2, we switch to Gemini directly, because the features we teach from then on, like search grounding, long-context caching, thinking budgets, and the Live voice API, only exist on Gemini. Until then, ADK is as vendor-neutral as you want it to be.

---

## Slide 16 — The arc of the course

This is the map of the course. Part 1 is the vendor-agnostic spine: agents, tools, sessions, workflow agents, multi-agent setups, callbacks, memory, evaluation, and deployment. All of it runs on anything LiteLLM can reach.

Part 2 is about what you lose by not using Gemini. Search-grounded answers with citations, where the model can hit Google and cite the URL it pulled from. Long-context question-answering with caching, so you can keep a million tokens of context in cache and pay only for the prompt. Thinking budgets that let you trade latency for reasoning quality. And the Live voice API, which is the only genuinely jaw-dropping Gemini-only capability in this space.

And then the final module is a short side step into A2A, the agent-to-agent protocol. It's deliberately short, because A2A is too new to teach as infrastructure, but too important to skip entirely.

---

## Slide 17 — Four artifacts per module

Every module ships four artifacts that stay aligned with each other. First, the slides you're watching now. Second, the speaker notes I'm reading right now, available as markdown so you can re-record them in your own voice, translate them, or just read them. Third, a textbook chapter, the long-form prose version with worked examples and gotchas. And fourth, a Jupyter notebook with the exact code you saw in the demo, runnable top-to-bottom against your own API key.

One key property holds across all four: a term defined on a slide is the same term in the speaker notes, the same term in the textbook, and the same term in the notebook. So pick whichever artifact fits how you learn best, and trust that the others stay consistent.

---

## Slide 18 — Write these down

Agent. Runner. Event. Session. If you can say those four out loud right now without looking at the slide, you're ready for the practical part. If you hesitated on any of them, scroll back through the event-stream illustrations on the previous slides and re-read what each primitive is actually doing.

In the notebook walkthrough that comes next, you'll run all of this yourself: build the greeter, add the weather tool, and watch the event stream grow from one event to three. See you there.
