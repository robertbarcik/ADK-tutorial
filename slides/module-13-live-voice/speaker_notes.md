# M13 — Speaker notes

---

## Slide 1 — Title

Welcome to module thirteen — the Live API voice agent. This is the third and most interesting of the three Gemini unlocks, and it's the one that covers bidirectional audio streaming, voice activity detection, and interruption handling. Really, this is the capability that makes Gemini genuinely hard to replace — nothing in the Claude, GPT, or open-weight ecosystem ships this cleanly as of April 2026.

---

## Slide 2 — The most differentiated capability

Let's start with the framing. Gemini Live is the single most differentiated capability Gemini ships that no competitor replicates cleanly. The closest alternative is OpenAI's Realtime API — different semantics, different pricing, and different failure modes. Anthropic, on the other hand, has no direct equivalent at all. So if real-time voice is your product, Gemini is where you build.

---

## Slide 3 — What Live does

Live really does four things. First, bidirectional audio — so voice in, voice out, all over a single WebSocket connection. Second, Voice Activity Detection — which means Gemini decides when you've stopped talking and starts responding on its own. You don't have to say "okay, done"; silence triggers the response. Third, interruption — if you start talking while Gemini is mid-response, Gemini stops immediately and listens. That's the natural conversational pattern humans actually use. And finally, sub-second latency on the happy path.

---

## Slide 4 — Live vs run_async

Now let's talk about the API-level difference from everything you've seen so far. `run_async` is request/response — you hand in a message, events stream back, the turn ends, and you move on. Every turn is independent, and the session is just history.

`run_live` is different. The agent holds an open bidirectional WebSocket to Gemini. So instead of handing over a single message, you stream chunks of audio — or text — into a queue. And chunks of response stream back in parallel. The session stays open for as long as you need it, with no turn-based structure.

So the rule of thumb is this. Text-based agents fit run_async. Voice agents need run_live.

---

## Slide 5 — Three primitives

There are three primitives here. First, the LiveRequestQueue — this is the client-side queue where you push user input, so text chunks or audio blobs. You call `send_content` for text and `send_realtime` for raw audio bytes.

Second, `Runner.run_live` — the async generator that yields server events. It runs until the queue closes or turn-complete fires. Same shape as run_async, just a different mechanism underneath.

And third, RunConfig with response_modalities — which is where you specify `TEXT`, `AUDIO`, or both. Audio gives you raw PCM bytes in the response's inline_data field, while text gives you regular text. You'd pick AUDIO for production voice agents, and TEXT for development and testing.

---

## Slide 6 — Code shape

In code, a Live agent looks like this. You define an LlmAgent with a Live-capable model — so gemini-3.1-flash-live-preview on the free tier, or gemini-live-2.5-flash-native-audio on paid. Create a LiveRequestQueue. Create a RunConfig with your modality. Push user content into the queue. Iterate run_live's async generator and consume the events. Close the queue when you're done.

If you remember one thing about this shape, remember that the queue stays open across turns. So for multi-turn conversation, you just keep pushing more content into the queue, and keep iterating the generator. The WebSocket never closes.

---

## Slide 7 — VAD + interruption

Voice Activity Detection and interruption are both handled server-side, and they're on by default. If you want to tune VAD sensitivity, pass a RealtimeInputConfig in the RunConfig with an automatic_activity_detection block.

There are two parameters worth knowing. The first is `silence_duration_ms` — which controls how long Gemini waits for silence before deciding you've stopped talking. The default is around 800ms. Lower means snappier, but more false triggers from brief pauses. Higher means more natural-feeling, but a noticeable delay. A thousand milliseconds is a sensible conversational default.

The second is `prefix_padding_ms` — which controls how much audio context to capture before the detected speech start. A couple hundred ms ensures Gemini doesn't miss the beginning of your sentence.

Interruption itself is automatic. If you send audio into the queue while Gemini is producing output, Gemini stops producing and listens. As a result, you don't have to manage that — it's in the protocol.

---

## Slide 8 — Production architecture

So what does a real Live-voice product actually look like? The browser on the user's side captures microphone audio via the Web Audio API, and streams it over a WebSocket to your backend. Your backend then pushes those audio chunks into a LiveRequestQueue. The ADK agent with run_live holds a WebSocket to Gemini and relays the audio. Response audio chunks come back through the same ADK agent, get relayed back to the browser WebSocket, and are played out via Web Audio.

None of this lives in a notebook. It needs a browser with microphone access, a WebSocket server, and audio libraries. The notebook teaches the ADK-side contract — so what the agent sees, and how to interact with the queue. For the full stack with browser integration, the adk-samples repo has a voice-agent example.

---

## Slide 9 — Live demo

Switch to the notebook, cell nine. This is a text-mode Live session — it pushes one message into the queue, iterates run_live, and captures the text response. Watch the output carefully — this is the API shape regardless of whether the endpoint succeeds.

---

## Slide 10 — Fair warning

Fair warning, on its own slide. The Live API is preview-tier and currently brittle. You will see transient server-side errors — things like code 1011 "Internal error encountered", connection drops, and random timeouts. These are on Google's side, not in your code. The course repo logs exactly what's failing at this moment in DEMOS_BROKEN.md.

So what do you do? Learn the API shape today — the code in the notebook is correct, and the concepts are durable. When you want a verified working Live demo, you have a few options — you can retry in a few weeks as the API stabilizes, switch to a paid tier, or run against Vertex AI, which uses different infrastructure under the hood.

The Live endpoint will improve. What you learn about the API won't change.

---

## Slide 11 — Pricing

Now let's talk about pricing. Audio is billed by the minute, not by the token — a quirk of real-time streaming. gemini-3.1-flash-live-preview is on the free tier up to quota limits. gemini-live-2.5-flash-native-audio is paid tier, at about 1.2 cents per minute of audio in and out combined. So for a conversational voice agent with one-minute average sessions, that's under a dollar per hundred sessions.

Model names rotate, so check the Google AI developer docs for the current catalog when you're building for production.

---

## Slide 12 — When to use Live

So when is Live the right tool? First, real-time conversational voice. Second, interruption handling — users will talk over you, and natural conversation needs it. Third, sub-second latency requirements — users notice delays above a few hundred milliseconds in conversation. And finally, open-session continuous dialog, not turn-based chat.

When is it not the right tool? For transcription, for example — use a dedicated speech-to-text service and feed the text to a regular agent. For TTS playback of pre-computed answers — use a dedicated TTS service. And for non-interactive voice — an agent narrating a pre-written script doesn't need Live.

For everything else, run_async with text-in/text-out plus separate STT and TTS is simpler, cheaper, and more controllable.

---

## Slide 13 — Carry forward

So what should you carry forward from today? Live is for real-time conversational voice. The API is run_live plus LiveRequestQueue plus RunConfig with response_modalities. The model names rotate. And preview-tier fragility is real — but the teaching of the API shape is durable.

---

## Slide 14 — Next

Module fourteen is the course finale — a sidestep into A2A, the agent-to-agent protocol Google donated to the Linux Foundation in June 2025 that's now the industry standard for agents talking to agents across vendors. It's a thirty-minute block. Four nouns — Agent Card, Task, Message, and Artifact. One demo — an ADK orchestrator calling a LangGraph currency-converter specialist over A2A. Plus the gotchas worth knowing, because A2A is still preview-tier, too. See you there.
