# Live API voice agent

The third and most interesting of the three Gemini-only unlocks.

**The Live API lets Gemini exchange audio bidirectionally with the user in real time.** Voice in, voice out. Voice activity detection. User-interruption-aware. Sub-second latency on happy-path sessions. Nothing in the Claude, GPT, or open-weight ecosystem ships this cleanly as of April 2026. OpenAI's Realtime API is the closest alternative — different semantics, different pricing, different failure modes. Anthropic has no direct equivalent.

The production use cases are the obvious ones: voice assistants, live interpreter agents, real-time coaching tools, accessibility apps, voice-driven customer support. If voice-first conversational agents are your product, Gemini Live is where you build.

**Fair warning before we begin.** Live is the most fragile of the three Gemini unlocks. The API is preview-tier; model names change frequently; the happy-path session can fail with server-side errors that have nothing to do with your code. The course repo's `DEMOS_BROKEN.md` logs the specific current failure mode observed at recording time.

This chapter teaches the **mechanics** — the API shape, the queue-based interaction pattern, what's special about it — even when the demo can't fully run end-to-end in some environments. The concepts are more durable than this month's version-string.

## What Live does differently

Every module until now used `runner.run_async(new_message=...)` — a request/response cycle. You hand ADK a user message, ADK drives the agent, events stream back, the turn ends, you move on to the next turn.

Live is different. The agent holds **an open bidirectional WebSocket** to Gemini. You don't hand over a single message; you stream chunks of audio (or text) into a queue, and chunks of response audio (or text) stream back, in parallel, for as long as the session is open. There are no "turns" in the traditional sense — just two streams flowing in opposite directions, with turn boundaries inferred from silence.

Four things make Live feel different from text chat:

- **Bidirectional audio** over a single WebSocket. Not request-then-response; they run simultaneously.
- **Voice Activity Detection (VAD)** — Gemini decides when you've stopped talking and starts responding. You don't say "okay, done"; silence triggers response.
- **Interruption** — if you start talking while Gemini is mid-response, Gemini stops immediately and listens. The natural "wait, actually..." pattern humans use.
- **Sub-second latency** on happy-path sessions.

## The three primitives

| Primitive | Role |
|---|---|
| `LiveRequestQueue` | Client-side queue you push user input into (text chunks via `send_content`, audio blobs via `send_realtime`) |
| `Runner.run_live(...)` | Async generator yielding server events; runs until you close the queue |
| `RunConfig(response_modalities=[...])` | Which output modalities — `"TEXT"`, `"AUDIO"`, or both |

Same `Runner` as the previous 12 modules; different method. Same event-stream shape; different transport.

Model names that ship the Live capability move around — check [ai.google.dev/gemini-api/docs/live](https://ai.google.dev/gemini-api/docs/live) for the current catalog. As of this writing:

- **`gemini-3.1-flash-live-preview`** — preview, free-tier-available. What the notebook tries.
- **`gemini-live-2.5-flash-native-audio`** — paid, production-grade, ~$0.012 per minute of audio.

## The API shape — text-mode Live

Before audio, see the API mechanics with text-only Live. Same WebSocket, same queue, same event generator — just text in text out.

```python
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

live_agent = LlmAgent(
    name="live_chat_agent",
    model="gemini-3.1-flash-live-preview",
    instruction="Chat casually, keep replies short.",
)

session_service = InMemorySessionService()
await session_service.create_session(app_name="m13", user_id="u", session_id="s1")
runner = Runner(agent=live_agent, app_name="m13", session_service=session_service)

queue = LiveRequestQueue()
config = RunConfig(response_modalities=["TEXT"])   # text out so we can print it

# Push one user turn into the queue
queue.send_content(
    content=types.Content(role="user", parts=[types.Part(text="Say hi.")]),
)

# Iterate events until the turn completes
async for event in runner.run_live(
    user_id="u", session_id="s1",
    live_request_queue=queue, run_config=config,
):
    if event.content and event.content.parts:
        for p in event.content.parts:
            if p.text:
                print(p.text, end="", flush=True)
    if event.turn_complete:
        break

queue.close()
```

Four things to notice:

1. `queue.send_content(...)` pushes a Content object in. For audio, you'd call `queue.send_realtime(audio_bytes)` with raw PCM at 16kHz, mono, 16-bit instead.
2. `response_modalities=["TEXT"]` asks Gemini for text out. Use `["AUDIO"]` for production voice; the response events contain `inline_data` with raw PCM at 24kHz.
3. Iteration uses `async for event in runner.run_live(...)` — same as `run_async`, but continues streaming until `event.turn_complete` or the queue closes.
4. `queue.close()` ends the session; do this in a `finally` block in production.

For multi-turn conversation, keep the queue open and keep pushing more content in; keep iterating the generator. The WebSocket never closes until you want it to.

## Voice Activity Detection + interruption

Both handled server-side. Default on. Tune via `RealtimeInputConfig` in `RunConfig`:

```python
from google.genai.types import RealtimeInputConfig, AutomaticActivityDetection

config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=RealtimeInputConfig(
        automatic_activity_detection=AutomaticActivityDetection(
            silence_duration_ms=1000,     # wait 1s of silence before responding
            prefix_padding_ms=200,        # 200ms of context before detected speech
        )
    ),
)
```

**`silence_duration_ms`** is the main knob. Lower (300-500ms) makes the agent snappy but triggers on brief pauses inside a sentence. Higher (1500ms+) waits for longer silences, feels more natural but noticeably delayed. 1000ms is a sensible conversational default; 500ms works for command-style interfaces where users know exactly what they'll say.

**`prefix_padding_ms`** captures some audio before the detected speech start — ensures Gemini doesn't miss the leading consonant of a word. 200ms is usually enough.

Interruption is automatic. While Gemini is producing output audio, if you send more audio into the queue, Gemini stops producing and listens. You don't have to manage that; the protocol handles it.

## Production architecture sketch

What a real Live-voice product looks like:

```
Browser (user)              Your backend              Gemini
──────────────              ──────────────            ──────
Microphone ──WebSocket──▶   ADK agent
                               │
                               ├── LiveRequestQueue ◀── audio chunks
                               │
                               │                     ──WebSocket──▶
                               │                       Live API
                               │
                               ◀── event.audio chunks ──
                               │
Audio out   ◀──WebSocket──   stream response audio
                             (+ interruption signals)
```

- **Browser side:** Web Audio API captures microphone audio, encodes to PCM, streams over a WebSocket to your backend at ~16kHz.
- **Backend side:** the ADK agent with `run_live(...)` holds a WebSocket to Gemini. You push audio chunks into `LiveRequestQueue`, the generator yields events, you pull audio out of `event.content.parts[].inline_data` and stream it back to the browser.
- **Browser side again:** Web Audio API plays the response audio. On a new audio chunk from the user, the browser also pushes a "cancel output" signal; the backend handles mid-response interruption.

None of this lives in a notebook — the full path needs a browser with microphone access, a WebSocket server, and audio libraries. What lives in the notebook is the ADK-side of the API contract. For a full-stack version, start from the [`google/adk-samples`](https://github.com/google/adk-samples) voice-agent example.

## Fragility is real — and worth naming

The Live API is preview-tier, and preview means what it says. Expected failure modes you'll encounter:

- **APIError 1011 "Internal error encountered"** on `live.connect(...)`. Happens at the WebSocket handshake; nothing you can do. Retry or wait.
- **Connection drops mid-session.** Network blip, server rotation, quota exhaustion. Implement reconnection with session resumption (Live's session-handle feature persists state across reconnections — see docs).
- **Model-name rotation.** The current free-tier preview model is `gemini-3.1-flash-live-preview` as of April 2026; it was `gemini-2.0-flash-live-preview-09-2025` last quarter. The course's `DEMOS_BROKEN.md` logs the current state.
- **Transient latency spikes.** When the service is under load, sub-second latency becomes multi-second. Not ADK's fault.

The code shown in this chapter and the matching notebook is correct. What fails is server-side. When the Live API matures past preview — likely by late 2026 — this roughness goes away. The API shape you learn here will remain.

## Pricing

Audio is billed **by minute, not by token** — a quirk of real-time streaming.

| Model | Tier | Rate |
|---|---|---|
| `gemini-3.1-flash-live-preview` | Preview, free-tier-eligible | Free up to quota |
| `gemini-live-2.5-flash-native-audio` | Paid, production-grade | ~$0.012 per minute audio in/out |

For a conversational voice agent with one-minute average sessions, that's under a dollar per hundred sessions. Cheap enough that the per-minute cost is rarely the blocker. What blocks production deployments is quota — Live has much tighter rate limits than text models.

## When Live is the right tool

Live is for **real-time conversational voice**. Not for:

- **Transcription.** Use a dedicated STT service (Google Cloud Speech, OpenAI Whisper, AssemblyAI); feed the text to a regular agent.
- **TTS playback of pre-computed answers.** Use a dedicated TTS service (Google TTS, ElevenLabs, OpenAI Audio).
- **Non-interactive voice.** An agent narrating a pre-written script doesn't need Live.

Live is specifically for:

- **Sub-second response latency** — users notice delays above ~300ms in real conversation.
- **Interruption handling** — users talk over the agent; natural conversation requires it.
- **Open-session continuous dialog** — not turn-based chat; fluid back-and-forth.

For everything else, `run_async` with text in, text out, plus separate STT and TTS services is simpler, cheaper, and more controllable. Live is a specific tool for a specific problem.

## What to carry forward

- **Live is the most differentiated Gemini capability.** Bidirectional audio, VAD, interruption, sub-second latency. No competitor replicates it cleanly as of April 2026.
- **Three primitives:** `LiveRequestQueue`, `Runner.run_live()`, `RunConfig(response_modalities=[...])`.
- **API shape**: push inputs via `send_content`/`send_realtime`, iterate events with `async for`, `turn_complete` ends a turn, `queue.close()` ends the session.
- **VAD + interruption** server-side; tune via `RealtimeInputConfig.automatic_activity_detection`.
- **Production architecture**: browser microphone → WebSocket → backend ADK agent with `run_live` → Gemini Live API → response audio back. Notebook can't do the full loop.
- **Preview-tier fragility is real** — transient server errors, model-name rotation, connection drops. Code is correct; endpoint matures over time.
- **Use Live only for real-time conversational voice.** Transcription, TTS-of-answers, non-interactive voice all have simpler tools.

## Your turn

1. **Enumerate Live models on your key.** Which ones are listed under `supported_actions=["bidiGenerateContent"]`? Note which require a paid tier.
2. **Run the text-mode Live cell several times.** How consistently does it succeed? Do you hit 1011 errors?
3. **Sketch audio-mode.** Modify the notebook's Live cell to pass `response_modalities=["AUDIO"]`. Inspect response events — are there `inline_data` parts with audio bytes? Don't try to play them; just confirm they arrive.
4. **Rate-limit exploration.** Run multiple concurrent Live sessions. What rate limits appear on your key's tier?

Module 14 — the course finale — steps sideways into the **A2A protocol**. Agent-to-agent communication — the protocol Google donated to the Linux Foundation in June 2025 that's now the industry standard for agents talking to agents across vendors. 30-minute block: four nouns, one demo, the gotchas that make A2A worth understanding as architecture before infrastructure.
