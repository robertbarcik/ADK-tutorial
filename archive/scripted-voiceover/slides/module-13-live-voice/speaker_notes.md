# M13 — Speaker notes

---

## Slide 1 — Title

The Live API. Bidirectional audio streaming, voice activity detection, and interruption handling over a single WebSocket. This is the third of the three Gemini unlocks, and the most differentiated: no other vendor ships this capability cleanly as of May 2026.

---

## Slide 2 — The most differentiated capability

Gemini Live is the single Gemini capability with no clean competitor alternative. The closest is OpenAI's Realtime API, with different semantics, different pricing, and different failure modes. Anthropic has no direct equivalent. If real-time voice is your product, Gemini is where you build.

---

## Slide 3 — What Live does

Live does four things. Bidirectional audio: voice in, voice out, over a single WebSocket connection. Voice Activity Detection: Gemini decides when you've stopped talking and starts responding without being prompted. Interruption: if you start talking while Gemini is mid-response, it stops immediately and listens. And sub-second latency on the happy path.

That last one, interruption, is what makes this feel like a real conversation rather than a phone-menu system.

---

## Slide 4 — Live vs run_async

`run_async` is request/response. You hand in a message, events stream back, the turn ends. Every turn is independent.

`run_live` is different. The agent holds an open bidirectional WebSocket to Gemini. Instead of a single message, you stream chunks of audio or text into a queue, and response chunks stream back in parallel. The session stays open for as long as you need it, with no turn-based structure.

Text-based agents fit `run_async`. Voice agents need `run_live`.

---

## Slide 5 — Three primitives

Three primitives make up the Live API contract.

`LiveRequestQueue` is the client-side queue where you push user input: `send_content` for text, `send_realtime` for raw audio bytes.

`Runner.run_live` is the async generator that yields server events. It runs until the queue closes or a turn-complete event fires.

`RunConfig` with `response_modalities` controls the output shape. `TEXT` gives you regular text chunks. `AUDIO` gives you raw PCM bytes in the `inline_data` field. Use `TEXT` in development and `AUDIO` in production voice agents.

---

## Slide 6 — Code shape

A Live agent follows a five-step pattern. Define an `LlmAgent` with a Live-capable model. Create a `LiveRequestQueue`. Create a `RunConfig` with your modality. Push user content into the queue with `send_content`. Then iterate `run_live`'s async generator and consume events until you close the queue.

The key property of this shape: the queue stays open across turns. For multi-turn conversation, you keep pushing content and keep consuming events. The WebSocket never closes between questions.

---

## Slide 7 — VAD + interruption

Voice Activity Detection and interruption are handled server-side and are on by default. Tune them via `RealtimeInputConfig` inside `RunConfig`.

`silence_duration_ms` controls how long Gemini waits before treating a pause as end-of-turn. Default is around 800ms. Lower is snappier but more prone to false triggers from brief pauses. Higher feels more natural but adds perceptible delay. 1000ms is a sensible conversational default.

`prefix_padding_ms` captures a short audio window before detected speech starts, so Gemini doesn't miss the first syllable.

Interruption is automatic. Send audio into the queue while Gemini is producing output, and it stops and listens. No client-side code required.

---

## Slide 8 — Production architecture

A production Live-voice stack has three layers. The browser captures microphone audio via the Web Audio API and streams it over a WebSocket to your backend. Your backend pushes those audio chunks into a `LiveRequestQueue`. The ADK agent with `run_live` holds the Gemini WebSocket and relays audio both ways.

None of this runs in the notebook. The notebook teaches the ADK-side contract: what the agent sees, how to push input, how to consume events. For the full browser-plus-backend stack, the `adk-samples` repo has a voice-agent example.

---

### Notebook break — One Live audio turn

[Switch the screen to the notebook.]

The demo cell runs one Live audio turn end to end. It pushes a typed message into the queue, iterates `run_live`, and two streams come back at once. The audio itself arrives as inline data parts, and we count the bytes. The words arrive next to it through output transcription, first as partial chunks while the model speaks, then as one consolidated line marked finished.

One thing to point out in the config. Current live models are audio-native, so asking for text-only output gets the session rejected with error 1007. That is why the demo requests audio and reads the words from the transcription instead. If the cell hits a transient server error, run it again. The endpoint is preview-tier, and an occasional hiccup is on Google's side, not in your code.

[Switch back to the slide deck.]

---

## Slide 9 — Fair warning

Fair warning belongs on its own slide. The Live API is preview-tier. Through spring of twenty twenty-six it threw transient server errors on free keys, and Google patched the endpoint in July. Sessions connect reliably now, but the occasional drop or timeout is still on Google's side, not in your code. The current state is logged in `DEMOS_BROKEN.md`.

The concepts you are learning are durable either way. If you ever hit persistent failures, switch to a paid tier or run against Vertex AI, which uses different infrastructure under the hood.

---

## Slide 10 — Pricing

Pricing for Live is per minute, not per token. `gemini-3.1-flash-live-preview` is free up to quota. `gemini-2.5-flash-native-audio-latest` is paid, at about 1.2 cents per minute of audio in and out combined. For a conversational agent averaging one minute per session, that's under a dollar per hundred sessions.

Model names rotate. Check the Google AI developer docs for the current catalog when building for production.

---

## Slide 11 — When to use Live

Live is the right tool for real-time conversational voice, especially when you need interruption handling, sub-second latency, or open-session continuous dialog.

It's not the right tool for transcription: use a dedicated speech-to-text service and feed the text to a regular agent. Not for TTS playback of pre-computed answers: use a dedicated TTS service. Not for non-interactive voice: a narration script doesn't need a live connection.

For everything else, `run_async` with text plus separate STT and TTS is simpler, cheaper, and more controllable.

---

## Slide 12 — Carry forward

Live is for real-time conversational voice. The API is `run_live` plus `LiveRequestQueue` plus `RunConfig` with response modalities. Model names rotate. Preview-tier fragility is real today; the API shape is durable.

---

## Slide 13 — Next

The course finale: A2A, the agent-to-agent protocol. You've spent this entire course building agents that call tools. The next module covers agents calling other agents, across processes, frameworks, and organizations. Four nouns, one live demo, and the gotchas worth knowing before you ship.
