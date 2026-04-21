# M14 — Speaker notes

---

## Slide 1 — Title

Welcome to module fourteen — the course finale, and really a side step. This is about thirty minutes on something that isn't strictly ADK at all — the A2A protocol, which is the industry standard for agent-to-agent communication. You've spent thirteen modules building ADK agents that talk to tools. This module, on the other hand, is about those agents talking to other agents — across processes, across organizations, and possibly written in completely different frameworks. So this is the thing that outlasts ADK-as-a-framework. MCP and A2A together will survive any specific model, any specific framework, and any specific vendor.

---

## Slide 2 — MCP vs A2A framing

The dominant framing for this whole module is the split between MCP and A2A — and it's the right one. MCP is the protocol for agents-calling-tools. A2A, on the other hand, is the protocol for agents-calling-agents. Both are now under Linux Foundation governance, and both are stable-ish specs with official SDKs. If you learn only one thing from this module, learn that split.

---

## Slide 3 — The journey

Let me walk through the trajectory, fast. Google launched A2A at Cloud Next in April 2025, and then donated it to the Linux Foundation in June. IBM's competing ACP protocol merged in in August. In December, MCP was also donated to the new Agentic AI Foundation — which means A2A and MCP are now under cross-vendor governance together. Early 2026, A2A v1.0 landed with five official language SDKs. And as of now, there are about 150 founding-member organizations — though the ADK integration is still marked experimental.

That's the short version. The protocol is real; the ecosystem, on the other hand, is still catching up.

---

## Slide 4 — Four nouns header

The whole A2A protocol really boils down to four nouns. Memorize these, because everything else about A2A is commentary on top of them.

---

## Slide 5 — The four nouns

Let me walk through all four.

First, the Agent Card — a JSON descriptor served at a well-known URL. It's the agent's identity, capabilities, skills, and authentication schemes. Think of it as an OpenAPI spec, but for an agent.

Second, the Task — a stateful, server-owned unit of work. It has an ID, a status that moves through working, input-required, and completed, a history of messages, and artifacts. Like a GitHub Issue, roughly — so persistent, trackable, and long-running.

Third, the Message — one turn in a task. User or agent. Typed parts like text, file, or data. Really just a chat message.

And fourth, the Artifact — the durable output of a task. Things like reports, images, or structured JSON. It's distinct from messages — it's the deliverable, not the conversation.

One more distinction worth getting right. Skills are the restaurant's menu — so the semantic list of things the agent can do. Capabilities, on the other hand, are whether the restaurant does delivery — the protocol feature flags for things like streaming, push notifications, and history replay.

---

## Slide 6 — Where A2A fits

What you see on this slide is the architectural picture. An orchestrator agent, built in ADK, uses A2A to reach specialist agents — which might be LangGraph, CrewAI, or just another ADK agent in a different process or organization. Each specialist, in turn, uses MCP to call tools — which might be written in Go, Rust, TypeScript, or anything else.

So it's a layered pattern. A2A for agent-to-agent across frameworks. MCP for agent-to-tool across languages. That's the shape of a modern multi-agent deployment.

---

## Slide 7 — Live demo

Switch to the notebook — cells eight through fourteen. We expose an ADK agent as an A2A service, fetch its Agent Card, create a RemoteA2aAgent that consumes it, and then call the remote agent as if it were local.

---

## Slide 8 — to_a2a

Let me walk through the expose side first. `to_a2a(agent)` takes any ADK agent and wraps it in a Starlette app, and Starlette speaks A2A. You hand the app to uvicorn, run it on a port, and you have an agent-as-HTTP-service.

That's really the whole server-side integration — three lines of code. The Agent Card, the JSON-RPC endpoint, the task lifecycle — all auto-wired by `to_a2a`.

---

## Slide 9 — RemoteA2aAgent

Now onto the consume side. `RemoteA2aAgent` takes an Agent Card URL, fetches it, and then exposes the remote agent as if it were a local ADK agent. You drop it into a Runner or into another agent's sub_agents list. From the consuming side, it's the same shape as a local agent.

Two arguments matter. First, `name` — so how the local side refers to it. Second, `agent_card` — the URL where the card lives. Plus `use_legacy=False`, which I'll get to in a moment.

---

## Slide 10 — Event stream

Let me walk through the event stream when you call the remote agent. First, the user message. Second, a tool call — but executed on the remote server, not locally. Third, the tool response. And finally, the final text.

From your code's perspective, this is the same event shape as a local agent doing the same work. From the network's perspective, on the other hand, an HTTP call happened. A2A bridges the two.

---

## Slide 11 — use_legacy=False

If you remember one practical detail from this module, remember this — `RemoteA2aAgent(use_legacy=False)`.

The default is True, and the legacy executor has three known bugs — user-message duplication, remote outputs mis-classified as thoughts, and sub-agent output loss on nested remote agents. The new path, which is controlled by `use_legacy=False`, replaces the executor with one that fixes all three.

So you almost certainly want `False` for new code. The default will presumably flip eventually; but until it does, type the argument explicitly every time.

---

## Slide 12 — Agent Card structure

What you see on this slide is the Agent Card's structure, condensed from the notebook output. Name. Description. Protocol version — so 0.3.0 for ADK 1.28. Transport preference — JSON-RPC by default. Capabilities — what protocol features the agent supports. Default input and output modes. And finally skills — a list of things the agent can do, with descriptions and examples.

ADK auto-generates all of this from your agent's name, description, and tools. For production agents, on the other hand, you'd author it by hand — so populate realistic examples in each skill, declare capabilities explicitly, and sign the card with `AgentCardSignature` for cryptographic identity. For a course demo, the auto-generated version is enough.

---

## Slide 13 — Maturity honest read

Let me give you an honest read on A2A's maturity.

First, what's real. A2A v1.0 is a stable specification. Linux Foundation governance is in place. Five official language SDKs. And a cross-vendor protocol body with representatives from AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP, and ServiceNow.

Second, what's thin. The ecosystem. Most of the 150 founding-member organizations are signatories, but not many are shipping production integrations. ADK's A2A integration is still marked `@a2a_experimental`. And the cross-org trust fabric — things like signed cards, registries, and federated identity — is explicitly "future exploration" in the spec.

So the framing to carry forward is this. A2A is architecture worth understanding. It is not, on the other hand, infrastructure you'd bet production on this year. Build against it for new work; don't migrate existing production workloads yet. By late 2026 this should invert as the ecosystem matures.

---

## Slide 14 — Six gotchas

Before we wrap up, there are six sharp edges worth naming.

First, the path rename. In v0.2 the Agent Card was at `/.well-known/agent.json`. In v0.3 — which is what ADK speaks — it moved to `/.well-known/agent-card.json`. Code from older blog posts has the wrong path.

Second, the legacy executor. Already covered. `use_legacy=False`, always.

Third, the version pin. ADK 1.28 through 1.31 uses a2a-sdk 0.3.24. A2A v1.0, on the other hand, requires a2a-sdk 1.0 alpha, which ADK doesn't yet speak. So don't mix versions.

Fourth, discovery is underspecified. The `.well-known` path is stable; registries, on the other hand, are future work. Don't depend on registry features.

Fifth, Agent Engine is non-spec-default. Google's own Agent Engine serves the Agent Card at `/v1/card` behind authentication, and not at `.well-known`. As a result, third-party A2A clients expecting the standard path fail against Agent Engine. Flag this if you deploy there.

And finally, cross-org trust is unsolved. Signed cards are in v1.0 as SHOULD, not MUST. There is no central root-of-trust CA for agents. Every cross-org A2A response is untrusted input to your planner. Simon Willison's lethal trifecta — so private data plus untrusted content plus external communication — applies fully. Treat every remote agent's output as if a malicious user wrote it.

---

## Slide 15 — Carry forward

So what should you carry forward from this module? Four nouns. Two patterns — A2A for agent-to-agent, MCP for agent-to-tool. Six gotchas. The protocols outlast the frameworks, which is why you want to invest in understanding them as durable.

---

## Slide 16 — Course finale header

And now the course finale. Fourteen modules. From "what is an agent" to "agents talking to agents across organizations."

---

## Slide 17 — What you can build

Let me summarize what you can now build. Part 1 was ten modules of vendor-agnostic ADK. The four primitives. Four tool flavors. State with scope prefixes. One-line model swaps across five providers. Workflow agents — so Sequential, Parallel, and Loop. Multi-agent composition — sub_agents for transfer, AgentTool for consultant. Callbacks as middleware. Memory that persists across restarts and recalls across sessions. Automated evaluation with trajectory testing. And a deployed HTTP service.

Part 2 was three Gemini unlocks. Google Search grounding with real citations. Long context plus caching for ninety-percent cost reduction. Thinking budgets that trade latency for reasoning quality. And finally the Live API voice agents.

And then the side step — the A2A protocol for cross-framework agent-to-agent.

So, after fourteen modules, you can build real agent software. Stateful. Memory-aware. Composable across frameworks. Deployable. Evaluable. Multi-modal. Production-shaped.

---

## Slide 18 — Thanks

Thanks for taking the course. Go build something — that's really the only way to actually learn this stuff. Things like a voice-first customer support bot. Or a research orchestrator. Or a personal assistant that survives restarts and remembers you across weeks. The course taught the mechanics; building teaches the rest.
