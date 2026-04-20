# A2A protocol — the side step

The course finale. Thirty minutes on something that isn't strictly ADK at all — the **A2A protocol**, the industry standard for agent-to-agent communication.

You've spent thirteen chapters building ADK agents that talk to tools. This chapter is about those agents talking to **other agents** — across processes, across organizations, possibly written in completely different frameworks. This is the single most durable thing in this course. **MCP and A2A together will outlast any specific model, any specific framework, any specific vendor.**

## The framing

One sentence that captures everything. **MCP is agent↔tool. A2A is agent↔agent.**

You saw MCP in Module 02 — connecting an agent to a separate tool-server process. A2A is the protocol for the next layer up: one agent calling another agent across a network boundary. They're both under Linux Foundation governance now (A2A since June 2025, MCP since December 2025), so they evolve together as the standard for the agentic-AI infrastructure layer.

## The journey — fast

- **April 2025** — Google launches A2A at Cloud Next.
- **June 2025** — Donated to the Linux Foundation. Technical Steering Committee forms.
- **August 2025** — IBM's competing Agent Communication Protocol (ACP) merged in.
- **December 2025** — MCP also donated to the Linux Foundation's Agentic AI Foundation; A2A and MCP under cross-vendor governance together.
- **Early 2026** — A2A v1.0 spec landed. Five official language SDKs (Python, JavaScript, Java, Go, .NET).
- **Now** — ~150 founding-member organizations. ~23K GitHub stars. ADK's A2A integration still marked `@a2a_experimental`.

The spec is real and stable. The ecosystem is real but thin.

## The four nouns

Memorize these. Everything else about A2A is commentary on these four.

| Noun | What it is | Analogue |
|---|---|---|
| **Agent Card** | JSON descriptor at `/.well-known/agent-card.json` — identity, skills, capabilities, auth | OpenAPI spec, but for an agent |
| **Task** | Stateful, server-owned unit of work. ID, status, history, artifacts | A GitHub Issue |
| **Message** | One turn — user or agent — with typed parts (text/file/data) | A chat message |
| **Artifact** | Durable output of a task (reports, images, structured data) | An Issue's attachments |

Two more distinctions worth getting right:

- **Skills** are the semantic menu a discovering agent reads to decide whether to call — `translate_spanish`, `find_flights`, each with description and examples.
- **Capabilities** are protocol feature-flags — whether the agent supports streaming, push notifications, state-history replay.

Pithy version: *"skills are the restaurant's menu; capabilities are whether it does delivery."*

## Where A2A fits architecturally

The layered pattern A2A enables:

```
Orchestrator  ─────A2A─────▶  Remote specialist
  (ADK)                         (LangGraph, CrewAI,
    │                            or another ADK)
    │                              │
    │                              ├──MCP──▶ Tool server
    │                              │        (any language)
    │                              │
    │                              └──MCP──▶ Tool server
    │
    └──MCP──▶ Local tools
```

An orchestrator agent (say, ADK) uses **A2A** to reach specialist agents — which might be written in LangGraph or CrewAI or just another ADK process owned by a different team. Each specialist, in turn, uses **MCP** to call tools — which might be written in Go, Rust, TypeScript, whatever.

This is the shape of a modern multi-agent deployment. A2A for agent-to-agent across frameworks. MCP for agent-to-tool across languages. Your code is an orchestrator layer over both.

## Exposing an ADK agent as A2A — `to_a2a()`

```python
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import uvicorn

root_agent = LlmAgent(
    name="temperature_specialist",
    model=LiteLlm(model="openrouter/google/gemini-2.5-flash-lite"),
    description="Converts Celsius to Fahrenheit via convert_c_to_f tool.",
    instruction="Convert temperatures. Return only the number.",
    tools=[convert_c_to_f],
)

app = to_a2a(root_agent, host="localhost", port=8123)
uvicorn.run(app, host="localhost", port=8123)
```

Three lines do the server side. `to_a2a` returns a Starlette app. Starlette speaks A2A — it auto-generates the Agent Card, exposes the JSON-RPC endpoint, handles task lifecycle. You run it under uvicorn and you have an agent-as-HTTP-service any A2A client can call.

## Consuming an A2A agent — `RemoteA2aAgent`

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

remote = RemoteA2aAgent(
    name="remote_temp_agent",
    agent_card=f"http://localhost:8123{AGENT_CARD_WELL_KNOWN_PATH}",
    description="Remote temperature conversion specialist.",
    use_legacy=False,   # critical; see below
)

# Use it anywhere a regular agent fits
runner = Runner(agent=remote, ...)
```

`RemoteA2aAgent` takes an Agent Card URL, fetches it on first use, and exposes the remote agent as a local ADK agent. Drop it into a `Runner`, into another agent's `sub_agents=` list, or wrap it in an `AgentTool`. The composition patterns from Module 06 apply unchanged — A2A is just the transport underneath.

**The single most practical detail in this chapter: `use_legacy=False`.** The default is `True`, and the legacy executor has three known bugs:

1. User messages can be duplicated across the wire.
2. Remote agent outputs are mis-classified as "thoughts" in the event stream.
3. Nested remote agents can lose sub-agent output entirely.

The new path (`use_legacy=False`) replaces the executor with one that fixes these. For new code, always `False`. Type it explicitly every time until the default flips.

## The event stream — what a remote call looks like

When you run the remote agent:

```
USER: Convert 20 degrees Celsius to Fahrenheit.

[tool_call] convert_c_to_f                   ← ran on the REMOTE server
[tool_resp] {'celsius': 20, 'fahrenheit': 68.0}
[remote_temp_agent] 68
```

The `convert_c_to_f` tool call executed **on the remote server's side of the network**, not locally. Your side sees a regular event — tool call, tool response, final text — same shape as a local agent's work. A2A bridges the gap seamlessly.

This is the A2A payoff. From your agent's perspective, the specialist might as well be local. From the network's perspective, you made an HTTP call to a separate process. From the architectural perspective, you've just crossed a framework or organization boundary. The event stream doesn't care which.

## The Agent Card, up close

ADK auto-generates the Agent Card from your agent's name, description, and tools. Here's what the course's demo agent produces:

```json
{
  "name": "temperature_specialist",
  "description": "Converts Celsius to Fahrenheit via convert_c_to_f tool.",
  "protocolVersion": "0.3.0",
  "preferredTransport": "JSONRPC",
  "capabilities": {},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "temperature_specialist",
      "name": "model",
      "description": "Converts Celsius to Fahrenheit... Convert temperatures using the tool. Return only the number.",
      "tags": ["llm"],
      "examples": []
    },
    {
      "id": "temperature_specialist-convert_c_to_f",
      "description": "Convert Celsius to Fahrenheit.",
      "tags": ["tool"],
      "examples": []
    }
  ]
}
```

For production, you'd author this by hand:

- Populate `examples` on each skill with realistic invocations.
- Declare `capabilities.streaming: true` if your agent supports incremental output.
- Add `securitySchemes` and `security` blocks for authenticated endpoints.
- Sign the card with an `AgentCardSignature` (JWS over canonicalized JSON) so consumers can verify identity.

The auto-generated version is fine for internal and demo use; the carefully-authored version is what you ship to external consumers.

## Maturity — an honest read

What's real:

- **A2A v1.0** is a stable, published specification.
- **Linux Foundation governance** is in place with a cross-vendor Technical Steering Committee.
- **Five official SDKs** — Python, JavaScript, Java, Go, .NET.
- **150+ founding-member organizations** have signed on.

What's thin:

- Most of those 150 orgs are signatories, not shippers. Named customer references (Adobe, Tyson Foods, S&P Global Market Intelligence) exist, but no deep production post-mortems are public yet.
- ADK's A2A integration is still marked `@a2a_experimental`. Tool-call shapes can drift between ADK and a2a-sdk versions; `use_legacy=False` exists because the legacy path has bugs.
- The cross-org **trust fabric is unfinished**. Signed Agent Cards are in v1.0 as SHOULD, not MUST. There's no central root-of-trust CA for agents. Registries — how you discover an agent you haven't hard-coded a URL for — are explicitly marked "future exploration" in the spec.

The framing to carry: **A2A is architecture worth understanding, not infrastructure you'd bet production on this year.** Build against it for new work; don't migrate existing production workloads yet. By late 2026 this should invert as the ecosystem matures.

## Six gotchas

1. **The `.well-known` path rename.** `/.well-known/agent.json` (v0.2) became `/.well-known/agent-card.json` (v0.3). Code copied from older blogs has the wrong path.
2. **Legacy executor bugs.** `RemoteA2aAgent(..., use_legacy=True)` (the default) has three issues: user-message duplication, remote outputs mis-classified as thoughts, sub-agent output loss. Pass `use_legacy=False` always.
3. **Version-pin ADK and a2a-sdk together.** ADK 1.28-1.31 uses `a2a-sdk 0.3.24`; A2A v1.0 requires `a2a-sdk ≥ 1.0.0a1` which ADK doesn't yet speak. Don't mix.
4. **Discovery is underspecified.** The `.well-known` path is stable; registries are explicitly future work. Don't build on registry features.
5. **Agent Engine is non-spec-default.** Google's Agent Engine serves the Agent Card at `/v1/card` behind authentication, not at `/.well-known/`. Third-party A2A clients expecting the standard path will fail against Agent Engine.
6. **Cross-org trust is unsolved.** Every cross-org A2A response is **untrusted input** to your planner. Simon Willison's lethal trifecta — private data + untrusted content + external communications — applies fully. Treat every remote agent's output as if a malicious user wrote it; run it through the same guardrails you'd apply to user input.

## What to carry forward — M14

- **Four A2A nouns**: Agent Card, Task, Message, Artifact.
- **Two patterns**: A2A for agent↔agent; MCP for agent↔tool.
- **`to_a2a(agent)`** exposes any ADK agent as A2A; **`RemoteA2aAgent(agent_card=...)`** consumes one.
- **`use_legacy=False`** is non-negotiable for new code.
- **Version-pin** `google-adk` + `a2a-sdk` together.
- **Maturity check**: spec is real, ecosystem is thin. Architecture worth understanding; not yet production-grade infrastructure.
- **Cross-org trust is unsolved**; every remote agent's output is untrusted.

## Course finale

Fourteen chapters. From "what is an agent" to "agents talking to agents across organizations."

**Part 1 — Vendor-agnostic spine** (M01-M10). The four primitives; four tool flavors; state with scope prefixes; one-line model swaps; workflow agents (Sequential / Parallel / Loop); multi-agent via `sub_agents` and `AgentTool`; callbacks as middleware; memory with persistence and long-term recall; automated eval; deployment as HTTP service.

**Part 2 — Gemini unlocks** (M11-M13). Google Search grounding with real citations; long context + 90%-discount caching; thinking budgets; Live API voice agents.

**Side step** (M14). A2A protocol for cross-framework agent-to-agent communication.

### What to do next

- **Build something.** A voice-first customer-support bot. A research orchestrator. A personal assistant that survives restarts. The course taught mechanics; building teaches the rest.
- **Follow the protocols.** A2A and MCP are both under Linux Foundation governance. The protocols outlast frameworks; invest in understanding them as durable.
- **Watch the course repo.** `DEMOS_BROKEN.md` tracks what's broken at preview-tier; entries will be cleared as the APIs stabilize.

Thanks for taking the course. Go build something.
