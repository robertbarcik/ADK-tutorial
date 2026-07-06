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

## M13 — Live API text-mode session

**Status:** broken (server-side)
**Observed:** 2026-04-20 on Google AI Studio free tier

**What works:**
- Listing Live-capable models on the API key (the `supported_actions` filter returns the current Live models).
- Building `LlmAgent(model="gemini-3.1-flash-live-preview", ...)`, creating a `LiveRequestQueue`, calling `runner.run_live(...)` — the ADK-side plumbing is all correct.

**What breaks:**
- The `client.aio.live.connect(...)` call inside `runner.run_live(...)` returns a server-side **APIError 1011 "Internal error encountered"**. Happens on both `gemini-3.1-flash-live-preview` and the older `gemini-2.5-flash-native-audio-*` variants. Failure is at Google's side — the WebSocket handshake returns 1011 before any frame is exchanged.

**Reproduce:**
```
python - <<'PY'
import asyncio, os
from dotenv import load_dotenv; load_dotenv()
from google import genai
from google.genai import types

async def main():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    cfg = types.LiveConnectConfig(response_modalities=["TEXT"])
    async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=cfg) as session:
        await session.send_client_content(turns=[types.Content(role="user", parts=[types.Part(text="hi")])])
        async for r in session.receive():
            if r.text: print(r.text)
            break

asyncio.run(main())
PY
```
→ `google.genai.errors.APIError: 1011 None. Internal error encountered.`

**Student workaround:**
- The M13 notebook's Live cell catches the error and reports it clearly; the notebook continues without raising. Students read the material, see the code, understand the mechanics. The code is correct — the live endpoint is just unreliable on the free tier.
- For a verified working Live demo, try again in a few weeks (Live is preview-tier and actively being stabilized), or switch to a paid tier, or run against Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) which has different quota/backend behavior.
- For full audio-mode end-to-end (browser microphone → ADK → audio response), see the `adk-samples` voice-agent example at github.com/google/adk-samples — that sample bundles the browser client, WebSocket bridge, and audio playback that a notebook cannot.

**Fix-later notes:**
- Watch ai.google.dev/gemini-api/docs/live for the current stable Live model string; the preview models rotate.
- Separate issue if it becomes reproducible: check `GOOGLE_GENAI_USE_VERTEXAI=FALSE` is actually being respected on the request path.
- Long-term this will resolve as the Live API exits preview. The module's teaching of the API shape is durable.

---

## M08 — `DatabaseSessionService` + `sqlite+aiosqlite://` (fixed 2026-07-06)

**Status:** fixed in the notebook; upstream bug remains in `google-adk==1.28.0`
**Observed:** 2026-07-06, executing the notebook headless with pinned `requirements.txt` versions

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

