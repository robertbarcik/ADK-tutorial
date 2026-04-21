# M08 — Speaker notes

---

## Slide 1 — Title

Welcome to module eight — memory. Every demo for the last seven modules has used `InMemorySessionService`, which is the dict-backed service that loses everything on process restart. That's perfect for tutorials, but useless for production. In this module, we fix that with two different mechanisms — a persistent session service backed by SQLite or Postgres, plus a separate memory service that lets the agent explicitly recall facts from past conversations weeks later. And then we'll return to the Skeptical Memory pattern, because at long time horizons, memory gets stale, and acting on stale memory is expensive.

---

## Slide 2 — Seven modules, one problem

Let me name the problem with what we've been doing. `InMemorySessionService` loses everything on process restart, which means if you restart your Python process, every session your users had is gone. That's fine for a tutorial. For a real product, though, it means the agent forgets everyone every single time you deploy.

---

## Slide 3 — Two time scales

Agents need to remember at two different time scales, and the boundary between them is really the most important thing to get right in this module.

The first scale is within one conversation — the stuff we covered with session state in module three. The agent tracks current-turn context, and `user:`-prefixed state carries across sessions for the same user within one session service.

The second scale is across weeks, across unrelated sessions — and that's the job of `MemoryService` plus the `load_memory` tool. The agent explicitly searches an archive of past conversations. So this is "what did we talk about last Tuesday" territory.

The rule of thumb is this. Session state handles today's conversation. MemoryService handles history.

---

## Slide 4 — Persistence header

On to part one — persistence, using `DatabaseSessionService`.

---

## Slide 5 — The swap

Here's the actual change, and it's really one line. Instead of `InMemorySessionService()`, you write `DatabaseSessionService(db_url=...)`. The rest of your code — so agents, runners, tools, callbacks — does not change at all.

For demos, use SQLite — `sqlite+aiosqlite:///app.db`. For production, Postgres — `postgresql+asyncpg://...`. Same interface, just pick your backend.

---

## Slide 6 — The async-URL gotcha

There's a gotcha worth flagging up front. ADK's DatabaseSessionService uses SQLAlchemy's async engine, which means you do NOT want to use `sqlite://` — the plain scheme. It uses a sync driver, and it fails with an unhelpful error. Use `sqlite+aiosqlite://` explicitly instead.

You'll also need to install two packages — `aiosqlite` as the async driver, and `greenlet` as a transitive SQLAlchemy requirement. Both are lightweight, both are pip installs. And if you forget either one, the error message doesn't tell you what to do.

---

## Slide 7 — Live: write, restart, recall

Switch to the notebook — cells eleven through thirteen. We create a database session service pointing at a SQLite file, and write a user preference. Then we build a brand-new service instance — simulating a process restart — pointing at the same file. We create a fresh session for the same user. And the state is already populated, because `user:`-prefixed keys loaded from disk.

---

## Slide 8 — Three-step recap

Back on the slide. What you just saw was a three-step sequence. First, instance one wrote `user:preference = terse` to the SQLite file, and the file grew. Second, the simulated process restart — we built instance two, a fresh DatabaseSessionService pointing at the same DB path. And third, we created a new session for the same user, and the state was already populated from disk.

The reason this works, which we covered in module three, is that ADK persists state via events. Both `output_key=` and `tool_context.state[...]` produce state-delta events that the service writes to storage. Then, on `create_session`, the service reads past state from storage and hands it back ready to use.

---

## Slide 9 — Long-term memory header

On to part two — long-term memory, using `MemoryService` and the `load_memory` tool.

---

## Slide 10 — The shape

The shape of long-term memory is a four-step dance.

First, a conversation happens. The user tells the agent something — like a project they're working on, a preference, or a fact about themselves.

Second, you explicitly archive the session to memory with `await memory_service.add_session_to_memory(session)`. This is the deliberate step — ADK doesn't auto-archive. You decide when a session becomes part of the agent's searchable long-term history.

Third, in a future, unrelated session, the agent has a tool called `load_memory`. It's a built-in — just import it from `google.adk.tools` and add it to the agent's `tools=` list.

And fourth, when the user asks a question that might be answered from history, the agent calls `load_memory` with a search query. The memory service returns matching snippets, and the agent reads them and grounds its answer.

So this is really explicit retrieval, not ambient recall. The model decides when to search, and the tool returns what it finds.

---

## Slide 11 — Two memory services

ADK ships two memory services out of the box.

The first is `InMemoryMemoryService` — dict-backed, perfect for demos and tests, and it loses everything on restart. That's what the notebook uses.

The second is `VertexAiMemoryBankService` — managed, Google Cloud only. It's significantly more sophisticated — it extracts distilled facts from raw sessions, deduplicates, and consolidates over time. So it's the real-world path if you're committed to Vertex AI.

For self-hosted production on another stack, on the other hand, you'd implement `BaseMemoryService` against Postgres plus a vector extension, or against your existing search infrastructure. The interface is stable; the backing store is yours.

---

## Slide 12 — Live: long-term recall

Over in the notebook, cells eighteen through twenty-two. We have a multi-turn past conversation, where the user describes a Raspberry Pi project called RaspiKitchen — the hardware, what it's for. We archive that session to memory. Then we start a fresh session and ask "what project am I working on?" Watch the event stream — the agent calls `load_memory`, gets the snippets back, and produces an answer grounded in facts from a session it never participated in directly.

---

## Slide 13 — Event stream

Back on the slide. What you just watched was a three-beat sequence. The agent called `load_memory` with the search query. The tool returned a `MemoryEntry` containing text from the past conversation. And the agent read that and produced a grounded answer — RaspiKitchen, Pi 5, 8GB RAM, ESP32 microphone array.

The important thing is that those facts are NOT in the current conversation's context window. The current session just started. The past session is entirely separate. The agent retrieved them deliberately, via `load_memory`.

---

## Slide 14 — Interlude header

A short interlude — Skeptical Memory, now with teeth. Module three introduced the pattern briefly, but it really deserves more weight at long time horizons.

---

## Slide 15 — Staleness at long horizons

Let me walk through the staleness problem in its full form. Three months ago, the user told the agent they work at Acme Corp. The memory is stored. Today, the agent searches memory for "employer," finds Acme, and uses it to ground a reply — "As an Acme employee, you..."

Except the user might have changed jobs. The memory is accurate as of the day it was stored. It is not accurate as of today. So the agent, acting confidently on a three-month-old fact, is confidently wrong.

At long time horizons — weeks, months — staleness is really the default, not the exception. Most of what was true when written is still true, but some critical percentage isn't. And your agent needs to account for both.

---

## Slide 16 — Three defensive patterns

There are three defensive patterns worth knowing, all from the Agentic Design Patterns publication.

First, retrieve-and-verify for high-stakes actions. Before the agent sends an email, makes a purchase, or does anything irreversible, the next step after `load_memory` should be a tool call that re-verifies the retrieved fact. So something like "Let me confirm — you're still at Acme, right?" before acting, not after the fact fails.

Second, stamp memories with recency metadata. Store the date alongside every `user:` or `app:` level write, and surface the age of the memory to the model when it retrieves. The model will naturally distrust a three-month-old fact more than a fresh one — but only if it knows the age.

And third, decay or consolidate aggressively. Memory fills up. Let old entries age out — so delete them after N days, or consolidate multiple entries into a single summary. Memory Bank does this automatically. For `InMemoryMemoryService`, on the other hand, you'll implement the policy yourself.

---

## Slide 17 — The framing

If you remember one thing from this interlude, remember this — long-term memory is a journal, not a cache. Every retrieved memory is a claim from when it was written, not a fact that's true now. Treat it accordingly.

---

## Slide 18 — Next

Up next is module nine — evaluation. The first eight modules have really been "does the agent work?", answered by eyeballing the event stream. Module nine introduces ADK's evaluation framework — so `AgentEvaluator`, `EvalSet`, trajectory metrics that check whether the agent called the right tools in the right order, and the ROUGE-1 response-match metric with honest warnings about why it's weak for real work. Plus the adk eval CLI loop — chat, save evalset, tweak prompt, rerun. See you there.
