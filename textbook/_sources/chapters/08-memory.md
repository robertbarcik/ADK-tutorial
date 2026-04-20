# Memory

Seven modules so far, every demo used `InMemorySessionService`. It is perfect for tutorials and useless for production. The moment your Python process restarts, every session your users had is gone. An agent that forgets every user on every deploy is not a product.

This chapter fixes that in two parts. First, persistence — the one-line swap from `InMemorySessionService` to `DatabaseSessionService`, backed by SQLite or Postgres. Sessions survive restarts; the agent code doesn't change. Second, long-term memory — the `MemoryService` and `load_memory` tool, which handle the harder problem of recalling facts from sessions that aren't in the current conversation's context.

And a return to the **Skeptical Memory** pattern from Module 03, which deserves more weight here — because at long time horizons, staleness is the default, and retrieved memories are often wrong.

## Two time scales

Agents need to remember at two different time scales, and the boundary between them is the single most important distinction in this chapter.

| Time scale | Primitive | Use case |
|---|---|---|
| **Within one conversation** | Session state (M03) | Current-turn context; `user:`-prefixed values carry across sessions within one service instance |
| **Across weeks, across unrelated sessions** | **`MemoryService` + `load_memory`** | Retrieve facts from past conversations the agent has no session-level reason to know |

Session state handles "today's conversation." MemoryService handles "what did we discuss last Tuesday?"

## Part 1 — Persistence: `DatabaseSessionService`

The swap is one line. Instead of `InMemorySessionService()`, use `DatabaseSessionService(db_url=...)`.

```python
# Demo backing (M01-M07)
session_service = InMemorySessionService()

# SQLite-backed persistence
session_service = DatabaseSessionService(
    db_url="sqlite+aiosqlite:///app.db"
)

# Postgres-backed production
session_service = DatabaseSessionService(
    db_url="postgresql+asyncpg://user:pass@host/db"
)
```

Everything else is identical. Same `Runner`, same agents, same event stream, same state-writing patterns (`output_key=` and `tool_context.state`). The only change is where ADK's state persistence goes.

### The async-URL gotcha

ADK's `DatabaseSessionService` uses SQLAlchemy's **async engine**. The plain `sqlite://` URL scheme fails because it resolves to a sync driver. You must use `sqlite+aiosqlite://` explicitly, and install the `aiosqlite` package (plus `greenlet`, a transitive SQLAlchemy async requirement).

```bash
pip install aiosqlite greenlet
```

For Postgres: `postgresql+asyncpg://` (install `asyncpg`). For MySQL: `mysql+aiomysql://` (install `aiomysql`).

The error message when you pick the wrong driver is SQLAlchemy's `"The asyncio extension requires an async driver to be used"`. If you see that, the fix is the driver scheme, not ADK.

### The demo — write, restart, recall

The pattern:

1. **Instance 1** of `DatabaseSessionService` creates a session for `alice`, handles a conversation, writes `user:preference = "terse"` via a tool. The state-delta goes through ADK's event path and lands in the SQLite file.
2. **Simulated process restart.** We discard the first instance and build a brand-new `DatabaseSessionService` against the same file path.
3. **Instance 2** creates a fresh session (different session ID) for `alice`. The session's initial state *already contains* `user:preference: "terse"` — loaded from disk by the service.

The reason this works is the same mechanism from Module 03 and Module 07: ADK persists state via events. Both `output_key=` (on the agent) and `tool_context.state[key] = value` (inside a tool) generate state-delta events. The session service writes those deltas to its backing store. On session create/load, the service applies the persisted deltas to produce the session's state dict.

Direct assignment to a returned session's `.state` dict — the anti-pattern from Module 03 — still silently fails with the database service, same as with the in-memory one. Use the two persisted patterns.

## Part 2 — Long-term memory: `MemoryService` and `load_memory`

Persistence gets you "the user's preferences survive restarts." It does not get you "remember what the user mentioned three sessions ago about their project." That's what `MemoryService` is for.

The shape is explicit, in four steps:

1. **During a conversation, things happen.** User mentions a project. Agent logs some context. Tool calls generate outputs.
2. **You archive the session to memory.** `await memory_service.add_session_to_memory(session)`. This is deliberate — ADK does not auto-archive.
3. **In a fresh, unrelated session later, the agent has `load_memory` in its tools list.** A built-in tool that takes a query string and searches the memory store.
4. **The agent calls `load_memory(query=...)`** when it thinks past context would help. The tool returns matching `MemoryEntry` snippets. The agent reads them and grounds its answer.

Two memory services ship:

- **`InMemoryMemoryService`** — dict-backed, for demos and tests.
- **`VertexAiMemoryBankService`** — managed, Google-Cloud-only. Much more sophisticated — it uses an LLM to extract *distilled facts* from raw sessions, deduplicates, consolidates over time. Covered briefly in Module 10.

For self-hosted production, you'd implement `BaseMemoryService` against Postgres with pgvector or against your existing search infrastructure. The interface is stable; only the backing changes.

### The demo — archive, recall

```python
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory

memory_svc = InMemoryMemoryService()

memory_agent = LlmAgent(
    name="memory_agent",
    model=LiteLlm(model=MODEL_STRING),
    instruction=(
        "When the user asks about something that might have come up in a "
        "past conversation, call load_memory with a search query. "
        "Base your answer on what it returns. If nothing relevant is found, "
        "say so — do not invent facts."
    ),
    tools=[load_memory],
)
```

The notebook runs a past conversation, archives it, then opens a fresh session:

```
USER (new session): What project am I working on, and what hardware?

[tool_call] load_memory({'query': 'what project and hardware'})
[tool_resp] memories=[MemoryEntry(content="I'm working on RaspiKitchen..."),
                     MemoryEntry(content="Pi 5 with 8GB, ESP32 microphone"),
                     ...]
[FINAL]     RaspiKitchen — a Raspberry Pi 5 voice-controlled recipe helper,
           running on 8GB of RAM with an ESP32 microphone array.
```

The facts came from a session that isn't in the current conversation's context. The agent retrieved them deliberately via `load_memory`, then grounded its answer in what it retrieved. **`load_memory` is explicit retrieval, not ambient recall** — the model decides when to search, the tool returns what it finds.

The "do not invent facts" clause in the instruction matters. Without it, some models will pattern-match an answer even when `load_memory` returns nothing useful. With it, the agent honestly says "I don't have that context" — which is almost always the right behavior.

## Interlude revisited — Skeptical Memory at long time horizons

Module 03 introduced Skeptical Memory briefly, with the one-line summary: *stored state is a hint, not a fact.* At long time horizons, the pattern pays off in spades.

Three months ago, the user told the agent they work at Acme Corp. The memory is stored. Today, when the agent searches memory for "employer," it comes back. The agent uses it to ground a reply: *"As an Acme employee, you..."*

The problem: **the user might have changed jobs.** The memory is accurate as of the day it was stored. It is not accurate as of today. The agent, acting confidently on a three-month-old fact, is confidently wrong.

At long time horizons — weeks, months — staleness is the default, not the exception. Most of what was true when written is still true. Some critical percentage isn't. Your agent needs to account for both.

### Three defensive patterns, with teeth this time

**1. Retrieve-and-verify for high-stakes actions.** Before the agent sends an email, makes a purchase, deploys code, or does anything with irreversible consequences, the next step after `load_memory` should be a tool call that re-verifies the fact the memory produced. *"I'm about to send an email to your Acme address — let me confirm you're still there before I do."* The cost of one extra verification call is trivial compared to the cost of acting on a stale fact.

**2. Stamp memories with recency metadata.** The publication's concrete recommendation: store the date alongside every `user:` or `app:`-scoped write. When the memory is retrieved, the model sees both the fact and when it was recorded. Models naturally distrust a fact stamped "November 2025" more than one stamped "yesterday" — if they see the stamp.

Concretely, you update your note-writing tool to also write a timestamp:

```python
def note_preference(preference: str, tool_context: ToolContext) -> dict:
    from datetime import datetime
    tool_context.state["user:preference"] = preference
    tool_context.state["user:preference_recorded_on"] = datetime.now().isoformat()
    return {"saved": preference}
```

And surface the timestamp to the model in the instruction: `"The user's preference was recorded on {user:preference_recorded_on?}."`

**3. Decay or consolidate aggressively.** Memory fills up. Let old entries age out — either delete them after N days or compress multiple entries into a single summary. Memory Bank does this automatically: it runs a periodic consolidation that extracts distilled facts, merges redundant entries, deletes stale ones. For `InMemoryMemoryService` or a custom implementation, you write the policy yourself.

### The framing

The single most useful framing from the Agentic Design Patterns book: **long-term memory is not a cache. It's a journal.**

A cache is "I already computed this; reuse it." A journal is "this was true when I wrote it; it may or may not be true now." Treat every retrieved memory as a journal entry, not a cache hit. That shift alone prevents most of the confident-but-wrong failures agents make with long-term memory.

## What to carry forward

- **`DatabaseSessionService` is a one-line swap** from `InMemorySessionService`. URL must be async: `sqlite+aiosqlite:///app.db`, `postgresql+asyncpg://...`. Install `aiosqlite` + `greenlet` for SQLite.
- **`MemoryService` + `load_memory`** is the long-term memory path. Archive is explicit (`add_session_to_memory`). Retrieval is explicit (the agent calls `load_memory`).
- **Two services ship**: `InMemoryMemoryService` (demos), `VertexAiMemoryBankService` (managed, Vertex-only).
- **`load_memory` is explicit retrieval**, not ambient recall. The model decides when to search.
- **Skeptical Memory with teeth**: retrieved facts are journal entries from when they were written. Retrieve-and-verify for high stakes; stamp with recency; decay aggressively.
- **The framing to carry**: long-term memory is a journal, not a cache.

Module 09 picks up **evaluation**. The first eight modules have been "does the agent work?" answered by eyeballing the event stream. Module 09 introduces ADK's evaluation framework — `AgentEvaluator`, `EvalSet`, trajectory metrics (did the agent call the right tools in the right order?), and the `adk eval` CLI loop (chat, save evalset, tweak prompt, rerun). Honest about ROUGE-1's limitations for production; gestures at LLM-as-judge as the upgrade path.
