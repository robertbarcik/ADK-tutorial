# M03 — Speaker notes

---

## Slide 1 — Title

Welcome to module three — sessions, state, events, and artifacts. Module one gave you the four primitives, and module two gave you tools. This module goes deep on the third primitive — Session — and everything that lives inside it. So if module two was about what an agent can *do*, module three is about what an agent *remembers*. Get this right, and your agents become infrastructure. Get it wrong, and they're party tricks that forget everyone's name every Monday.

---

## Slide 2 — Stateless vs stateful

The framing for this module is simple. A stateless agent is really just a party trick — each turn starts from zero, which means it can't remember what you told it five minutes ago, let alone yesterday. A stateful agent, on the other hand, is infrastructure. It knows who its users are, what they've asked before, and what decisions it's already made. That's the difference between a demo and a product.

---

## Slide 3 — A session is two things

Let me unpack what actually lives inside a session. A session is identified by three strings — app name, user ID, and session ID. That triple is the primary key for every session in every session store, regardless of backend.

A session itself holds two things. First, a list of events — the full ordered history of every message, every tool call, every tool response, and every state mutation. You can't append to it from your code; ADK does that for you. So from your side, it's read-only.

And second, a state dict — mutable key-value storage for whatever you want the agent to carry between turns. That's really where the action is.

---

## Slide 4 — Three session services

ADK ships three session services. The first is in-memory, which backs everything by a Python dict — it loses on process restart, so it's perfect for tests and notebooks. The second is database-backed, using SQLAlchemy, which works against Postgres, MySQL, or SQLite — and it's the production default. The third is Vertex-AI-backed, which you'd only reach for if you're on Google Cloud and committed to it.

The interface is the same across all three. So when module eight promotes memory to the subject, we'll swap the in-memory service for the database one, and the agent code does not change. That's really the point of the abstraction.

---

## Slide 5 — State section header

Now on to the important part — state with scope prefixes. This is the most useful under-documented feature in ADK, and it's the one you'll use every single day.

---

## Slide 6 — Four scope tiers

The state dict is a regular Python dict, but the prefix on the key decides the lifetime of the value. There are four tiers.

First, unprefixed keys — these live in this session only. When the session is deleted, they're gone.

Second, the `user:` prefix — pronounced "user colon" — which persists across all sessions for this user. So if Alice has session one and session two, anything she writes to `user:favorite_color` in session one is visible in session two.

Third, the `app:` prefix, which is global across the application. Every user sees the same `app:` values, which is why you want to reserve this for genuinely application-wide things.

And finally, the `temp:` prefix, which is per-invocation only. The value lives for this one run and gets thrown away when the run ends. Useful for scratch work that a tool needs to carry across steps.

So four rings of scope. You pick the ring by choosing the prefix.

---

## Slide 7 — Mental model

What you see on this slide is the visual version of those four tiers. App state is the outermost ring — everyone sees it. User state is inside that, per-user. Session state is inside that again — per-session for one user. And temp state is at the center — gone the moment the run ends.

The rule of thumb is to pick the right ring when you write. A favorite color is `user:` — it shouldn't leak to other users, but it should survive the session. A system prompt template is `app:` — every user uses the same one. A current turn's scratch computation is `temp:` — nobody else needs to see it, ever.

---

## Slide 8 — Writing state from a tool

In code, writing state from a tool looks like this. The tool function takes an extra parameter — `tool_context: ToolContext`. ADK injects the running context automatically, so you don't pass it in yourself. From that context, `tool_context.state` behaves like a dict. Assignments to it are recorded as events, and then persisted by the session service.

Two things to notice in the code. First, the parameter is `tool_context` with an underscore — ADK looks for exactly that name, not `context` or `ctx`. Second, the `user:` prefix on the key is what makes the value survive beyond this session. Drop the prefix, and the value disappears when the session does.

---

## Slide 9 — Live: cross-session memory

Switch to the notebook, cells eleven through fifteen. We create an agent that can remember and recall a favorite color. In session one, we tell it teal. Then in session two — a fresh session, same user — we ask it what our color is. Watch the event stream.

---

## Slide 10 — The wow moment

Back on the slide. Let me walk through what just happened.

Session one: the user says "my favorite color is teal." The agent calls `remember_favorite_color` with `color='teal'`. The tool writes `user:favorite_color = 'teal'` into the state. Session ends.

Session two starts. We didn't pass any initial state. But the session's state *starts* with `user:favorite_color: 'teal'` already present — because the key was prefixed with `user:`, ADK carried it across when it loaded session two.

The user asks "what's my favorite color?" The agent calls `recall_favorite_color`, which reads `user:favorite_color`, and returns `"teal"`. The model then says "teal."

Cross-session memory. No database setup. No vector store. No custom embedding pipeline. Just a prefix on a dict key.

---

## Slide 11 — Three ways to write state

There are three patterns for writing state. Two of them work. One of them doesn't — and it's the one people reach for first.

Pattern one is `output_key=` on the agent. When you construct an LlmAgent, you pass `output_key="last_response"`. After every run, the model's final text reply is automatically stored under that key. Useful for caching, and also for passing output between workflow agents — which we'll see in module five.

Pattern two is `tool_context.state[key] = value` inside a tool. That's the pattern you just saw. It works, and it persists.

Pattern three is where people get caught. You fetch a session with `get_session()`, get back a session object with a `.state` dict, and assign to it directly — so `session.state["foo"] = "bar"`. This does **not** persist. The next time you call `get_session()` for the same triple, your assignment is gone. Nobody ever tells you this happens — you just wonder why state isn't sticking.

---

## Slide 12 — The rule

So the rule, on one slide. Use `output_key=` on the agent. Use `tool_context.state[...]` inside a tool. And do not assign directly to a returned session's `.state` dict. The first two persist because they go through events. The third bypasses events — and events are how ADK persists state.

The notebook has a cell that demonstrates this pitfall explicitly. Run it, and you'll see the direct-assignment values vanish on the next fetch.

---

## Slide 13 — Events and Artifacts header

Part two of the module — events and artifacts. This is a quicker pass, because the state material is really the part that matters most in practice.

---

## Slide 14 — Events, immutable ledger

Events are the immutable ledger. Every turn in a session produces events, and the session keeps them all. So you can walk `session.events` to audit what happened, replay a conversation, or feed it into an evaluation suite.

The diagram shows the event history from the color demo — four events in total. First, user input. Second, tool call. Third, tool response with a state delta recording the color write. And finally, the final text response with a state delta recording the `output_key` save.

State is really a projection of this event stream. When you fetch a session, ADK replays the events in order, applies the state deltas, and hands you the final state. That's event sourcing — and it's the reason swapping in-memory sessions for database sessions is seamless in module eight. The data model is the same; only the storage changes.

---

## Slide 15 — Artifacts

A quick word on the fourth concept — artifacts. Artifacts are for binary data — things like images, audio, PDFs, or any large blob — that you want to associate with a session but don't want to serialize into events.

The analogy here is Git LFS for agents. The pointer lives in the event stream, while the payload lives in a separate store.

Three artifact services mirror the session services — in-memory, Google Cloud Storage, and a base class you can implement for S3, Azure, MinIO, or whatever else you use. You won't really need artifacts for the text agents in part one of this course. Module thirteen — the Live API voice agent — is the first module where they earn their keep.

---

## Slide 16 — Interlude header

Time for a quick two-minute interlude, from the Agentic Design Patterns publication, chapter two — persistent context. The pattern has a name — Skeptical Memory.

---

## Slide 17 — Staleness is real

Staleness is the thing the demo doesn't show you. The demo looks clean because the state hasn't had time to go stale. In production, that is not how it works.

A user's favorite color from three months ago is probably still current. Their current project, on the other hand? Probably not — they might have moved on without telling the agent. Tickets the agent "remembered" being open yesterday might all be closed by now. A server IP cached by an MCP tool might have been reassigned.

So stored memory is a hint. Not a fact. If you treat it as a fact, the day it becomes stale is the day your agent does something embarrassing.

---

## Slide 18 — Three guidelines

Three guidelines come out of the publication.

First, prefer retrieval over recall for high-stakes decisions. Before the agent sends an email, charges a card, or deploys code, it should call a read-only tool to re-verify — not trust its own stored state. The cost of an extra tool call is cheap compared to the cost of acting on stale information.

Second, scope your state aggressively. Temp for scratchpads, unprefixed for per-session, user for things that only change when the user explicitly changes them, and app for genuinely immutable configuration. The more narrowly scoped the state, the less staleness it can cause.

Third, when you write to user-scope or app-scope state, log a reason. Months from now, you'll be debugging an agent acting on six-month-old memory, and a one-line "why did this get stored" note saves hours of investigation.

The pattern has a name. Skeptical Memory. Treat your own stored context as unverified until proven otherwise.

---

## Slide 19 — What to carry forward

So what should you carry forward from today? Four things.

State, events, artifacts, and scope prefixes. Those are the four mechanical tools ADK gives you for making an agent remember things.

And one principle, from the Skeptical Memory pattern — stored state is a hint, not a fact.

---

## Slide 20 — Next

Up next in module four — the one-line model swap. We've been using `LiteLlm` as a black box for three modules. Now we open it up. Claude, GPT, Qwen, or a locally-hosted Ollama model — all from the same agent code, all with just one line of configuration different. And we'll cover the specific gotcha around the `ollama_chat` prefix that causes infinite tool-call loops if you get it wrong. See you there.
