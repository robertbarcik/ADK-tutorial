# M14 — Speaker notes

---

## Slide 1 — Title

Module fourteen. The course finale. The side step. Thirty minutes on something that isn't strictly ADK at all — the A2A protocol, the industry standard for agent-to-agent communication. You've spent thirteen modules building ADK agents that talk to tools. This module is about those agents talking to other agents, across processes, across organizations, possibly written in completely different frameworks. This is the thing that outlasts ADK-as-a-framework. MCP and A2A together will survive any specific model, any specific framework, any specific vendor.

---

## Slide 2 — MCP vs A2A framing

The dominant framing — and it's the right one. MCP is the protocol for agents-calling-tools. A2A is the protocol for agents-calling-agents. Both now under Linux Foundation governance. Both stable-ish specs with official SDKs. If you learn only one thing from this module, learn this split.

---

## Slide 3 — The journey

The trajectory, fast. Google launched A2A at Cloud Next in April 2025. Donated it to the Linux Foundation in June. IBM's competing ACP protocol merged in in August. In December, MCP was also donated to the new Agentic AI Foundation, so A2A and MCP are now under cross-vendor governance together. Early 2026, A2A v1.0 landed with five official language SDKs. As of now, there are about 150 founding-member organizations — though the ADK integration is still marked experimental.

That's the short version. The protocol is real; the ecosystem is still catching up.

---

## Slide 4 — Four nouns header

Four nouns. Memorize these. Everything else about A2A is commentary on these four.

---

## Slide 5 — The four nouns

Agent Card — a JSON descriptor served at a well-known URL. It's the agent's identity, capabilities, skills, and authentication schemes. OpenAPI spec but for an agent.

Task — a stateful, server-owned unit of work. It has an ID, a status that moves through working / input-required / completed, a history of messages, and artifacts. Like a GitHub Issue, roughly — persistent, trackable, long-running.

Message — one turn in a task. User or agent. Typed parts — text, file, data. A chat message.

Artifact — the durable output of a task. Reports, images, structured JSON. Distinct from messages; it's the deliverable, not the conversation.

One more distinction worth getting right. Skills are the restaurant's menu — the semantic list of things the agent can do. Capabilities are whether the restaurant does delivery — the protocol feature flags for streaming, push notifications, history replay.

---

## Slide 6 — Where A2A fits

The architectural picture. An orchestrator agent, built in ADK, uses A2A to reach specialist agents — which might be LangGraph, CrewAI, or just another ADK agent in a different process or organization. Each specialist, in turn, uses MCP to call tools — which might be written in Go, Rust, TypeScript, anything.

Layered pattern. A2A for agent-to-agent across frameworks. MCP for agent-to-tool across languages. This is the shape of a modern multi-agent deployment.

---

## Slide 7 — Live demo

Switch to the notebook. Cells eight through fourteen. We expose an ADK agent as an A2A service, fetch its Agent Card, create a RemoteA2aAgent that consumes it, and call the remote agent as if it were local.

---

## Slide 8 — to_a2a

The expose side. `to_a2a(agent)` takes any ADK agent and wraps it in a Starlette app. Starlette speaks A2A. You hand the app to uvicorn, run it on a port, and you have an agent-as-HTTP-service.

That's the whole server-side integration. Three lines of code. The Agent Card, the JSON-RPC endpoint, the task lifecycle — all auto-wired by `to_a2a`.

---

## Slide 9 — RemoteA2aAgent

The consume side. `RemoteA2aAgent` takes an Agent Card URL, fetches it, and exposes the remote agent as if it were a local ADK agent. You drop it into a Runner or into another agent's sub_agents list. From the consuming side, same shape as a local agent.

Two arguments matter. `name` — how the local side refers to it. `agent_card` — the URL where the card lives. Plus `use_legacy=False` which I'll get to in a moment.

---

## Slide 10 — Event stream

The event stream when you call the remote agent. User message. Tool call — but executed on the remote server, not locally. Tool response. Final text.

From your code's perspective, this is the same event shape as a local agent doing the same work. From the network's perspective, an HTTP call happened. A2A bridges the two.

---

## Slide 11 — use_legacy=False

The single most important practical detail in this module. `RemoteA2aAgent(use_legacy=False)`.

The default is True. The legacy executor has three known bugs — user-message duplication, remote outputs mis-classified as thoughts, and sub-agent output loss on nested remote agents. The new path, controlled by `use_legacy=False`, replaces the executor with one that fixes these.

You almost certainly want `False` for new code. The default will presumably flip eventually; until it does, type the argument explicitly every time.

---

## Slide 12 — Agent Card structure

The Agent Card's structure, condensed from the notebook output. Name. Description. Protocol version — 0.3.0 for ADK 1.28. Transport preference — JSON-RPC by default. Capabilities — what protocol features the agent supports. Default input and output modes. Skills — a list of things the agent can do, with descriptions and examples.

ADK auto-generates all of this from your agent's name, description, and tools. For production agents, you'd author it by hand — populate realistic examples in each skill, declare capabilities explicitly, sign the card with `AgentCardSignature` for cryptographic identity. For a course demo, the auto-generated version is enough.

---

## Slide 13 — Maturity honest read

An honest read on A2A's maturity.

What's real. A2A v1.0 is a stable specification. Linux Foundation governance is in place. Five official language SDKs. Cross-vendor protocol body with representatives from AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP, ServiceNow.

What's thin. The ecosystem. Most of the 150 founding-member organizations are signatories; not many are shipping production integrations. ADK's A2A integration is still marked `@a2a_experimental`. Cross-org trust fabric — signed cards, registries, federated identity — is explicitly "future exploration" in the spec.

The framing to carry. A2A is architecture worth understanding. It is not infrastructure you'd bet production on this year. Build against it for new work; don't migrate existing production workloads yet. By late 2026 this should invert as the ecosystem matures.

---

## Slide 14 — Six gotchas

Six sharp edges worth naming.

Path rename. In v0.2 the Agent Card was at `/.well-known/agent.json`. In v0.3 — which is what ADK speaks — it moved to `/.well-known/agent-card.json`. Code from older blog posts has the wrong path.

Legacy executor. Already covered. `use_legacy=False`, always.

Version pin. ADK 1.28 through 1.31 uses a2a-sdk 0.3.24. A2A v1.0 requires a2a-sdk 1.0 alpha, which ADK doesn't yet speak. Don't mix versions.

Discovery is underspecified. The `.well-known` path is stable; registries are future work. Don't depend on registry features.

Agent Engine is non-spec-default. Google's own Agent Engine serves the Agent Card at `/v1/card` behind authentication, not at `.well-known`. Third-party A2A clients expecting the standard path fail against Agent Engine. Flag this if you deploy there.

Cross-org trust is unsolved. Signed cards are in v1.0 as SHOULD, not MUST. There is no central root-of-trust CA for agents. Every cross-org A2A response is untrusted input to your planner. Simon Willison's lethal trifecta — private data plus untrusted content plus external communication — applies fully. Treat every remote agent's output as if a malicious user wrote it.

---

## Slide 15 — Carry forward

What to carry forward. Four nouns. Two patterns — A2A for agent-to-agent, MCP for agent-to-tool. Six gotchas. The protocols outlast the frameworks. Invest in understanding them as durable.

---

## Slide 16 — Course finale header

The course finale. Fourteen modules. From "what is an agent" to "agents talking to agents across organizations."

---

## Slide 17 — What you can build

The summary. Part 1 — ten modules of vendor-agnostic ADK. The four primitives. Four tool flavors. State with scope prefixes. One-line model swaps across five providers. Workflow agents — Sequential, Parallel, Loop. Multi-agent composition — sub_agents for transfer, AgentTool for consultant. Callbacks as middleware. Memory that persists across restarts and recalls across sessions. Automated evaluation with trajectory testing. Deployed HTTP service.

Part 2 — three Gemini unlocks. Google Search grounding with real citations. Long context plus caching for ninety-percent cost reduction. Thinking budgets that trade latency for reasoning quality. Live API voice agents.

And the side step — A2A protocol for cross-framework agent-to-agent.

After fourteen modules, you can build real agent software. Stateful. Memory-aware. Composable across frameworks. Deployable. Evaluable. Multi-modal. Production-shaped.

---

## Slide 18 — Thanks

Thanks for taking the course. Go build something. That's the only way to actually learn this stuff. A voice-first customer support bot. A research orchestrator. A personal assistant that survives restarts and remembers you across weeks. The course taught the mechanics; building teaches the rest.
