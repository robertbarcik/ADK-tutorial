# Lecture plan — Skillmea filming map

One row per lecture (one video each). Slide ranges refer to the current decks;
`demo@SN` means the speaker notes place a notebook break after slide N — the demo
opens or sits inside that lecture, per the notebook-break sections in
`slides/module-NN-*/speaker_notes.md`. Estimates are narration word count at
~130 wpm plus ~2 min per notebook demo; slide-dwell adds to that in practice.

This file mirrors the "ADK" sheets in the Udemy and Skillmea overview workbooks
(Management drive). Update all three together when the plan changes.

## Welcome section

| # | Lecture | Slides | Est |
|---|---------|--------|-----|
| 0.1 | Course overview | M00 deck (4 slides) | ~3 min |
| 0.2 | About your instructor | none (talking head) | ~2 min |


# PART 1 — Build agents on any LLM

## Module 1 — Mental model

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 1.1 | What is ADK? | 1–3 | — | ~4 min |
| 1.2 | The agent mental model | 4–5 | — | ~2 min |
| 1.3 | The four primitives | 6–9 | — | ~5.5 min |
| 1.4 | Running your first agent | 10 | after S9 | ~2.5 min |
| 1.5 | Your first tool call | 11–12 | after S11 | ~4.5 min |
| 1.6 | The visual debugger and the alternatives | 13–14 | — | ~2 min |
| 1.7 | Vendor neutrality and the road ahead | 15–18 | — | ~4 min |

## Module 2 — Tools

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 2.1 | How tools work in ADK | 1–4 | — | ~3 min |
| 2.2 | Python functions as tools (FunctionTool) | 5–7 | after S7 | ~6 min |
| 2.3 | REST APIs as tools (OpenAPIToolset) | 8–10 | after S10 | ~6 min |
| 2.4 | MCP servers as tools (McpToolset) | 11–13 | after S13 | ~5.5 min |
| 2.5 | Agents as tools (AgentTool) | 14–16 | after S16 | ~5 min |
| 2.6 | Risk-based tool design | 17–18 | — | ~2 min |
| 2.7 | Where to put the guard | 19–20 | after S20 | ~5 min |
| 2.8 | Picking a flavor and avoiding gotchas | 21–24 | — | ~3 min |

## Module 3 — Sessions, state, events, artifacts

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 3.1 | What a session actually is | 1–4 | — | ~3 min |
| 3.2 | State and scope prefixes | 5–8 | — | ~5 min |
| 3.3 | Cross-session memory | 9 | after S8 | ~2.5 min |
| 3.4 | Three ways to write state | 10–11 | — | ~2 min |
| 3.5 | Events and artifacts | 12–14 | — | ~2.5 min |
| 3.6 | Skeptical memory and the takeaway | 15–19 | — | ~3 min |

## Module 4 — The one-line model swap (LiteLLM)

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 4.1 | How LiteLlm actually works | 1–4 | — | ~3 min |
| 4.2 | One agent, five providers | 5–6 | after S5 | ~4.5 min |
| 4.3 | Ollama, and using Gemini directly | 7–10 | — | ~3 min |
| 4.4 | Priority tiers in your instruction | 11–14 | after S14 | ~5.5 min |
| 4.5 | When to actually swap models | 15–17 | — | ~2 min |

## Module 5 — Workflow agents: Sequential, Parallel, Loop

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 5.1 | Three ways to compose agents | 1–4 | — | ~2.5 min |
| 5.2 | Sequential pipelines and state flow | 5–7 | after S7 | ~4.5 min |
| 5.3 | Concurrent fan-out with ParallelAgent | 8–10 | after S9 | ~4.5 min |
| 5.4 | The generator-critic loop | 11–15 | after S14 | ~7 min |
| 5.5 | Nesting workflows, and when to go LLM-driven | 16–20 | after S17 | ~6 min |

## Module 6 — Multi-agent hierarchies

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 6.1 | The key question: sub_agents vs AgentTool | 1–3 | — | ~2 min |
| 6.2 | The transfer pattern (sub_agents) | 4–7 | after S6 | ~5.5 min |
| 6.3 | The consultant pattern (AgentTool) | 8–11 | after S10 | ~5 min |
| 6.4 | Picking transfer vs consultant | 12–14 | — | ~2.5 min |
| 6.5 | When multi-agent is worth it | 15–19 | — | ~4 min |

## Module 7 — Callbacks as middleware

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 7.1 | The six hooks and the one rule | 1–5 | — | ~3 min |
| 7.2 | Blocking queries before the LLM sees them | 6–8 | after S7 | ~4.5 min |
| 7.3 | Redacting PII before the LLM sees it | 9–11 | after S10 | ~4.5 min |
| 7.4 | Mocking tools for tests | 12–14 | after S13 | ~4 min |
| 7.5 | When to use callbacks, and a gotcha | 15–19 | — | ~4.5 min |

## Module 8 — Memory: persistent sessions and long-term recall

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 8.1 | Two time scales of memory | 1–3 | — | ~2 min |
| 8.2 | Persistent sessions with a database | 4–7 | after S6 | ~5 min |
| 8.3 | Long-term memory with MemoryService | 8–11 | after S10 | ~6 min |
| 8.4 | Skeptical Memory and wrap-up | 12–16 | — | ~3.5 min |

## Module 9 — Evaluation

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 9.1 | Two metrics and why trajectory matters most | 1–4 | — | ~3 min |
| 9.2 | Running your first eval | 5–6 | after S6 | ~5 min |
| 9.3 | Why ROUGE-1 fails and what to use instead | 7–9 | — | ~3.5 min |
| 9.4 | The production evaluation stack | 10–14 | — | ~5.5 min |

## Module 10 — Deployment

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 10.1 | The three deployment paths | 1–3 | — | ~2 min |
| 10.2 | Your agent as an HTTP service | 4–8 | after S7 | ~4.5 min |
| 10.3 | Deploying with Docker or Cloud Run | 9–13 | — | ~2 min |
| 10.4 | Agent Engine: the managed path | 14–16 | — | ~1.5 min |
| 10.5 | Plugins, and what production actually needs | 17–19 | — | ~2 min |
| 10.6 | What you can build after ten modules | 20–22 | — | ~1 min |

# PART 2 — Gemini-only capabilities

## Module 11 — Gemini grounding and caching

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 11.1 | Part 2 begins: the three Gemini unlocks | 1–4 | — | ~2 min |
| 11.2 | Real citations with Google Search | 5–8 | after S6 | ~4.5 min |
| 11.3 | Long context, and two flavors of caching | 9–12 | — | ~2 min |
| 11.4 | Explicit caching, and the savings math | 13–14 | — | ~1.5 min |
| 11.5 | Native Gemini or LiteLLM? Have both | 15–18 | — | ~2 min |

## Module 12 — Thinking budgets

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 12.1 | What is a thinking budget? | 1–3 | after S3 | ~4 min |
| 12.2 | One knob, big quality difference | 4–6 | — | ~1.5 min |
| 12.3 | When thinking earns its keep | 7–9 | — | ~2 min |
| 12.4 | What makes Gemini's thinking different | 10–13 | — | ~2.5 min |

## Module 13 — Live API voice agent

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 13.1 | What the Live API actually does | 1–3 | — | ~1 min |
| 13.2 | The Live API in code | 4–6 | — | ~2 min |
| 13.3 | Voice detection, interruption, and production flow | 7–8 | after S8 | ~4.5 min |
| 13.4 | Running Live, and what can go wrong | 9–10 | — | ~1 min |
| 13.5 | When Live is the right tool | 11–13 | — | ~1 min |

# PART 3 — A2A: agents talking to agents

## Module 14 — Agent-to-agent (A2A)

| # | Lecture | Slides | Demo | Est |
|---|---------|--------|------|-----|
| 14.1 | What is A2A protocol | 1–3 | — | ~1.5 min |
| 14.2 | The four nouns of A2A | 4–5 | — | ~1.5 min |
| 14.3 | Exposing and consuming an A2A agent | 6–9 | after S6 | ~4.5 min |
| 14.4 | One flag and one card you need to know | 10–11 | — | ~1.5 min |
| 14.5 | An honest read on A2A, and six gotchas | 12–13 | — | ~2.5 min |
| 14.6 | Course finale: what you can build | 14–17 | — | ~1.5 min |

---

**Totals:** 77 lectures (75 module lectures + 2 welcome), 27 with a notebook demo, across 15 decks / 249 module slides + M00.
