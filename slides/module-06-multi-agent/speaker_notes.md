# M06 — Speaker notes

---

## Slide 1 — Title

Welcome to module six — multi-agent hierarchies. Module five gave you named, declarative workflow — so Sequential, Parallel, and Loop. This module gives you the other half of the story: LLM-driven routing. When the user's input is what decides which specialist runs, you don't want a workflow agent — you want the LLM itself to route. ADK has two patterns for exactly this, and they look similar on the surface, but they actually behave very differently. Today we pull them apart.

---

## Slide 2 — Three ways to combine agents

There are three ways, in total, to compose agents in ADK — and it's worth naming all three up front, so you see where today fits.

First, workflow agents — that was module five. Declarative control flow, named primitives — you say Sequential, Parallel, or Loop, and the framework runs the pattern. Use them when you can name the workflow.

Second, sub-agents — that's today. LLM-driven routing via transfer. The coordinator's LLM picks which specialist should take over, and ADK hands off control.

And third, AgentTool — also today. LLM-driven routing via function call. The coordinator picks which specialist to call, the specialist runs, and the coordinator stays in charge.

So today we focus on the two LLM-driven patterns, side by side.

---

## Slide 3 — The one question

If you remember one thing from this module, remember this single question — because it's really the only meaningful difference between the two patterns. After the specialist finishes its work, who is in charge of the conversation? If the specialist is, you want sub_agents. If the coordinator is, you want AgentTool. That's the whole decision — everything else is just mechanics.

---

## Slide 4 — sub_agents header

On to pattern one — `sub_agents`, the org-chart transfer.

---

## Slide 5 — How sub_agents works

Let me walk through the mechanics. You give the coordinator a `sub_agents=` list, and ADK detects this and automatically injects a built-in tool called `transfer_to_agent`. You don't register it — it's just there for you.

When the coordinator's model reads the user's message and decides a specialist fits, it emits a structured call — something like `transfer_to_agent(agent_name='weather_specialist')`. ADK catches that call and routes control to the named child. The child then runs, produces a response, and that response is what the user sees.

After the transfer, the child remains the active agent for the rest of the session by default. So if the user sends a follow-up, it goes to the specialist — not back to the coordinator. In other words, the specialist owns the conversation from that point on.

Think of it as an org chart. The coordinator is the manager reading the inbox; the specialist takes the meeting.

One production-sensitive detail worth flagging: the child's `description=` field is what the coordinator's LLM reads to decide whether to route there. So write descriptions for the model, not for a human reviewer. "Handles greetings" is fine; "Agent that greets users warmly and makes them feel welcome" is just noise.

---

## Slide 6 — sub_agents code

In code, the shape looks like this. Two specialists, each with a name, a description — that's really the routing schema — and its own instruction. Then a coordinator that has both in its `sub_agents=` list. And that's it. No routing code, because ADK handles the transfer mechanism for you.

---

## Slide 7 — Live: transfer

Switch to the notebook — cells twelve and thirteen. Greeting first, weather second. Watch the event stream carefully — you'll see `transfer_to_agent` appear as a tool call from the coordinator, and then the specialist produces the final response.

---

## Slide 8 — Event stream of transfer

Back on the slide, here's what you just saw in the notebook. The coordinator emitted `transfer_to_agent` with `agent_name='weather_specialist'`. ADK routed. The weather specialist produced the final response.

The key thing to notice is the **author** of that final response. It's the specialist, not the coordinator. That's the tell that this is a transfer pattern.

---

## Slide 9 — AgentTool header

On to pattern two — `AgentTool`, the consultant pattern.

---

## Slide 10 — How AgentTool works

Same team, just different wiring. Instead of putting the specialists in `sub_agents=`, you wrap each one in `AgentTool(agent=...)` and put them in the coordinator's `tools=` list.

Now, to the coordinator's LLM, they look like tools — no different from a FunctionTool, an OpenAPI tool, or an MCP tool. When the coordinator decides to use a specialist, it emits a regular function call — so the same mechanism that triggers `get_weather` or `search_tickets` in earlier modules.

ADK then runs the specialist as a fresh LLM call. The specialist produces its output. That output comes back to the coordinator as a tool-response event. The coordinator reads it, and produces the final user-facing reply itself.

So the specialist never gets the microphone. It answers a structured question, hands the result back, and the coordinator speaks on its behalf.

---

## Slide 11 — AgentTool code

In code, you see the same specialists we just saw — but now wrapped in `AgentTool` and placed in the coordinator's `tools=` list, not `sub_agents=`. That single word difference in the constructor is really the whole behavioral difference between the two patterns.

---

## Slide 12 — Live: consultant

Switch to the notebook — cells eighteen and nineteen. Same prompts as before — greeting, then weather. Watch the event stream carefully, and compare it to the transfer pattern you just saw.

---

## Slide 13 — Event stream — note the author

Back on the slide. The coordinator called `weather_specialist` as a tool. A tool-response event came back with the result. And then the coordinator — not the specialist — produced the final reply.

That's the consultant pattern in action. The specialist answered a specific question and stepped back, while the coordinator remained in charge of speaking to the user.

---

## Slide 14 — Tell-tale sign

So here's the tell-tale sign on one slide. Look at the author of the final response.

If the specialist is the author, you're looking at a transfer — so the sub_agents pattern.

If the coordinator is the author, you're looking at a consultant call — so the AgentTool pattern.

That's the diagnostic. Print the event stream, read the last author, and you know which pattern is in use.

---

## Slide 15 — When to pick which

So when should you pick which? Let me give you four markers for each side.

Use sub_agents — the transfer pattern — first, when the specialist should own the dialog. Second, when the specialist might take multiple turns with the user before handing back. Third, when a topic shift means the specialist is really the right conversation partner for that whole topic. And finally, when you want the user to perceive they're talking to a specialist.

Use AgentTool — the consultant pattern — first, when the specialist answers one question and steps back. Second, when the specialist has a clean input/output contract. Third, when the coordinator needs to compose the specialist's output with other sources — things like multiple tools, or other specialists. And finally, when you want the user to perceive they're talking to one assistant that just has specialists behind the scenes.

---

## Slide 16 — Concrete examples

Let me ground those rules with two concrete examples.

First, a sub_agents scenario. Imagine an IT support desk with a billing specialist and a hardware specialist. The user says "my laptop won't boot." The coordinator routes to hardware. Over the next five turns of the session, the hardware specialist walks the user through diagnosis — power, connections, BIOS, boot order. That's an extended conversation the coordinator shouldn't mediate. So you transfer once, and let the specialist handle the whole topic.

Now an AgentTool scenario. Think of a coding assistant whose orchestrator wraps a specialist code-analyzer, a specialist docs-lookup, and a specialist test-runner. The user asks "why is my test failing?" The orchestrator decides all three specialists are relevant, calls all three in one turn, reads their three tool-responses, and synthesizes one answer. Each specialist contributes a single structured response, and the orchestrator owns the composition.

---

## Slide 17 — Interlude header

Time for a two-minute interlude — Agentic Design Patterns, chapter eight, on multi-agent decomposition. Some theory on when multi-agent architectures pay for their coordination tax, and — just as importantly — when they don't.

---

## Slide 18 — Coordination tax

Multi-agent architectures are fashionable. They're also expensive. Before you decompose a task into specialists, you have to consider the coordination tax, and it has three parts.

First, extra LLM calls. Every transfer, and every AgentTool call, is an additional model invocation. A two-specialist system makes at least two calls per user turn — one to route, one to resolve. A five-specialist system can make ten or more. As a result, this compounds latency and cost in production.

Second, routing errors. Every routing decision is a chance to pick the wrong specialist. So the more specialists you have, the wider the miss surface. You have to design descriptions carefully enough that the coordinator's LLM never gets confused — and when it inevitably does, your testing has to catch it.

And third, context fragmentation. Each child has its own system prompt, which means information you put in the coordinator's instruction does not automatically reach the children. As a result, specialists sometimes fail because they lack context the coordinator had. In a monolithic single agent, this problem simply doesn't exist — there's just one prompt.

---

## Slide 19 — Three tests

The publication gives you three tests to apply before you decompose.

First, the reuse test. Will any of these specialists be used elsewhere — by a different top-level agent, in a different product, or by a different team? If yes, decomposition makes sense, because the specialists become reusable components. If no, consider staying with one agent and just adding more tools.

Second, the model-heterogeneity test. Does each specialist benefit from a different model? Cheap routing decisions on Haiku, hard resolutions on Opus — that mix is only possible if you decompose. But if all your specialists use the same model anyway, the decomposition buys you less.

And third, the instruction-scale test. Is a single system prompt getting unmanageable — say, five hundred lines, with overlapping rules for different scenarios? Breaking it up into specialists with narrower prompts is a legitimate way to reduce each prompt to its core job. But if your single-agent prompt is only thirty lines, don't split it just because you can.

---

## Slide 20 — The default

So what should you do when none of the three tests pass? The default is to keep it to one agent with tools. A single well-written agent with eight tools is almost always simpler, cheaper, and faster than a coordinator-plus-specialists architecture doing the same work. Multi-agent is sometimes the right answer — it is just not the right answer by default.

---

## Slide 21 — Next

Up next in module seven, we dig into callbacks as middleware. Six lifecycle hooks wrap every invocation — so `before_agent`, `after_agent`, `before_model`, `after_model`, `before_tool`, and `after_tool`. Return None, and things proceed normally. Return a response object, and you short-circuit the LLM or tool altogether. Think Django middleware, Express middleware, or plugin hooks — but for agents. The blocklist-guardrail demo is small, visual, and really the cleanest example in the course of code-level safety. See you there.
