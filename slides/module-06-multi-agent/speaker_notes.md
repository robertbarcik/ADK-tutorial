# M06 — Speaker notes

---

## Slide 1 — Title

Module six. Multi-agent hierarchies. Module five gave you named, declarative workflow — Sequential, Parallel, Loop. This module gives you the other half: LLM-driven routing. When the user's input decides which specialist runs, you don't want a workflow agent. You want the LLM to route. ADK has two patterns for exactly this, and they look similar on the surface but behave very differently.

---

## Slide 2 — Three ways to combine agents

Three ways, total, to compose agents in ADK.

Workflow agents — that was module five. Declarative control flow, named primitives, you say Sequential or Parallel or Loop and the framework runs the pattern. Use them when you can name the workflow.

Sub-agents — that's today. LLM-driven routing via transfer. The coordinator's LLM picks which specialist should take over, and ADK hands off control.

AgentTool — also today. LLM-driven routing via function call. The coordinator picks which specialist to call, the specialist runs, the coordinator stays in charge.

Today we focus on the two LLM-driven patterns.

---

## Slide 3 — The one question

The one question that separates the two patterns — the only meaningful difference — is this. After the specialist finishes its work, who is in charge of the conversation? If the specialist is, you want sub_agents. If the coordinator is, you want AgentTool. That's the whole decision.

---

## Slide 4 — sub_agents header

Pattern one. `sub_agents`. The org-chart transfer.

---

## Slide 5 — How sub_agents works

The mechanics. You give the coordinator a `sub_agents=` list. ADK detects this and automatically injects a built-in tool called `transfer_to_agent`. You don't register it; it's just there.

When the coordinator's model reads the user's message and decides a specialist fits, it emits a structured call — `transfer_to_agent(agent_name='weather_specialist')`. ADK catches that call and routes control to the named child. The child runs, produces a response, and that response is what the user sees.

After the transfer, the child remains the active agent for the rest of the session by default. If the user sends a follow-up, it goes to the specialist — not back to the coordinator. The specialist owns the conversation.

Think of it as an org chart. The coordinator is the manager reading the inbox; the specialist takes the meeting.

One production-sensitive detail: the child's `description=` field is what the coordinator's LLM reads to decide whether to route there. Write descriptions for the model, not for a human reviewer. "Handles greetings" is fine; "Agent that greets users warmly and makes them feel welcome" is noise.

---

## Slide 6 — sub_agents code

Here's the shape. Two specialists, each with a name, a description — that's the routing schema — and its own instruction. A coordinator that has both in its `sub_agents=` list. That's it. No routing code; ADK handles the transfer mechanism.

---

## Slide 7 — Live: transfer

Switch to the notebook. Cells twelve and thirteen. Greeting first, weather second. Watch the event stream — you'll see `transfer_to_agent` as a tool call from the coordinator, and the specialist produces the final response.

---

## Slide 8 — Event stream of transfer

Back on the slide. Here's what you saw. The coordinator emitted `transfer_to_agent` with `agent_name='weather_specialist'`. ADK routed. The weather specialist produced the final response.

The key thing to notice is the **author** of the final response. It's the specialist, not the coordinator. That's the tell that this is a transfer pattern.

---

## Slide 9 — AgentTool header

Pattern two. `AgentTool`. The consultant pattern.

---

## Slide 10 — How AgentTool works

Same team, different wiring. Instead of putting the specialists in `sub_agents=`, you wrap each in `AgentTool(agent=...)` and put them in the coordinator's `tools=` list.

Now to the coordinator's LLM, they look like tools — no different from a FunctionTool, an OpenAPI tool, an MCP tool. When the coordinator decides to use a specialist, it emits a regular function call — the same mechanism that triggers `get_weather` or `search_tickets` in earlier modules.

ADK runs the specialist as a fresh LLM call. The specialist produces its output. That output comes back to the coordinator as a tool-response event. The coordinator reads it and produces the final user-facing reply itself.

The specialist never gets the microphone. It answers a structured question, hands the result back, and the coordinator speaks on its behalf.

---

## Slide 11 — AgentTool code

The same specialists we just saw, but now wrapped in `AgentTool` and placed in the coordinator's `tools=` list — not `sub_agents=`. That single word difference in the constructor is the whole behavioral difference.

---

## Slide 12 — Live: consultant

Switch to the notebook. Cells eighteen and nineteen. Same prompts as before — greeting, weather. Watch the event stream carefully. Compare it to the transfer pattern you just saw.

---

## Slide 13 — Event stream — note the author

Back on the slide. The coordinator called `weather_specialist` as a tool. A tool-response event came back with the result. Then the coordinator — not the specialist — produced the final reply.

That's the consultant pattern. The specialist answered a specific question and stepped back. The coordinator remained in charge of speaking to the user.

---

## Slide 14 — Tell-tale sign

The tell-tale sign, on one slide. Look at the author of the final response.

If the specialist is the author, you're looking at a transfer. sub_agents pattern.

If the coordinator is the author, you're looking at a consultant call. AgentTool pattern.

That's the diagnostic. Print the event stream, read the last author, you know which pattern is in use.

---

## Slide 15 — When to pick which

When to pick which.

Use sub_agents — the transfer pattern — when the specialist should own the dialog. When the specialist might take multiple turns with the user before handing back. When a topic shift means the specialist is the right conversation partner for that whole topic. When you want the user to perceive they're talking to a specialist.

Use AgentTool — the consultant pattern — when the specialist answers one question and steps back. When the specialist has a clean input/output contract. When the coordinator needs to compose the specialist's output with other sources — multiple tools, other specialists. When you want the user to perceive they're talking to one assistant that has specialists behind the scenes.

---

## Slide 16 — Concrete examples

Two concrete examples to ground the rules.

Sub_agents scenario. IT support desk with a billing specialist and a hardware specialist. User says "my laptop won't boot." Coordinator routes to hardware. Over the next five turns of the session, the hardware specialist walks the user through diagnosis — power, connections, BIOS, boot order. That's an extended conversation the coordinator shouldn't mediate. Transfer once; let the specialist handle the topic.

AgentTool scenario. Coding assistant whose orchestrator wraps a specialist code-analyzer, a specialist docs-lookup, and a specialist test-runner. User asks "why is my test failing?" The orchestrator decides all three specialists are relevant, calls all three in one turn, reads their three tool-responses, synthesizes one answer. Each specialist contributes a single structured response; the orchestrator owns the composition.

---

## Slide 17 — Interlude header

Two-minute interlude. Agentic Design Patterns, chapter eight. Multi-agent decomposition. Theory on when multi-agent architectures pay for their coordination tax — and when they don't.

---

## Slide 18 — Coordination tax

Multi-agent architectures are fashionable. They're also expensive. Before you decompose a task into specialists, consider the coordination tax. It has three parts.

Extra LLM calls. Every transfer, every AgentTool call, is an additional model invocation. A two-specialist system makes at least two calls per user turn — one to route, one to resolve. A five-specialist system can make ten or more. This compounds latency and cost in production.

Routing errors. Every routing decision is a chance to pick the wrong specialist. The more specialists, the wider the miss surface. You have to design descriptions carefully enough that the coordinator's LLM never gets confused, and — when it inevitably does — your testing has to catch it.

Context fragmentation. Each child has its own system prompt. Information you put in the coordinator's instruction does not automatically reach the children. Specialists sometimes fail because they lack context the coordinator had. In a monolithic single agent, this problem doesn't exist — there's one prompt.

---

## Slide 19 — Three tests

Three tests from the publication to apply before you decompose.

Reuse test. Will any of these specialists be used elsewhere — by a different top-level agent, in a different product, by a different team? If yes, decomposition makes sense because the specialists become reusable components. If no, consider staying with one agent and adding more tools.

Model-heterogeneity test. Does each specialist benefit from a different model? Cheap routing decisions on Haiku, hard resolutions on Opus — that mix is only possible if you decompose. If all your specialists use the same model anyway, the decomposition buys you less.

Instruction-scale test. Is a single system prompt getting unmanageable — five hundred lines with overlapping rules for different scenarios? Breaking it up into specialists with narrower prompts is a legitimate way to reduce each prompt to its core job. But if your single-agent prompt is thirty lines, don't split it just because you can.

---

## Slide 20 — The default

The default, when none of the three tests pass. Keep it to one agent with tools. A single well-written agent with eight tools is almost always simpler, cheaper, and faster than a coordinator-plus-specialists architecture doing the same work. Multi-agent is sometimes the right answer. It is not the right answer by default.

---

## Slide 21 — Next

Module seven. Callbacks as middleware. Six lifecycle hooks that wrap every invocation — before_agent, after_agent, before_model, after_model, before_tool, after_tool. Return None and things proceed normally. Return a response object and you short-circuit the LLM or tool altogether. Django middleware, Express middleware, plugin hooks — for agents. The blocklist-guardrail demo is small, visual, and the cleanest example in the course of code-level safety. See you there.
