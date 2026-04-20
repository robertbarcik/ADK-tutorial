# Why agents, why ADK

The first time anyone builds an agent by hand, they end up writing roughly the same sixty lines of code. A retry loop around the LLM call because the API occasionally times out. A JSON-output parser that crashes on the fourth edge case and needs a try-except wrapper. A manual conversation-history list that outgrows the context window after twelve turns and starts costing money in ways that surprise the billing department. A switch statement that dispatches tool calls to Python functions, because the model keeps emitting structured tool requests and somebody has to execute them. Error handling for the day the model hallucinates a tool that doesn't exist, and the handler that prompts it to try again without the hallucination.

Sixty lines. Every time.

A framework earns its keep when it stops you writing that boilerplate. You write the things that are actually yours — your instruction, your tools, your business logic — and the framework handles the plumbing. That's the deal ADK is offering.

This chapter establishes the mental model that every later chapter builds on. Four primitives. Agent, Runner, Event, Session. Write them on a sticky note. Say them out loud. They will show up in every subsequent chapter, and by the end of the course you will have added dozens of concepts on top of them, but none of those concepts require you to forget the four.

## What ADK is, and what it isn't

ADK is Google's open-source Python framework for building LLM-driven agents. The 1.0 release shipped in May 2025; as of April 2026 it sits at v1.31, with biweekly releases. The Python implementation is the reference; there are Java, Go, and TypeScript SDKs if you need them, but features land in Python first and this course lives there.

Four things ADK is not, because these matter:

**It is not a model.** You bring your own. Gemini, Claude, GPT, Qwen, Gemma — it doesn't care. This is the single point people miss when they hear "Google's agent framework" and assume Gemini is bundled in. It isn't. We'll prove this by module four, at which point the same agent from module one will be running on Claude and on a locally-hosted open-weight model without a line of logic changing.

**It is not a cloud.** It runs on your laptop today, and on Google Cloud Run, AWS Fargate, Azure Container Apps, or a Raspberry Pi tomorrow. The deployment story is a Dockerfile, and the Dockerfile is yours to write. ADK ships a `deploy cloud_run` command because it lives in Google's ecosystem, but it is a convenience, not a requirement.

**It is not a UI.** It ships a development UI (`adk web`), which we'll see in a minute, but the output of an ADK project is code you deploy, not a dashboard you sell. The dev UI exists for the same reason any framework ships a dev server: to make the developer experience survivable.

**It is not a graph DSL.** You write typed Python. Not JSON, not YAML, not a node-and-edges diagram. When you want a loop, you use a loop construct. When you want control flow to run in parallel, you say so. This is probably the single largest difference between ADK and LangGraph, and it matters if you write Python for a living.

## The agent equation

Before the primitives, the picture.

An agent is an LLM, plus an instruction telling it how to behave, plus some tools it can call, plus some memory of what has happened so far, plus a loop that ties it all together. That is the whole equation.

ADK supplies the loop and the plumbing around it. You supply the other four. Keep this picture in your head as we go through the primitives — every one of them is a concrete piece of this equation.

## The four primitives

### Agent

An `Agent` is a configuration object. Four required fields — name, model, description, instruction — and one optional field that matters: `tools`.

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

greeter = Agent(
    name="greeter",
    model=LiteLlm(model="openrouter/google/gemini-2.5-flash-lite"),
    description="Greets the user in a friendly way.",
    instruction="You are a friendly greeter. Respond in one short sentence.",
)
```

The name is how ADK refers to this agent internally, and how other agents refer to it if they need to delegate work to it. The model is wrapped in the `LiteLlm` helper, which is what makes ADK model-agnostic: we'll swap the model string three ways in module four and the rest of the code won't change. The description matters when this agent is a child of another agent — the parent's LLM reads the description to decide whether to route a task here. And the instruction is, for our purposes, the system prompt.

If you add `tools=[get_weather, lookup_ticket]`, the agent can call those Python functions. We'll do exactly that in the next few paragraphs.

### Runner

An `Agent` on its own does nothing. It is inert. The `Runner` is what wires the agent to a session service and turns it into a working conversation.

```python
runner = Runner(
    agent=greeter,
    app_name="demo",
    session_service=InMemorySessionService(),
)

async for event in runner.run_async(
    user_id="student",
    session_id="s1",
    new_message=types.Content(role="user", parts=[types.Part(text="hi")]),
):
    print(event)
```

The mental model: the Runner is a game engine's main loop, and your agent is the entity being ticked on each frame. The Runner sends the current conversation state into the model, reads the response, dispatches tool calls if there are any, and emits events for everything it observes. You iterate over those events with a Python `async for` and make decisions based on what you see.

If you have used Express.js or Django middleware, the shape is familiar. Something external drives requests through a pipeline, and you observe or intervene at well-defined points along the way.

### Event

`Event` is the primitive that sets ADK apart from most agent frameworks, and it is the one worth paying the most attention to.

Every communication inside an agent run produces an Event. The user's message is an event. The model's text response is an event. The model's decision to call a tool is an event, distinct from the tool's actual execution, which is a different event. A state-dictionary change is an event. An agent handing off to a sub-agent is an event.

You don't have to do anything special to see events — they are what `run_async` yields. You iterate over them, read what happened, and act accordingly.

```
USER: What's the weather in Prague?

[tool_call] get_weather({'city': 'Prague'})
[tool_resp] {'city': 'Prague', 'report': 'Cloudy, 14°C'}
[FINAL]     weather_agent: Prague is cloudy and 14°C.
```

Three events, each one inspectable. If the model had called the wrong tool, you would see it in the first event. If the tool had returned a different shape than expected, you would see it in the second. If the model had misread the tool's output, you would see it in the third. The gap between "the agent did something weird" and "I know exactly why" is almost always a matter of reading one more event.

This is the debugger for agent work. When someone asks me how to debug an ADK agent, the honest answer is: print the events. Everything else is a special case of that.

### Session

The fourth primitive. A `Session` holds the event history and a state dictionary for one conversation, keyed by the triple `(app_name, user_id, session_id)`.

Three session services ship with ADK.

- **`InMemorySessionService`** — a Python dict. Loses everything on process restart. Appropriate for demos, tests, and notebooks. This is what we'll use from module one through module seven.
- **`DatabaseSessionService`** — SQLAlchemy-backed, runs against Postgres, MySQL, or SQLite. Appropriate for self-hosted production. We'll swap to this in module eight, when memory becomes the point of the chapter.
- **`VertexAiSessionService`** — managed, Google-Cloud-only. Mentioned in this course, not taught — the pattern is the same, only the backing store changes.

State is a dict that lives inside the session. Module three will be entirely about what you can and should put in it, and how the prefixes (`user:`, `app:`, `temp:`) work. For now, it is enough to know that every session has one.

## Event stream as debugger

The single best development habit you can build with ADK is reading the event stream as the agent runs. Other frameworks make you reach for a separate tracing tool to see what the model is doing. ADK puts it in front of you by default.

When an agent does something unexpected — returns the wrong answer, calls a tool with the wrong argument, refuses to do a thing it should have done — the reason is almost always visible in the event stream. A tool returned the wrong shape. An instruction was ambiguous. A state key was stale. A sub-agent was routed to when it shouldn't have been. You don't need to guess; you read the events.

There is also a visual version of this. Run `adk web` from a folder containing your agent, and it opens a browser chat UI with the event stream rendered as a clickable timeline beside the conversation. Same data, friendlier to explore. Keep `adk web` open while you're developing an agent — the time savings are substantial. For the rest of this course we'll rely on text printouts because they drop into recorded video cleanly, but in your own work, the web UI is the default.

## Why not LangGraph, why not CrewAI

These are fair comparisons and worth being honest about.

**LangGraph** is the current market leader. Thirty-four million monthly downloads, strong documentation, large community, an explicit graph-DSL approach where you declare nodes and edges. If your control flow is complex — conditional branches, multiple fan-out/fan-in points, cycles — LangGraph's graph model is a good fit, because it forces you to make the control flow legible. For anything simpler, the ceremony outweighs the benefit.

**CrewAI** is at the other end of the spectrum. Forty-four thousand stars, role-playing DSL — you declare a Researcher, a Writer, an Editor, and let the framework orchestrate them. Demos beautifully. The metaphor gets in the way once your use case is something that doesn't map to "team of human specialists collaborating."

**ADK** sits in the middle. Smaller community — about eighteen thousand GitHub stars, two hundred contributors, under three thousand dependent projects — but the case for it rests on three things the others don't do as well: explicit event-level observability, workflow agents as first-class typed primitives, and the cleanest vendor-neutrality story via LiteLLM.

If you're choosing a framework for a team, the right answer depends on your control-flow complexity and the vocabulary your team already uses. If you're choosing one to learn, ADK teaches you concepts that transfer cleanly to the others, which makes it an unusually good teaching vehicle.

## "But ADK is a Google framework"

This is the single most common objection, and it's fair to name it here rather than hiding it. Google wrote ADK, Google maintains it, and Google has commercial incentives — it wants you to use Gemini and deploy on Vertex AI.

The model question is settled in one line of code. `LlmAgent(model="gemini-2.5-flash")` is Gemini. `LlmAgent(model=LiteLlm(model="openrouter/anthropic/claude-haiku-4-5"))` is Claude. `LlmAgent(model=LiteLlm(model="ollama_chat/qwen3:8b"))` is a locally-hosted Qwen3. The rest of the code — the tools, the instruction, the session, the runner — does not change.

Part 1 of this course uses OpenRouter with LiteLLM the whole way. Ten modules' worth of material, running against whatever model you pick, with the code unchanged. When we get to Part 2 in module eleven, we switch to Gemini directly because the features we teach then — Google Search grounding, long-context caching, thinking budgets, the Live voice API — only exist on Gemini, and swapping that out for Claude would break the chapter. Until then, ADK is as vendor-neutral as you want it to be.

The deployment question is the same shape. `adk deploy cloud_run` is a convenience. The container that command produces is a regular Docker container that runs on any cloud that runs Docker containers. We'll build one in module ten and deploy the same image two ways to prove the point.

## What to leave this chapter with

Four words. Agent, Runner, Event, Session.

If you can say them out loud without looking at your notes, you're ready for the next module. If any of the four is still fuzzy, re-read this chapter, and then open the notebook and watch the event stream of the weather agent. Every concept in this chapter corresponds to something visible in that notebook's output, and the mapping between the concepts and the output is what makes the mental model real.

Module two picks up tools as a first-class topic. You saw one flavor — a plain Python function — in the demo. ADK has three more: an OpenAPI specification consumed wholesale, an MCP server connected as a tool source, and another agent wrapped to look like a tool. Each of the four has a time it's the right answer. That's next.
