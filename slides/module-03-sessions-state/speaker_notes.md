# M03 — Speaker notes

Written as spoken delivery. Read one section per slide.

---

## Slide 1 — Title

Module three. Sessions, State, Events, Artifacts. Module one gave you the four primitives; module two gave you tools. This module goes deep on the third primitive — Session — and everything inside it. If module two was about what an agent can do, module three is about what an agent remembers. Get this right and your agents become infrastructure. Get it wrong and they're party tricks that forget everyone's name every Monday.

---

## Slide 2 — Stateless vs stateful

The framing. A stateless agent is a party trick. Each turn starts from zero; it can't remember what you told it five minutes ago, let alone yesterday. A stateful agent is infrastructure. It knows who its users are, what they've asked before, what decisions it's already made. That's the difference between a demo and a product.

---

## Slide 3 — A session is two things

A session is identified by three strings: app name, user ID, session ID. That triple is the primary key for every session in every session store, regardless of backend.

A session holds two things. A list of events — the full ordered history of every message, every tool call, every tool response, every state mutation. You can't append to it from your code; ADK does that. Read-only from your side.

And a state dict — mutable key-value storage for whatever you want the agent to carry between turns. This is where the action is.

---

## Slide 4 — Three session services

ADK ships three session services. In-memory, which backs everything by a Python dict — loses on process restart, perfect for tests and notebooks. Database-backed, using SQLAlchemy, which works against Postgres, MySQL, SQLite — this is the production default. And Vertex-AI-backed, which you only reach for if you're on Google Cloud and committed to it.

The interface is the same across all three. When module eight promotes memory to the subject, we'll swap the in-memory service for the database one and the agent code does not change. That's the point of the abstraction.

---

## Slide 5 — State section header

Now the important part. State with scope prefixes. This is the most useful under-documented feature in ADK, and the one you'll use every single day.

---

## Slide 6 — Four scope tiers

The state dict is a regular Python dict, but the key's prefix decides the lifetime of the value. Four tiers.

Unprefixed keys live in this session only. When the session is deleted, they're gone.

`user:` prefix — pronounced "user colon" — persists across all sessions for this user. If Alice has session one and session two, anything she writes to `user:favorite_color` in session one is visible in session two.

`app:` prefix is global across the application. Every user sees the same `app:` values. Reserve this for genuinely application-wide things.

`temp:` prefix is per-invocation only. The value lives for this one run and gets thrown away when the run ends. Useful for scratch work a tool needs to carry across steps.

Four rings of scope. You pick the ring by choosing the prefix.

---

## Slide 7 — Mental model

Visual version. App state is the outermost ring — everyone sees it. User state is inside, per-user. Session state is inside that — per-session for one user. Temp state is at the center — gone when the run ends.

Pick the right ring when you write. A favorite color is `user:` — it shouldn't leak to other users, but it should survive the session. A system prompt template is `app:` — every user uses the same one. A current turn's scratch computation is `temp:` — nobody else needs to see it, ever.

---

## Slide 8 — Writing state from a tool

Here's the pattern for writing state. The tool function takes an extra parameter — `tool_context: ToolContext`. ADK injects the running context automatically; you don't pass it in. From that context, `tool_context.state` behaves like a dict. Assignments to it are recorded as events and persisted by the session service.

Two things to notice in the code. The parameter is `tool_context` with an underscore — ADK looks for exactly that name, not `context` or `ctx`. And the `user:` prefix on the key is what makes the value survive beyond this session. Drop the prefix, and the value disappears when the session does.

---

## Slide 9 — Live: cross-session memory

Switch to the notebook, cells eleven through fifteen. We create an agent that can remember and recall a favorite color. Session one, we tell it teal. Session two — a fresh session, same user — we ask it what our color is. Watch the event stream.

---

## Slide 10 — The wow moment

Back on the slide. This is what just happened.

Session one: user says "my favorite color is teal." The agent calls `remember_favorite_color` with `color='teal'`. The tool writes `user:favorite_color = 'teal'` into the state. Session ends.

Session two starts. We didn't pass any initial state. But the session's state *starts* with `user:favorite_color: 'teal'` already present. Because the key was prefixed with `user:`, ADK carried it across when it loaded session two.

User asks "what's my favorite color?" The agent calls `recall_favorite_color`, which reads `user:favorite_color`, returns `"teal"`. The model says "teal."

Cross-session memory. No database setup. No vector store. No custom embedding pipeline. A prefix on a dict key.

---

## Slide 11 — Three ways to write state

Three patterns for writing state. Two of them work. One of them doesn't — and it's the one people reach for first.

Pattern one: `output_key=` on the agent. When you construct an LlmAgent, pass `output_key="last_response"`. After every run, the model's final text reply is automatically stored under that key. Useful for caching, and for passing output between workflow agents — which we'll see in module five.

Pattern two: `tool_context.state[key] = value` inside a tool. The pattern you just saw. Works. Persists.

Pattern three: you fetch a session with `get_session()`, get back a session object with a `.state` dict, and you assign to it directly — `session.state["foo"] = "bar"`. This does **not** persist. The next time you call `get_session()` for the same triple, your assignment is gone. Nobody ever tells you this happens. You just wonder why state isn't sticking.

---

## Slide 12 — The rule

The rule, on one slide. Use `output_key=` on the agent. Use `tool_context.state[...]` inside a tool. Do not assign directly to a returned session's `.state` dict. The first two persist because they go through events. The third bypasses events — and events are how ADK persists state.

The notebook has a cell that demonstrates this pitfall explicitly. Run it; you'll see the direct-assignment values vanish on the next fetch.

---

## Slide 13 — Events and Artifacts header

Part two of the module. Events and artifacts. Quicker pass; the state material is the part that matters most in practice.

---

## Slide 14 — Events, immutable ledger

Every turn in a session produces events, and the session keeps them all. Walk `session.events` to audit what happened, replay a conversation, feed it into an evaluation suite.

The diagram shows the event history from the color demo. Four events. User input. Tool call. Tool response with a state delta recording the color write. Final text response with a state delta recording the `output_key` save.

State is a projection of this event stream. When you fetch a session, ADK replays the events in order, applies the state deltas, and hands you the final state. That's event sourcing. It's the reason swapping in-memory sessions for database sessions is seamless in module eight — the data model is the same; only the storage changes.

---

## Slide 15 — Artifacts

Quick word on the fourth concept. Artifacts are for binary data — images, audio, PDFs, any large blob — that you want to associate with a session but don't want to serialize into events.

Analogy: Git LFS for agents. The pointer lives in the event stream; the payload lives in a separate store.

Three artifact services mirror the session services — in-memory, Google Cloud Storage, and a base class you can implement for S3, Azure, MinIO, whatever. You won't need artifacts for the text agents in part one of this course. Module thirteen — the Live API voice agent — is the first module where they earn their keep.

---

## Slide 16 — Interlude header

Two-minute interlude. From the Agentic Design Patterns publication. Chapter two, persistent context. The pattern has a name: Skeptical Memory.

---

## Slide 17 — Staleness is real

The demo looks clean because the state hasn't had time to go stale. In production, this is not how it works.

A user's favorite color from three months ago is probably still current. Their current project? Probably not — they might have moved on without telling the agent. Tickets the agent "remembered" being open yesterday might all be closed. A server IP cached by an MCP tool might have been reassigned.

Stored memory is a hint. Not a fact. If you treat it as a fact, the day it becomes stale is the day your agent does something embarrassing.

---

## Slide 18 — Three guidelines

Three guidelines from the publication.

First: prefer retrieval over recall for high-stakes decisions. Before the agent sends an email, charges a card, or deploys code, it should call a read-only tool to re-verify — not trust its own stored state. The cost of an extra tool call is cheap compared to the cost of acting on stale information.

Second: scope your state aggressively. Temp for scratchpads, unprefixed for per-session, user for things that only change when the user explicitly changes them, app for genuinely immutable configuration. The more narrowly scoped the state, the less staleness it can cause.

Third: when you write to user-scope or app-scope state, log a reason. Months from now, you're debugging an agent acting on six-month-old memory. A one-line "why did this get stored" note saves hours of investigation.

The pattern has a name. Skeptical Memory. Treat your own stored context as unverified until proven otherwise.

---

## Slide 19 — What to carry forward

What to carry forward. Four things.

State, events, artifacts, scope prefixes. The four mechanical tools ADK gives you for making an agent remember things.

And one principle, from the Skeptical Memory pattern: stored state is a hint, not a fact.

---

## Slide 20 — Next

Module four. The one-line model swap. We've been using `LiteLlm` as a black box for three modules. Now we open it up. Claude, GPT, Qwen, a locally-hosted Ollama model — all from the same agent code, all with one line of configuration different. And the specific gotcha around the `ollama_chat` prefix that causes infinite tool-call loops if you get it wrong. See you there.
