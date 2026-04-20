# Sessions, State, Events, Artifacts

Module 01 gave you four primitives: Agent, Runner, Event, Session. Module 02 built on the first two. This chapter goes deep on the third, which is where the agent's memory actually lives. A stateless agent is a demo. A stateful agent is infrastructure. The difference is entirely about how you use the Session.

## A session is two things

A session is identified by a triple: `(app_name, user_id, session_id)`. Those three strings are the primary key for every session in every session store, regardless of which backend you're using. Inside the session live two collections.

The first is a **list of events** — the full ordered history of every user message, every model response, every tool call, every tool response, every state mutation. You don't append to this list; ADK does, as things happen. Your code reads it when it wants to audit what happened, replay a conversation, or feed a run into an evaluation suite.

The second is a **state dictionary** — mutable key-value storage for whatever you want the agent to carry between turns. This is where the action is.

ADK ships three session services:

- **`InMemorySessionService`** — backs everything by a Python dict. Loses on process restart. This is what we'll use through Module 07. Perfect for tests, notebooks, and demos.
- **`DatabaseSessionService`** — SQLAlchemy-backed. Works against Postgres, MySQL, SQLite. This is the production default for self-hosted deployments. Module 08 swaps to it when memory becomes the subject.
- **`VertexAiSessionService`** — managed, Google-Cloud-only. Mentioned in this course; not taught — the pattern is the same, only the backing store changes.

The interface is identical across all three. The agent code does not change when you swap the service, which is the whole point of the abstraction.

## State with scope prefixes

This is the most useful under-documented feature in ADK, and the one you will use every day.

A state dict is a regular Python dict. But the key's **prefix decides where the value lives and how long it survives.** Four tiers.

| Prefix | Scope | Survives |
|---|---|---|
| *(none)* | This session only | Until the session is deleted |
| `user:` | This user, across all their sessions | As long as the user exists |
| `app:` | Global across all users of this app | As long as the app exists |
| `temp:` | This invocation only | Thrown away after the run |

Think of it as React state with persistence tiers baked into the key. You decide the lifetime of every piece of data with a 5-character prefix; ADK handles the routing.

In practice:

- **Unprefixed** is the default. A favorite color you learn mid-conversation and only need for this session's replies. A draft the agent is composing.
- **`user:`** for per-user persistence. Favorite colors, language preferences, history summaries — anything that's specific to one user but should persist across all their sessions with your app.
- **`app:`** for global configuration. A daily-changing prompt template every agent should use. A shared rate-limit counter. Rare in practice; reach for it cautiously.
- **`temp:`** for scratchpads inside a single run. A tool that needs to hand a value to the next tool in the same turn. A calculation the agent would rather not expose in the final event log.

Pick the scope when you write, and ADK handles persistence accordingly.

## Writing state — three ways, one of which is a trap

Three patterns for writing state. Two of them persist. One of them silently fails. It is almost always the one a new developer reaches for first.

**Pattern 1 — `output_key=` on the agent.** When you construct an `LlmAgent`, pass `output_key="last_response"` (or whatever key you want). After every run, the model's final text response is automatically written to `state[output_key]`. This is the cleanest way to cache a final answer, and — more importantly — it's how you pass output between workflow-agent steps, which Module 05 will lean on heavily.

```python
agent = LlmAgent(
    name="color_agent",
    model=LiteLlm(model=MODEL_STRING),
    instruction="...",
    tools=[...],
    output_key="last_response",   # final text auto-saved to state['last_response']
)
```

**Pattern 2 — `tool_context.state[key] = value` inside a tool.** Your tool function gets an extra parameter, `tool_context: ToolContext`. ADK injects the running context automatically; you don't pass it in. From inside the tool, `tool_context.state` behaves like a mutable dict. Writes are recorded as events and persisted by the session service.

```python
def remember_favorite_color(color: str, tool_context: ToolContext) -> dict:
    """Record the user's favorite color for future sessions."""
    tool_context.state["user:favorite_color"] = color
    return {"status": "saved", "color": color}
```

Two subtleties to notice: the parameter is `tool_context` — ADK looks for exactly that name. And the `user:` prefix on the key is what makes the value survive beyond this session. Drop it, and the value is session-local.

**Pattern 3 — direct assignment to a returned session's `.state` dict. Does NOT persist.** You fetch a session with `session_service.get_session(...)`, get back a Session object with a `.state` dict, and you assign to it:

```python
session = await session_service.get_session(app_name=APP, user_id=USER, session_id=SID)
session.state["user:foo"] = "bar"   # ← does not persist
```

Next time you call `get_session()` for the same triple, your assignment is gone. Nobody tells you. You just wonder why state isn't sticking.

The reason is event sourcing: ADK persists state *via events*. Patterns 1 and 2 both produce state-delta events that the session service writes to the backing store. Pattern 3 is a dict assignment on an in-memory object; no event is generated; nothing is persisted.

**Rule to carry forward:** use `output_key=` on the agent for final-text caching, and `tool_context.state[...]` inside a tool for structured writes. Treat a fetched session's `.state` as read-only.

## The cross-session wow demo

The notebook for this module ships a complete version. Here is the essence.

```python
APP = "m03_demo"
USER = "alice"

def remember_favorite_color(color: str, tool_context: ToolContext) -> dict:
    tool_context.state["user:favorite_color"] = color
    return {"status": "saved", "color": color}

def recall_favorite_color(tool_context: ToolContext) -> dict:
    color = tool_context.state.get("user:favorite_color")
    return {"known": bool(color), "color": color}

agent = LlmAgent(
    name="color_agent",
    model=LiteLlm(model=MODEL_STRING),
    instruction=(
        "You track the user's favorite color. When they tell you one, call "
        "remember_favorite_color. When they ask, call recall_favorite_color. "
        "Be brief."
    ),
    tools=[remember_favorite_color, recall_favorite_color],
)
```

**Session 1:** the user says "my favorite color is teal." The agent calls `remember_favorite_color("teal")`. The tool writes `user:favorite_color = "teal"` to the state.

**Session 2:** a brand-new session for the same user. No initial state passed. But the session's `.state` *starts* with `user:favorite_color: "teal"` — because the `user:` prefix made the value survive across sessions.

The user asks, "what's my favorite color?" The agent calls `recall_favorite_color()`, which reads the key, returns `"teal"`. The model replies "teal."

Cross-session memory. No database setup. No vector store. No custom embedding pipeline. A prefix on a dict key.

## Events — the session's immutable ledger

Every turn produces events, and the session keeps them all. `session.events` gives you the full audit log: every user message, every model response, every tool call, every tool response, every state mutation recorded as a `state_delta`.

A condensed example from the color demo:

```
[ 0] user         text(My favorite color is teal.)
[ 1] color_agent  tool_call(remember_favorite_color)
[ 2] color_agent  tool_resp | state_delta(['user:favorite_color'])
[ 3] color_agent  text(Awesome!) | state_delta(['last_response'])
```

Four events. Two state deltas. The state dict is a **projection** of the event stream — when you fetch a session, ADK replays the events in order, applies the state deltas, and hands you the final state. This is event sourcing, and it's why Module 08 can swap in-memory sessions for database sessions without changing the agent code. The data model is the same; only the storage changes.

Read-only from your code's perspective. You don't build events yourself. You read them when you need to understand what happened, or when you hand them to an evaluation suite (Module 09) for trajectory testing.

## Artifacts — binary blobs outside the event stream

A brief word on the fourth concept.

**Artifacts** are for binary data — images, audio clips, PDFs, any large payload — that you want associated with a session but don't want serialized into events. The analogy: [Git LFS](https://git-lfs.com) for agents. The pointer lives in the event stream; the payload lives in a separate store.

Three artifact services mirror the session services:

- `InMemoryArtifactService` — demos and tests.
- `GcsArtifactService` — Google Cloud Storage, for production.
- Roll your own `BaseArtifactService` for S3, Azure Blob, MinIO, whatever.

You won't need artifacts for the text-only agents in Part 1 of this course. Module 13 (Live API voice agent) is the first module where they carry real weight — audio clips need to live somewhere that isn't the event stream.

## Interlude — Skeptical Memory

*From the Agentic Design Patterns publication, Chapter 2: The Persistent Context Problem. The pattern has a name: Skeptical Memory. It is worth two minutes.*

The wow demo in this chapter looks clean because the state has not had time to go stale. In production, this is not how it works.

A user's favorite color from three months ago is probably still their favorite color. Their current project, maybe not — they might have switched projects and never told the agent. The tickets the agent "remembered" being open yesterday might all be closed by now. A server IP an MCP tool cached might have been reassigned. The client name in `user:current_client` might refer to a client the user no longer works with.

**Stored memory is a hint, not a fact.**

Three guidelines, condensed from the publication:

1. **Prefer retrieval over recall for high-stakes decisions.** Before the agent sends an email, charges a card, deploys code, or takes any action with irreversible consequences, it should call a read-only tool to re-verify the relevant state — not act on its own stored memory. The cost of one extra tool call is trivial compared to the cost of acting on stale information.
2. **Scope your state aggressively.** `temp:` for scratchpads inside a single run. Unprefixed for per-session. `user:` only for things you are confident change only on explicit user action. `app:` only for genuinely immutable configuration. The more narrowly scoped the data, the less staleness it can cause.
3. **Log a reason when you write `user:` or `app:` state.** Months from now, when you're debugging an agent acting on six-month-old memory, a one-line "why did this get stored" note saves hours of investigation. Future you will thank present you.

The pattern's name captures the spirit: **Skeptical Memory**. Treat your own stored context as unverified hints, not facts. Verify before acting on anything consequential.

Module 08 picks up this thread when we move from session state into long-term memory — where the staleness problem gets its full treatment.

## What to carry forward

From this chapter, five things:

- A **Session** is `(app_name, user_id, session_id)`. It holds events (immutable ledger) and state (mutable dict).
- **Scope prefixes** on state keys decide lifetime: unprefixed is session-only, `user:` is per-user, `app:` is global, `temp:` is per-invocation.
- **Two state-write patterns persist**: `output_key=` on the agent, and `tool_context.state[key] = value` inside a tool.
- **Direct assignment to a fetched session's `.state`** does not round-trip. Use the two patterns above.
- **Skeptical Memory**: stored state is a hint, not a fact. Verify before acting on high-stakes decisions.

Module 04 opens up the `LiteLlm` wrapper we've been using since M01. The one-line model swap: Claude, GPT, Qwen via OpenRouter, and a locally-hosted Ollama model — same agent code, different provider — plus the one prefix gotcha that causes infinite tool-call loops if you get it wrong.
