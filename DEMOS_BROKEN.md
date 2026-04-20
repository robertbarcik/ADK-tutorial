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

