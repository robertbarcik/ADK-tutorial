# M13 — Speaker notes

---

## Slide 1 — Title

Module thirteen. Live API voice agent. The third and most interesting of the three Gemini unlocks. Bidirectional audio streaming. Voice activity detection. Interruption handling. This is the capability that makes Gemini genuinely hard to replace — nothing in the Claude, GPT, or open-weight ecosystem ships this cleanly as of April 2026.

---

## Slide 2 — The most differentiated capability

The framing. Gemini Live is the single most differentiated capability Gemini ships that no competitor replicates cleanly. OpenAI's Realtime API is the closest alternative — different semantics, different pricing, different failure modes. Anthropic has no direct equivalent. If real-time voice is your product, Gemini is where you build.

---

## Slide 3 — What Live does

Four things. Bidirectional audio — voice in, voice out, over a single WebSocket connection. Voice Activity Detection — Gemini decides when you've stopped talking and starts responding. You don't have to say "okay, done"; silence triggers response. Interruption — if you start talking while Gemini is mid-response, Gemini stops immediately and listens. The natural conversational pattern humans use. And sub-second latency on the happy path.

---

## Slide 4 — Live vs run_async

The API-level difference from everything you've seen. `run_async` is request/response. You hand in a message, events stream back, the turn ends, you move on. Every turn is independent; the session is just history.

`run_live` is different. The agent holds an open bidirectional WebSocket to Gemini. You don't hand over a single message; you stream chunks of audio — or text — into a queue. Chunks of response stream back in parallel. The session is open for as long as you need it; no turn-based structure.

Text-based agents fit run_async. Voice agents need run_live.

---

## Slide 5 — Three primitives

The primitives. LiveRequestQueue — the client-side queue where you push user input. Text chunks or audio blobs. You call `send_content` for text; `send_realtime` for raw audio bytes.

`Runner.run_live` — the async generator that yields server events. Runs until the queue closes or turn-complete. Same shape as run_async; different mechanism.

RunConfig with response_modalities — you specify `TEXT`, `AUDIO`, or both. Audio gives you raw PCM bytes in the response's inline_data field. Text gives you regular text. You'd pick AUDIO for production voice agents, TEXT for development and testing.

---

## Slide 6 — Code shape

Here's the shape. Define an LlmAgent with a Live-capable model — gemini-3.1-flash-live-preview on free tier, gemini-live-2.5-flash-native-audio on paid. Create a LiveRequestQueue. Create a RunConfig with your modality. Push user content into the queue. Iterate run_live's async generator, consume events. Close the queue when done.

Key thing to notice: the queue stays open across turns. For multi-turn conversation, you keep pushing more content into the queue, keep iterating the generator. The WebSocket never closes.

---

## Slide 7 — VAD + interruption

Voice Activity Detection and interruption are handled server-side. Default on. If you want to tune VAD sensitivity, pass a RealtimeInputConfig in the RunConfig with an automatic_activity_detection block.

Two parameters worth knowing. `silence_duration_ms` — how long Gemini waits for silence before deciding you've stopped talking. Default is around 800ms. Lower means snappier but more false triggers from brief pauses. Higher means more natural-feeling but noticeable delay. A thousand milliseconds is a sensible conversational default.

`prefix_padding_ms` — how much audio context to capture before the detected speech start. A couple hundred ms ensures Gemini doesn't miss the beginning of your sentence.

Interruption is automatic. If you send audio into the queue while Gemini is producing output, Gemini stops producing and listens. You don't have to manage that; it's in the protocol.

---

## Slide 8 — Production architecture

What a real Live-voice product looks like. Browser on the user's side captures microphone audio via Web Audio API, streams it over a WebSocket to your backend. Your backend pushes those audio chunks into a LiveRequestQueue. The ADK agent with run_live holds a WebSocket to Gemini and relays the audio. Response audio chunks come back through the same ADK agent, get relayed back to the browser WebSocket, played out via Web Audio.

None of this lives in a notebook. It needs a browser with microphone access, a WebSocket server, audio libraries. The notebook teaches the ADK-side contract — what the agent sees, how to interact with the queue. For the full stack with browser integration, the adk-samples repo has a voice-agent example.

---

## Slide 9 — Live demo

Switch to the notebook. Cell nine. Text-mode Live session — pushes one message into the queue, iterates run_live, captures the text response. Watch the output carefully — this is the API shape regardless of whether the endpoint succeeds.

---

## Slide 10 — Fair warning

Fair warning, on its own slide. The Live API is preview-tier and currently brittle. You will see transient server-side errors. Code 1011 "Internal error encountered." Connection drops. Random timeouts. These are at Google's side, not your code's. The course repo logs exactly what's failing at this moment in DEMOS_BROKEN.md.

What to do. Learn the API shape today — the code in the notebook is correct, and the concepts are durable. When you want a verified working Live demo, retry in a few weeks as the API stabilizes, switch to a paid tier, or run against Vertex AI, which uses different infrastructure under the hood.

The Live endpoint will improve. What you learn about the API won't change.

---

## Slide 11 — Pricing

Pricing. Audio is billed by minute, not by token — a quirk of real-time streaming. gemini-3.1-flash-live-preview is on the free tier up to quota limits. gemini-live-2.5-flash-native-audio is paid tier, about 1.2 cents per minute of audio in and out combined. For a conversational voice agent with one-minute average sessions, that's under a dollar per hundred sessions.

Model names rotate. Check the Google AI developer docs for the current catalog when you're building for production.

---

## Slide 12 — When to use Live

When Live is the right tool. Real-time conversational voice. Interruption handling — users will talk over you, and natural conversation needs it. Sub-second latency requirements — users notice delays above a few hundred milliseconds in conversation. Open-session continuous dialog, not turn-based chat.

When it's not the right tool. Transcription — use a dedicated speech-to-text service; feed the text to a regular agent. TTS playback of pre-computed answers — use a dedicated TTS service. Non-interactive voice — an agent narrating a pre-written script doesn't need Live.

For everything else, run_async with text-in/text-out plus separate STT and TTS is simpler, cheaper, more controllable.

---

## Slide 13 — Carry forward

What to carry forward. Live is for real-time conversational voice. The API is run_live plus LiveRequestQueue plus RunConfig with response_modalities. The model names rotate. Preview-tier fragility is real; the teaching of the API shape is durable.

---

## Slide 14 — Next

Module fourteen. The course finale. The sidestep into A2A — the agent-to-agent protocol Google donated to the Linux Foundation in June 2025 that's now the industry standard for agents talking to agents across vendors. Thirty-minute block. Four nouns — Agent Card, Task, Message, Artifact. One demo — an ADK orchestrator calling a LangGraph currency-converter specialist over A2A. And the gotchas worth knowing because A2A is still preview-tier, too. See you there.
