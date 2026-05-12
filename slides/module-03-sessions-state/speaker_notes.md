# M03 — Speaker notes

---

## Slide 1 — Title

Welcome to module three: sessions, state, events, and artifacts. Most agent failures in production aren't about reasoning. They're about memory. The agent forgets who you are between sessions, forgets what you told it five minutes ago, or worse, remembers something that's no longer true. This module is about how memory actually works in ADK and how to design it well. By the end you'll know how to make an agent remember a user across separate conversations, why a five-character prefix decides whether memory lasts a turn or forever, and the three patterns for writing state, two of which work and one of which silently fails. Let's get into it.

---

## Slide 2 — Stateless vs stateful

The framing for this whole module is simple. A stateless agent is just a party trick. Each turn starts from zero, meaning there's no thread between conversations. Whatever you told the agent yesterday is gone. Whatever it figured out in the last session is gone. A stateful agent, on the other hand, is infrastructure. It knows who its users are, what they've asked before, and what decisions it's already made. That's the difference between a demo and a product.

---

## Slide 3 — A session is two things

Let me unpack what actually lives inside a session. A session is identified by three strings: app name, user ID, and session ID. That triple is the primary key for every session in every session store, regardless of backend.

A session itself holds two things. First, a list of events. That's the full ordered history of every message, every tool call, every tool response, and every state mutation. You can't append to it from your code; ADK does that for you. From your side, it's read-only.

And second, a state dict. This is mutable key-value storage for whatever you want the agent to carry between turns. That's really where the action is.

---

## Slide 4 — Three session services

ADK ships three session services. The first is in-memory, which backs everything by a Python dict. It loses everything on process restart, so it's perfect for tests and notebooks, and it's what we'll use through most of the course. The second is database-backed, using SQLAlchemy, which works against Postgres, MySQL, or SQLite. That's the production default. The third is Vertex-AI-backed, which you'd only reach for if you're on Google Cloud and committed to it.

The interface is the same across all three. Later in the course, when persistent memory becomes the focus of an entire module, we'll swap the in-memory service for the database one, and the agent code doesn't change. That's really the point of the abstraction.

---

## Slide 5 — State with scope prefixes

Now on to the important part: state with scope prefixes. This is the most useful under-documented feature in ADK, and it's the one you'll use every single day.

---

## Slide 6 — Four scope tiers

The state dict is a regular Python dict, but the prefix on the key decides the lifetime of the value. There are four tiers.

First, unprefixed keys. These live in this session only. When the session is deleted, they're gone.

Second, the `user:` prefix, pronounced "user colon", which persists across all sessions for this user. So if Alice has session one and session two, anything she writes to `user:favorite_color` in session one is visible in session two.

Third, the `app:` prefix, which is global across the application. Every user sees the same `app:` values, which is why you want to reserve this for genuinely application-wide things.

And finally, the `temp:` prefix, which is per-invocation only. The value lives for this one run and gets thrown away when the run ends. Useful for scratch work that a tool needs to carry across steps within a single call.

So four rings of scope. You pick the ring by choosing the prefix.

---

## Slide 7 — Mental model: four rings

What you see on this slide is the visual version of those four tiers. App state is the outermost ring, visible to everyone. User state is inside that, scoped per-user. Session state is inside that again, scoped per-session for one user. And temp state is at the center, gone the moment the run ends.

The rule of thumb is to pick the right ring when you write. A favorite color belongs in `user:`. It shouldn't leak to other users, but it should survive the session. A system prompt template belongs in `app:`. Every user uses the same one. A current turn's scratch computation belongs in `temp:`. Nobody else needs to see it, ever.

---

## Slide 8 — Writing state from a tool

Here on the slide we have a function called `remember_favorite_color`. It takes a color as a string and writes it into the agent's state so the agent can recall it later. The actual recording happens on this line: `tool_context.state["user:favorite_color"] = color`. That single assignment is what makes the value persist.

Let me unpack how it works. The tool function takes an extra parameter, `tool_context: ToolContext`. You don't pass this in yourself when calling the function; ADK injects the running context automatically whenever the tool is invoked. From that context, `tool_context.state` behaves like a regular Python dictionary. But anything you assign to it is recorded as an event behind the scenes, and that event is what the session service persists.

Two things to notice in this code. First, the parameter has to be named exactly `tool_context`, with the underscore. ADK looks for that specific name. Not `context`, not `ctx`. Second, the `user:` prefix on the key is what makes the value survive beyond this session. Drop the prefix, and the value disappears when the session is deleted.

---

### Notebook break — Cross-session memory in action

[Switch the screen to the notebook.]

Let me show you this actually running. The color agent is already set up here, with the `remember_favorite_color` and `recall_favorite_color` tools we just looked at on the slide. I'll start with session one, where I tell the agent that my favorite color is teal. [Run the session-one cell.] Look at the event stream that comes back. You can see the tool call to `remember_favorite_color` with `color='teal'`, and then a state delta recording the write to `user:favorite_color`. The session ends there.

Now I'll start session two. Same user, but a brand-new session ID, and no initial state passed in. I just ask: "what's my favorite color?" [Run the session-two cell.] Watch what happens. The state isn't empty. ADK loaded the session, saw that this user already has a `user:`-prefixed key, and carried `favorite_color = 'teal'` into the new session automatically. The agent calls `recall_favorite_color`, reads the value, and answers "teal."

[Switch back to the slide deck.]

---

## Slide 9 — The wow moment

You just saw it run. On the slide is the same thing as a diagram you can keep in your head: session one writes, session two reads it back, with nothing in between but the `user:` prefix doing the work.

Cross-session memory in five characters. No database setup, no vector store, no embedding pipeline. Just a prefix convention on a dict key.

---

## Slide 10 — Three ways to write state

There are three patterns for writing state. Two of them work. One of them doesn't, and unfortunately it's the one people reach for first.

Pattern one is `output_key=` on the agent. When you construct an LlmAgent, you pass `output_key="last_response"`. After every run, the model's final text reply is automatically stored under that key. Useful for caching, and also for passing output between workflow agents, which we'll see in a later module.

Pattern two is `tool_context.state[key] = value` inside a tool. That's the pattern you just saw on the previous slides. It works, and it persists.

Pattern three is where people get caught. You fetch a session with `get_session()`, get back a session object with a `.state` dict, and assign to it directly: `session.state["foo"] = "bar"`. This does not persist. The next time you call `get_session()` for the same triple, your assignment is gone. Nobody ever tells you this happens. You just sit there wondering why state isn't sticking.

---

## Slide 11 — The rule

So the rule, on one slide. Use `output_key=` on the agent. Use `tool_context.state[...]` inside a tool. And do not assign directly to a returned session's `.state` dict. The first two persist because they go through events. The third bypasses events, and events are how ADK persists state.

The notebook walkthrough that comes later has a cell that demonstrates this pitfall explicitly. Run it, and you'll see the direct-assignment values vanish on the next fetch.

---

## Slide 12 — Events and Artifacts

Part two of the module: events and artifacts. This is a quicker pass, because the state material is really the part that matters most in day-to-day practice.

---

## Slide 13 — Events: the immutable ledger

Events are the immutable ledger of a session. Every turn produces events, and the session keeps them all. You can walk `session.events` to audit what happened, replay a conversation, or feed it into an evaluation suite.

The diagram on the slide shows the actual event history from the color demo. Four events in total. First, the user input. Second, the tool call. Third, the tool response with a state delta recording the color write. And finally, the final text response with a second state delta recording the `output_key` save.

State is really a projection of this event stream. When you fetch a session, ADK replays the events in order, applies the state deltas, and hands you the final state. That's event sourcing, and it's the reason you can swap in-memory sessions for database-backed sessions later in the course without your agent code noticing. The data model is the same; only the storage changes.

---

## Slide 14 — Artifacts: binary blobs outside events

A quick word on the fourth concept: artifacts. Artifacts are for binary data, things like images, audio, PDFs, or any large blob, that you want to associate with a session but don't want to serialize into events themselves.

The analogy here is Git LFS for agents. The pointer lives in the event stream, while the payload lives in a separate store.

Three artifact services mirror the session services. There's an in-memory one for tests, a Google Cloud Storage one for production, and a base class you can implement yourself for S3, Azure, MinIO, or whatever else you use. You won't really need artifacts for the text-only agents in Part 1 of this course. They earn their keep later, in the module on the Live voice API.

---

## Slide 15 — Skeptical Memory

Time for a quick interlude from the Agentic Design Patterns publication, chapter two on persistent context. The pattern has a name: Skeptical Memory.

---

## Slide 16 — Memory staleness is real

Staleness is the thing the demo doesn't show you. The demo looks clean because the state hasn't had time to go stale. In production, that is not how it works.

A user's favorite color from three months ago is probably still current. Their current project, on the other hand? Probably not. They might have moved on without telling the agent. Tickets the agent "remembered" being open yesterday might all be closed by now. A server IP cached by an MCP tool might have been reassigned.

So stored memory is a hint. Not a fact. If you treat it as a fact, the day it becomes stale is the day your agent does something embarrassing.

---

## Slide 17 — Three guidelines from the publication

Three guidelines come out of the publication.

First, prefer retrieval over recall for high-stakes decisions. Before the agent sends an email, charges a card, or deploys code, it should call a read-only tool to re-verify, not trust its own stored state. The cost of an extra tool call is cheap compared to the cost of acting on stale information.

Second, scope your state aggressively. `temp:` for scratchpads, unprefixed for per-session, `user:` for things that only change when the user explicitly changes them, and `app:` for genuinely immutable configuration. The more narrowly scoped the state, the less staleness it can cause.

Third, when you write to user-scope or app-scope state, log a reason. Months from now, you'll be debugging an agent acting on six-month-old memory, and a one-line "why did this get stored" note saves hours of investigation.

The pattern has a name. Skeptical Memory. Treat your own stored context as unverified until proven otherwise.

---

## Slide 18 — What to carry forward

So what should you carry forward from today? Four mechanical tools and one principle.

The four tools are State, Events, Artifacts, and Scope prefixes. Those are what ADK gives you for making an agent remember things.

And one principle from the Skeptical Memory pattern: stored state is a hint, not a fact.

---

## Slide 19 — Up next

In the notebook walkthrough that comes next, you'll see all of this in action. You'll create an agent that remembers a favorite color in session one, then watch it recall the color in a fresh session two. You'll also reproduce the silent-failure pitfall with direct `.state` assignment, so you can recognize it when it happens in your own code. Then, in the module after that, we open up `LiteLlm`. Claude, GPT, Qwen, or a locally-hosted Ollama model, all from the same agent code, all with just one line of configuration different. See you there.
