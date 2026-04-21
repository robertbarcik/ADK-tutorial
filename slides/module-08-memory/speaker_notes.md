# M08 — Speaker notes

---

## Slide 1 — Title

Module eight. Memory. Every demo for the last seven modules has used `InMemorySessionService` — the dict-backed service that loses everything on process restart. Perfect for tutorials; useless for production. This module fixes that with two different mechanisms: a persistent session service backed by SQLite or Postgres, and a separate memory service that lets the agent explicitly recall facts from past conversations weeks later. Plus a return to the Skeptical Memory pattern — because at long time horizons, memory gets stale, and acting on stale memory is expensive.

---

## Slide 2 — Seven modules, one problem

The problem with what we've been doing. `InMemorySessionService` loses everything on process restart. Restart your Python process, every session your users had is gone. That's fine for a tutorial. For a product, it means the agent forgets everyone every time you deploy.

---

## Slide 3 — Two time scales

Agents need to remember at two different time scales, and the boundary between them is the most important thing to get right in this module.

Within one conversation — the stuff covered by session state in module three. The agent tracks current-turn context; `user:`-prefixed state carries across sessions for the same user within one session service.

Across weeks, across unrelated sessions — that's the job of `MemoryService` plus the `load_memory` tool. The agent explicitly searches an archive of past conversations. This is "what did we talk about last Tuesday" territory.

Session state handles today's conversation. MemoryService handles history.

---

## Slide 4 — Persistence header

Part one. Persistence. `DatabaseSessionService`.

---

## Slide 5 — The swap

Here's the actual change. One line. Instead of `InMemorySessionService()`, write `DatabaseSessionService(db_url=...)`. The rest of your code — agents, runners, tools, callbacks — does not change.

For demos, SQLite: `sqlite+aiosqlite:///app.db`. For production, Postgres: `postgresql+asyncpg://...`. Same interface; pick your backend.

---

## Slide 6 — The async-URL gotcha

A gotcha worth flagging up front. ADK's DatabaseSessionService uses SQLAlchemy's async engine. Do NOT use `sqlite://` — the plain scheme. It uses a sync driver and fails with an unhelpful error. Use `sqlite+aiosqlite://` explicitly.

Install two packages: `aiosqlite` as the async driver, and `greenlet` as a transitive SQLAlchemy requirement. Both are lightweight, both are pip installs. If you forget either, the error message doesn't tell you what to do.

---

## Slide 7 — Live: write, restart, recall

Switch to the notebook. Cells eleven through thirteen. We create a database session service pointing at a SQLite file, write a user preference. Then we build a brand-new service instance — simulating a process restart — pointing at the same file. Create a fresh session for the same user. The state is already populated because `user:`-prefixed keys loaded from disk.

---

## Slide 8 — Three-step recap

Back on the slide. Instance one wrote `user:preference = terse` to the SQLite file. The file grew. Simulated process restart: we built instance two, a fresh DatabaseSessionService pointing at the same DB path. Created a new session for the same user. The state was already populated from disk.

The reason this works, which we covered in module three: ADK persists state via events. Both `output_key=` and `tool_context.state[...]` produce state-delta events that the service writes to storage. On `create_session`, the service reads past state from storage and hands it back ready to use.

---

## Slide 9 — Long-term memory header

Part two. Long-term memory. `MemoryService` and the `load_memory` tool.

---

## Slide 10 — The shape

Four steps.

One: a conversation happens. The user tells the agent something — a project they're working on, a preference, a fact about themselves.

Two: you explicitly archive the session to memory. `await memory_service.add_session_to_memory(session)`. This is the deliberate step — ADK doesn't auto-archive. You decide when a session becomes part of the agent's searchable long-term history.

Three: in a future, unrelated session, the agent has a tool called `load_memory`. It's a built-in; import it from `google.adk.tools` and add it to the agent's `tools=` list.

Four: when the user asks a question that might be answered from history, the agent calls `load_memory` with a search query. The memory service returns matching snippets. The agent reads them and grounds its answer.

This is explicit retrieval, not ambient recall. The model decides when to search; the tool returns what it finds.

---

## Slide 11 — Two memory services

ADK ships two memory services.

`InMemoryMemoryService` — dict-backed. Perfect for demos and tests. Loses on restart. That's what the notebook uses.

`VertexAiMemoryBankService` — managed, Google Cloud only. Significantly more sophisticated — it extracts distilled facts from raw sessions, deduplicates, consolidates over time. It's the real-world path if you're committed to Vertex AI.

For self-hosted production on another stack, you'd implement `BaseMemoryService` against Postgres plus a vector extension, or against your existing search infrastructure. The interface is stable; the backing store is yours.

---

## Slide 12 — Live: long-term recall

Notebook cells eighteen through twenty-two. We have a multi-turn past conversation — user describes a Raspberry Pi project called RaspiKitchen, the hardware, what it's for. We archive that session to memory. Then we start a fresh session and ask "what project am I working on?" Watch the event stream — the agent calls `load_memory`, gets the snippets back, and produces an answer grounded in facts from a session it never participated in directly.

---

## Slide 13 — Event stream

Back on the slide. Here's what you just watched. The agent called `load_memory` with the search query. The tool returned a `MemoryEntry` containing text from the past conversation. The agent read that and produced a grounded answer — RaspiKitchen, Pi 5, 8GB RAM, ESP32 microphone array.

The important thing: those facts are NOT in the current conversation's context window. The current session just started. The past session is entirely separate. The agent retrieved them deliberately, via `load_memory`.

---

## Slide 14 — Interlude header

Short interlude. Skeptical Memory, now with teeth. Module three introduced the pattern briefly. It deserves more weight at long time horizons.

---

## Slide 15 — Staleness at long horizons

The staleness problem in its full form. Three months ago, the user told the agent they work at Acme Corp. The memory is stored. Today, the agent searches memory for "employer," finds Acme, uses it to ground a reply: "As an Acme employee, you..."

Except the user might have changed jobs. The memory is accurate as of the day it was stored. It is not accurate as of today. The agent, acting confidently on a three-month-old fact, is confidently wrong.

At long time horizons — weeks, months — staleness is the default, not the exception. Most of what was true when written is still true; some critical percentage isn't. Your agent needs to account for both.

---

## Slide 16 — Three defensive patterns

Three defensive patterns, from the Agentic Design Patterns publication.

One: retrieve-and-verify for high-stakes actions. Before the agent sends an email, makes a purchase, or does anything irreversible, the next step after `load_memory` should be a tool call that re-verifies the retrieved fact. "Let me confirm — you're still at Acme, right?" before acting, not after the fact fails.

Two: stamp memories with recency metadata. Store the date alongside every `user:` or `app:` level write. Surface the age of the memory to the model when it retrieves. The model will naturally distrust a three-month-old fact more than a fresh one — if it knows the age.

Three: decay or consolidate aggressively. Memory fills up. Let old entries age out — delete them after N days, or consolidate multiple entries into a single summary. Memory Bank does this automatically. For `InMemoryMemoryService`, you'll implement the policy yourself.

---

## Slide 17 — The framing

The single most useful framing from the book. Long-term memory is a journal, not a cache. Every retrieved memory is a claim from when it was written — not a fact that's true now. Treat it accordingly.

---

## Slide 18 — Next

Module nine. Evaluation. The first eight modules have been "does the agent work?" answered by eyeballing the event stream. Module nine introduces ADK's evaluation framework — `AgentEvaluator`, `EvalSet`, trajectory metrics that check whether the agent called the right tools in the right order, and the ROUGE-1 response-match metric with honest warnings about why it's weak for real work. The adk eval CLI loop: chat, save evalset, tweak prompt, rerun. See you there.
