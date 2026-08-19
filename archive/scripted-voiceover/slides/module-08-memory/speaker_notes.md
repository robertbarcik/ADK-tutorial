# M08 — Speaker notes

---

## Slide 1 — Title

Memory. That's what this module is about, and it comes in two flavors that we'll keep separate from each other throughout. There's persistence, which is what makes sessions survive a process restart. And there's long-term recall, which is what lets an agent search past conversations weeks or months later. We'll build both with one-line additions to what you already have, and then close with the Skeptical Memory pattern again, because at long time horizons, memory gets stale, and acting on stale memory is expensive.

---

## Slide 2 — The persistence problem

The persistence problem is on the slide. `InMemorySessionService` loses everything on process restart, which means if you restart your Python process, every session your users had is gone. That's fine for a tutorial. For a real product, though, it means the agent forgets everyone every single time you deploy.

---

## Slide 3 — Two different time scales

Agents need to remember at two different time scales, and the boundary between them is really the most important thing to get right in this module.

The first scale is within one conversation. This is the stuff we covered with session state earlier in the course. The agent tracks current-turn context, and `user:`-prefixed state carries across sessions for the same user within one session service.

The second scale is across weeks, across unrelated sessions. That's the job of `MemoryService` plus the `load_memory` tool. The agent explicitly searches an archive of past conversations. This is "what did we talk about last Tuesday" territory.

The rule of thumb is this. Session state handles today's conversation. MemoryService handles history.

---

## Slide 4 — Part 1: DatabaseSessionService

Let's start with part one of the module: persistence, using `DatabaseSessionService`. The goal here is simple. We want sessions to survive a process restart, so when you redeploy your service, the conversations users were having don't just vanish. The next few slides walk through the one-line swap that gets you there.

---

## Slide 5 — The swap

On the slide we have the one-line swap, side by side with the in-memory version we've been using. Instead of `InMemorySessionService()`, you write `DatabaseSessionService(db_url=...)`. The rest of your code stays exactly the same: same agents, same runners, same tools, same callbacks.

For demos, use SQLite, with the URL `sqlite+aiosqlite:///app.db`. For real production, you'd point at Postgres or MySQL through a connection string like `postgresql+asyncpg://...`. Same interface either way, just pick your backend.

---

## Slide 6 — The async-URL gotcha

There's a gotcha worth flagging up front. ADK's DatabaseSessionService uses SQLAlchemy's async engine, which means you do not want to use the plain `sqlite://` scheme. That one uses a sync driver and fails with an unhelpful error. Use `sqlite+aiosqlite://` explicitly instead.

You'll also need to install two packages: `aiosqlite` as the async driver, and `greenlet` as a transitive SQLAlchemy requirement. Both are lightweight, both are pip installs. And if you forget either one, the error message doesn't tell you what to do.

---

### Notebook break — Write, restart, recall

[Switch the screen to the notebook.]

Let me show this in action. The notebook is set up with two service instances that both point at the same SQLite file, but they're built one at a time so we can simulate a process restart in between. I'll create instance one first and write a `user:preference = "terse"` into the state. [Run the cell.] You can see the SQLite file grew on disk. Now I'll throw instance one away and build instance two from scratch, pointing at the same file. [Run the next cell.] Then I'll create a new session for the same user, without passing any initial state. [Run the last cell.] Watch what happens. The state already contains `user:preference = "terse"`. Instance two loaded it from disk, exactly as if instance one had never gone away.

[Switch back to the slide deck.]

---

## Slide 7 — Three-step recap

On the slide is the three-step sequence laid out for reference: write, restart, recall. The reason it works is event sourcing, which we touched on earlier in the course. Both `output_key=` and `tool_context.state[...]` produce state-delta events that the service writes to storage. Then, on `create_session`, the service reads past state from storage and hands it back ready to use. The agent code doesn't change; only the persistence does.

---

## Slide 8 — Part 2: MemoryService and load_memory

Now to part two of the module: long-term memory, with `MemoryService` and the `load_memory` tool. This is what lets your agent search past conversations weeks or months later, even when nothing about the current conversation refers to those past sessions. Persistence keeps the session alive; long-term memory makes the agent able to remember things across totally unrelated sessions.

---

## Slide 9 — The shape

Long-term memory in ADK follows four steps. Let me walk through them.

First, a conversation happens. The user tells the agent something, like a project they're working on, a preference, or a fact about themselves.

Second, you explicitly archive the session to memory with `await memory_service.add_session_to_memory(session)`. This is the deliberate step. ADK doesn't auto-archive; you decide when a session becomes part of the agent's searchable long-term history.

Third, in a future, unrelated session, the agent has a tool called `load_memory`. It's a built-in, just import it from `google.adk.tools` and add it to the agent's `tools=` list.

And fourth, when the user asks a question that might be answered from history, the agent calls `load_memory` with a search query. The memory service returns matching snippets, and the agent reads them and grounds its answer.

So this is really explicit retrieval, not ambient recall. The model decides when to search, and the tool returns what it finds.

---

## Slide 10 — Two memory services

ADK ships two memory services out of the box.

The first is `InMemoryMemoryService`. It's dict-backed, perfect for demos and tests, and it loses everything on restart. That's the one the notebook uses.

The second is `VertexAiMemoryBankService`, which is managed and Google Cloud only. It's significantly more sophisticated. It extracts distilled facts from raw sessions, deduplicates them, and consolidates over time. That's the real-world path if you're committed to Vertex AI.

For self-hosted production on another stack, you'd implement `BaseMemoryService` against Postgres plus a vector extension, or against your existing search infrastructure. The interface is stable; the backing store is yours.

---

### Notebook break — Long-term recall in action

[Switch the screen to the notebook.]

Time to see long-term recall in action. The notebook walks through a four-step demo. First, we have a multi-turn past conversation, where the user describes a Raspberry Pi project called RaspiKitchen, including the hardware and what it's for. [Run the cell.] That session ends. Then we explicitly archive it to memory with `add_session_to_memory`. [Run the next cell.] Now we open a fresh session, with a brand-new session ID, and ask: "what project am I working on?" [Run the last cell.] Watch the event stream. The agent calls `load_memory` with a search query, gets snippets back from the past conversation, and produces an answer grounded in facts from a session it never directly participated in.

[Switch back to the slide deck.]

---

## Slide 11 — The event stream

Here's the same sequence captured as a static reference. Three beats: the agent called `load_memory` with the search query, the tool returned a `MemoryEntry` with text from the past conversation, and the agent produced a grounded answer about RaspiKitchen, the Pi 5, 8GB RAM, and the ESP32 microphone array.

The important thing to internalize is that those facts are NOT in the current conversation's context window. The current session just started. The past session is entirely separate. The agent retrieved them deliberately, via `load_memory`.

---

## Slide 12 — Skeptical Memory, revisited

Time for a short interlude on the Skeptical Memory pattern. We met it briefly earlier in the course. Now that we have memory spanning weeks or months, it's worth going into properly.

---

## Slide 13 — Memory staleness at long horizons

Let me walk through the staleness problem in its full form. Three months ago, the user told the agent they work at Anthropic. The memory is stored. Today, the agent searches memory for "employer," finds Anthropic, and uses it to ground a reply: "As an Anthropic employee, you..."

Except the user might have changed jobs since then. The memory is accurate as of the day it was stored. It is not accurate as of today. So the agent, acting confidently on a three-month-old fact, is confidently wrong.

At long time horizons, whether weeks or months, staleness is really the default, not the exception. Most of what was true when written is still true, but some critical percentage isn't. And your agent needs to account for both possibilities.

---

## Slide 14 — Three defensive patterns

There are three defensive patterns worth knowing when you're working with stale long-term memory.

The first pattern is retrieve-and-verify, especially for high-stakes actions. Before the agent sends an email, makes a purchase, or does anything irreversible, the next step after `load_memory` should be a tool call that re-verifies the retrieved fact. So you'd code something like "Let me confirm: you're still at Anthropic, right?" before acting, not after the action fails.

The second pattern is to stamp memories with recency metadata. What that means in practice is that you store the date alongside every `user:` or `app:` level write, and you surface the age of the memory to the model when it retrieves. With the age visible, the model will naturally distrust a three-month-old fact more than a fresh one. Without it, the model has no way to tell the difference.

And the third pattern is to decay or consolidate aggressively, because memory fills up over time. You can let old entries age out, delete them after some number of days, or consolidate multiple entries into a single summary. Memory Bank does this automatically. For `InMemoryMemoryService`, you'll implement the policy yourself.

---

## Slide 15 — The framing

The framing to carry forward from this interlude is on the slide. Long-term memory is a journal, not a cache. Every retrieved memory is a claim from the day it was written, not a fact that's automatically true now. Treat it accordingly: as a hint to verify, not as ground truth.

---

## Slide 16 — Up next

Up next, evaluation. So far in the course we've been answering the question "does the agent work?" by eyeballing the event stream. The next module introduces ADK's evaluation framework. We'll meet `AgentEvaluator` and `EvalSet`, trajectory metrics that check whether the agent called the right tools in the right order, and the ROUGE-1 response-match metric, along with honest warnings about why ROUGE is weak for real work. Plus the `adk eval` CLI loop: chat, save evalset, tweak prompt, rerun. See you there.
