# M14 — Speaker notes

---

## Slide 1 — Title

The A2A protocol. Not strictly ADK, but the thing that outlasts it. MCP and A2A together survive any specific model, any specific framework, any specific vendor. You've spent this entire course building agents that call tools. This is about those agents calling other agents, across processes, across organizations, possibly written in completely different frameworks.

---

## Slide 2 — MCP vs A2A framing

The split between MCP and A2A is the right frame for this whole section. MCP is the protocol for agents-calling-tools. A2A is the protocol for agents-calling-agents. Both are now under Linux Foundation governance. Both have stable-ish specs with official SDKs. That split is the single most durable takeaway here.

---

## Slide 3 — The journey

The trajectory, fast. Google launched A2A at Cloud Next in April 2025, then donated it to the Linux Foundation in June. IBM's competing ACP protocol merged in during August. In December, MCP was also donated to the new Agentic AI Foundation, which means A2A and MCP are now under cross-vendor governance together. Early 2026, A2A v1.0 landed with five official language SDKs. As of now, roughly 150 founding-member organizations have signed on, though the ADK integration is still marked experimental.

The protocol is real. The ecosystem is still catching up.

---

## Slide 4 — Four nouns header

The whole A2A protocol boils down to four nouns. Memorize these, because everything else about A2A is commentary on top of them.

---

## Slide 5 — The four nouns

Four nouns, one at a time.

First, the Agent Card: a JSON descriptor served at a well-known URL. It's the agent's identity, capabilities, skills, and authentication schemes. Think of it as an OpenAPI spec, but for an agent.

Second, the Task: a stateful, server-owned unit of work. It has an ID, a status that moves through working, input-required, and completed, a history of messages, and artifacts. Like a GitHub Issue: persistent, trackable, and long-running.

Third, the Message: one turn in a task. User or agent. Typed parts like text, file, or data. A chat message.

Fourth, the Artifact: the durable output of a task. Reports, images, structured JSON. It's distinct from messages. It's the deliverable, not the conversation.

One distinction worth getting right. Skills are the semantic list of things the agent can do: the menu. Capabilities are the protocol feature flags for streaming, push notifications, and history replay: whether the kitchen does delivery. Different concepts, different fields in the Agent Card.

---

## Slide 6 — Where A2A fits

The architectural picture is a layered pattern. An orchestrator agent, built in ADK, uses A2A to reach specialist agents, which might be LangGraph, CrewAI, or just another ADK agent in a different process or organization. Each specialist, in turn, uses MCP to call tools written in Go, Rust, TypeScript, or anything else.

A2A for agent-to-agent across frameworks. MCP for agent-to-tool across languages. That's the shape of a modern multi-agent deployment.

---

### Notebook break — Expose and consume

[Switch the screen to the notebook.]

Cells eight through fourteen. The first half exposes an ADK agent as an A2A service: `to_a2a(agent)`, a uvicorn server, and a live endpoint. Then we fetch the Agent Card from that endpoint and inspect what ADK auto-generated. The second half consumes the service: `RemoteA2aAgent` pointed at the Agent Card URL, dropped into a Runner, called exactly like a local agent.

Run both halves. The event stream from the consume side is the key thing to watch: it shows tool calls executing on the remote server, not locally.

[Switch back to the slide deck.]

---

## Slide 7 — Expose — to_a2a()

The server side is three lines. `to_a2a(agent)` wraps any ADK agent in a Starlette app that speaks A2A. Hand the app to uvicorn with a host and port, and you have an agent-as-HTTP-service. The Agent Card, the JSON-RPC endpoint, the task lifecycle: all auto-wired.

There's no A2A-specific code in the agent itself. Any `LlmAgent` you've already built works.

---

## Slide 8 — Consume — RemoteA2aAgent

The consume side mirrors the expose side. `RemoteA2aAgent` takes an Agent Card URL, fetches it, and exposes the remote agent as a local ADK agent. Drop it into a Runner or into another agent's `sub_agents` list. From the consuming side, the shape is identical to a local agent.

Two arguments matter: `name`, how the local side refers to it, and `agent_card`, the URL where the card lives. Plus `use_legacy=False`, which the next slide covers.

---

## Slide 9 — The event stream

The event stream from a remote agent call has four steps: the user message, a tool call executed on the remote server, the tool response, and the final text.

From your code's perspective, this is the same event shape as a local agent doing the same work. From the network's perspective, an HTTP call happened. A2A bridges the two without exposing the difference to the caller.

---

## Slide 10 — use_legacy=False

`RemoteA2aAgent(use_legacy=False)` is the one argument worth memorizing.

The default is `True`, and the legacy executor has three known bugs: user-message duplication, remote outputs mis-classified as thoughts, and sub-agent output loss on nested remote agents. Setting `use_legacy=False` replaces the executor with one that fixes all three.

New code should always pass `False` explicitly. The default will presumably flip in a future ADK release, but until it does, type the argument every time.

---

## Slide 11 — Agent Card structure

The Agent Card output from the notebook shows what ADK auto-generates. Name. Description. Protocol version: 0.3.0, which is the a2a-sdk line ADK depends on. Transport preference: JSON-RPC by default. Capabilities: what protocol features the agent supports. Default input and output modes. And skills: a list of things the agent can do, with descriptions and examples.

ADK derives all of this from your agent's name, description, and tools. For production agents, you'd author the card by hand: populate realistic examples in each skill, declare capabilities explicitly, and sign the card with `AgentCardSignature` for cryptographic identity. For a course demo, the auto-generated version is enough.

---

## Slide 12 — Maturity: honest read

An honest assessment of A2A's maturity in two halves.

What's real: A2A v1.0 is a stable specification. Linux Foundation governance is in place. Five official language SDKs exist. The cross-vendor protocol body has representatives from AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP, and ServiceNow.

What's thin: the ecosystem. Most of the 150 founding-member organizations are signatories, not shipping production integrations. ADK's A2A integration is still marked `@a2a_experimental`. The cross-org trust fabric (signed cards, registries, federated identity) is explicitly "future exploration" in the spec.

The practical framing: A2A is architecture worth understanding now. It is not infrastructure you'd bet production on this year. Build against it for new work; don't migrate existing production workloads yet. By late 2026 this should invert as the ecosystem matures.

---

## Slide 13 — Six gotchas

Six sharp edges worth naming.

First, the path rename. In v0.2 the Agent Card was at `/.well-known/agent.json`. In v0.3, which is what ADK speaks, it moved to `/.well-known/agent-card.json`. Code from older blog posts has the wrong path.

Second, the legacy executor. Already covered. `use_legacy=False`, always.

Third, the version pin. ADK, through the current 2.4 release, requires a2a-sdk 0.3. A2A v1.0 requires a2a-sdk 1.0, which ADK doesn't yet speak. Don't mix versions.

Fourth, discovery is underspecified. The `.well-known` path is stable; registries are future work. Don't depend on registry features.

Fifth, Agent Engine is non-spec-default. Google's own Agent Engine serves the Agent Card at `/v1/card` behind authentication, not at `.well-known`. Third-party A2A clients expecting the standard path fail against Agent Engine. Flag this if you deploy there.

Sixth, cross-org trust is unsolved. Signed cards are in v1.0 as SHOULD, not MUST. There is no central root-of-trust CA for agents. Every cross-org A2A response is untrusted input to your planner. Simon Willison's lethal trifecta (private data plus untrusted content plus external communication) applies fully. Treat every remote agent's output as if a malicious user wrote it.

---

## Slide 14 — Carry forward

Four nouns. Two protocol splits: A2A for agent-to-agent, MCP for agent-to-tool. Six gotchas. The protocols outlast the frameworks, which is why understanding them is a durable investment.

---

## Slide 15 — Course finale header

The course finale. From "what is an agent" to "agents talking to agents across organizations."

---

## Slide 16 — What you can build

Here's what the course covered. Part 1 was ten modules of vendor-agnostic ADK: the four primitives, four tool flavors, state with scope prefixes, one-line model swaps across five providers, workflow agents (Sequential, Parallel, Loop), multi-agent composition with sub_agents and AgentTool, callbacks as middleware, persistent memory, automated evaluation with trajectory testing, and a deployed HTTP service.

Part 2 was three Gemini unlocks: Google Search grounding with real citations, long context with caching for ninety-percent cost reduction, thinking budgets that trade latency for reasoning quality, and the Live API for voice agents.

The side step was the A2A protocol: cross-framework agent-to-agent communication built on a cross-vendor open standard.

Put it together and you can build real agent software. Stateful. Memory-aware. Composable across frameworks. Deployable. Evaluable. Multi-modal. Production-shaped.

---

## Slide 17 — Thanks

Thanks for taking the course. Go build something. That's the only way to actually learn this. A voice-first customer support bot. A research orchestrator. A personal assistant that survives restarts and remembers you across weeks. The course taught the mechanics. Building teaches the rest.
