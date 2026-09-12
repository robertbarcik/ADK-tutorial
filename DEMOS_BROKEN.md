# Demos that need fixing

Running log of demos whose material shipped but whose code does not (yet) run end-to-end. Each entry is a scoped, reproducible bug with a hypothesis for the fix and a student-facing workaround.

Use this format for each entry:

```
## MNN — <short name>
**Status:** partial | broken | flaky
**What works:** <what the student will see>
**What breaks:** <specific error or failure mode>
**Reproduce:** <shell command or notebook cell reference>
**Student workaround:** <what to do in the meantime>
**Fix-later notes:** <hypothesis or link to upstream issue>
```

---

## M13 — Live API voice agent (module retired 2026-09-12)

The Live voice notebook was removed from the course: the Live API stayed preview-tier and its model names kept rotating, so the demo broke more often than it taught. The notebook and its textbook chapter are in git history (`notebooks/13_live_api_voice.ipynb`, last at commit 001847d). Module 13 is now the A2A side step.

---

## M08 — `DatabaseSessionService` + `sqlite+aiosqlite://` (fixed 2026-07-06; INVERTED by ADK 2.x on 2026-07-10)

**Status:** fixed in the notebook; upstream bug remains in `google-adk==1.28.0`
**Observed:** 2026-07-06, executing the notebook headless with pinned `requirements.txt` versions

**ADK 2.x update (2026-07-10):** the situation flips on the 2.x line. `DatabaseSessionService` in google-adk 2.4.0 builds its engine with SQLAlchemy's **async** `create_async_engine` — the plain sync `sqlite:///` URL is now *rejected* ("Failed to create database engine"), and `sqlite+aiosqlite:///` is *required* (verified with a create/get round trip). SQLAlchemy also moved behind the `[db]` extra. The notebook now installs `'google-adk[db]' aiosqlite greenlet` and uses the `sqlite+aiosqlite://` scheme again. The entry below documents the 1.x behavior for history:

**What broke:**
- `DatabaseSessionService(db_url="sqlite+aiosqlite:///...")` raised `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called` on the very first `create_session`/`get_session` call — reproduces even outside Jupyter/`nest_asyncio`, with a plain `asyncio.run(...)`.
- Root cause: `DatabaseSessionService.__init__` (in `google/adk/sessions/database_session_service.py`) builds its engine with SQLAlchemy's **synchronous** `create_engine(db_url)` and then calls sync methods (`inspect(...)`, `Base.metadata.create_all(...)`) directly on it. That's fine against a sync driver, but against the `aiosqlite` async driver those sync calls try to open a real connection without the `greenlet_spawn` context SQLAlchemy's async extension requires — so it always fails, unrelated to nbconvert/notebook headlessness.

**Fix applied:** switched `SQLITE_URL` to a plain sync `sqlite:///{DB_PATH}` (no `+aiosqlite`). `DatabaseSessionService` wraps its sync engine internally, so a sync SQLite URL works correctly with `google-adk==1.28.0`. Dropped the now-unneeded `aiosqlite`/`greenlet` extras from the notebook's `!pip install` cell. Same fix applies to the `postgresql+asyncpg://` line in the Key Takeaways cell, wasn't tested here (only SQLite is used in the demo).

**Reproduce (pre-fix):**
```python
import asyncio
from google.adk.sessions import DatabaseSessionService

async def main():
    svc = DatabaseSessionService(db_url="sqlite+aiosqlite:///:memory:")
    await svc.create_session(app_name="a", user_id="u")

asyncio.run(main())  # -> sqlalchemy.exc.MissingGreenlet
```

**Fix-later notes:** watch adk-python for a fix that either uses `create_async_engine` for async-driver URLs or documents that only sync URLs are supported. Re-test `sqlite+aiosqlite://` on the next `google-adk` bump (paired with `litellm` per the pinning rule above).

---

## M09 — `AgentEvaluator.evaluate(agent_module=...)` module path (fixed 2026-07-06)

**Status:** fixed in the notebook
**Observed:** 2026-07-06, executing the notebook headless

**What broke:**
- `AgentEvaluator.evaluate(agent_module="eval_demo_agent.agent", ...)` raised `ValueError: Module eval_demo_agent.agent does not have a member named 'agent'`.
- Root cause: `AgentEvaluator._get_agent_for_eval` (google-adk 1.28.0) does `importlib.import_module(module_name)` and then expects `hasattr(that_module, "agent")` to be true — i.e. `module_name` must be the **package** (`eval_demo_agent`), and the package's `__init__.py` must re-export the `agent` submodule (`from . import agent`) so it resolves `eval_demo_agent.agent.root_agent`. Passing `"eval_demo_agent.agent"` directly imports the leaf module, which has no further `.agent` attribute on it.

**Fix applied:** the temp `__init__.py` now contains `from . import agent`, and both `AgentEvaluator.evaluate(...)` calls pass `agent_module="eval_demo_agent"` (package name only, no `.agent` suffix).

**Fix-later notes:** this is a documentation/convention gap more than a bug — the pattern isn't obvious from the `AgentEvaluator.evaluate` signature. Re-check against future `google-adk` releases in case the resolution logic changes.

