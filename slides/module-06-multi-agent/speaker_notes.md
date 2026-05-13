# M06 — Speaker notes

---

## Slide 1 — Title

Welcome to module six: multi-agent hierarchies. This is the module where the LLM itself decides which agent handles the user's request. When the user's input is what determines which specialist runs, you don't want a workflow agent. You want the LLM at the top to route. ADK has two patterns for exactly this, and they look similar on the surface but behave very differently. Today we pull them apart.

---

## Slide 2 — Three ways to combine agents

There are three ways in total to compose agents in ADK, and it's worth naming all three up front so you see where today fits.

First, workflow agents. Declarative control flow with named primitives: Sequential, Parallel, and Loop. You name the workflow, the framework runs the pattern. Use them when you can name the workflow.

Second, sub-agents. LLM-driven routing via transfer. The coordinator's LLM picks which specialist should take over, and ADK hands off control.

And third, AgentTool. LLM-driven routing via function call. The coordinator picks which specialist to call, the specialist runs, and the coordinator stays in charge.

Today we focus on the two LLM-driven patterns, side by side.

---

## Slide 3 — The one question

The whole module comes down to one question, and you can see it on the slide. After the specialist finishes its work, who is in charge of the conversation? If the specialist is, you want `sub_agents`. If the coordinator is, you want `AgentTool`. That's the entire decision. Everything else is just mechanics.

---

## Slide 4 — sub_agents: the org-chart transfer

On to pattern one: `sub_agents`, the org-chart transfer.

---

## Slide 5 — How sub_agents works

Let me walk through the mechanics. You give the coordinator a `sub_agents=` list, and ADK detects this and automatically injects a built-in tool called `transfer_to_agent`. You don't register it; it's just there for you.

When the coordinator's model reads the user's message and decides a specialist fits, it emits a structured call, something like `transfer_to_agent(agent_name='weather_specialist')`. ADK catches that call and routes control to the named child. The child then runs, produces a response, and that response is what the user sees.

After the transfer, the child remains the active agent for the rest of the session by default. So if the user sends a follow-up, it goes to the specialist, not back to the coordinator. In other words, the specialist owns the conversation from that point on.

Think of it as an org chart. The coordinator is the manager reading the inbox; the specialist takes the meeting.

One production-sensitive detail worth flagging: the child's `description=` field is what the coordinator's LLM reads to decide whether to route there. So write descriptions for the model, not for a human reviewer. "Handles greetings" is fine; "Agent that greets users warmly and makes them feel welcome" is just noise.

---

## Slide 6 — sub_agents in code

Here on the slide we have the sub_agents pattern in code. Two specialists at the top, each with a name, a description (which is really the routing schema), and its own instruction. Then a coordinator at the bottom that has both specialists in its `sub_agents=` list. And that's it. No routing code, because ADK handles the transfer mechanism for you.

---

### Notebook break — Transfer routing in action

[Switch the screen to the notebook.]

Here's the coordinator and its two specialists wired up. I'll send a greeting first. [Run the cell.] Watch the event stream. The coordinator's model emits a `transfer_to_agent` call with `agent_name='greeter'`, and ADK routes. The greeter produces the final response, and that response is what the user sees. Now a weather question. [Run the next cell.] Same shape, different routing target: `transfer_to_agent(agent_name='weather_specialist')`. The weather specialist takes over and produces the answer.

[Switch back to the slide deck.]

---

## Slide 7 — The event stream

Here on the slide is the same event stream as a static reference. The coordinator emitted `transfer_to_agent` with `agent_name='weather_specialist'`. ADK routed. The weather specialist produced the final response.

The key thing to notice is the author of that final response. It's the specialist, not the coordinator. That's the tell that this is a transfer pattern.

---

## Slide 8 — AgentTool: the consultant pattern

On to pattern two: `AgentTool`, the consultant pattern.

---

## Slide 9 — How AgentTool works

Same team, just different wiring. Instead of putting the specialists in `sub_agents=`, you wrap each one in `AgentTool(agent=...)` and put them in the coordinator's `tools=` list.

Now, to the coordinator's LLM, the specialists look like tools. No different from a FunctionTool, an OpenAPI tool, or an MCP tool. When the coordinator decides to use a specialist, it emits a regular function call, the same mechanism that triggers `get_weather` or `search_tickets` for other tool types.

ADK then runs the specialist as a fresh LLM call. The specialist produces its output. That output comes back to the coordinator as a tool-response event. The coordinator reads it, and produces the final user-facing reply itself.

So the specialist never gets the microphone. It answers a structured question, hands the result back, and the coordinator speaks on its behalf.

---

## Slide 10 — AgentTool in code

Here on the slide we have the same two specialists from before, but now wrapped in `AgentTool` and placed in the coordinator's `tools=` list, not `sub_agents=`. That single word difference in the constructor is really the whole behavioral difference between the two patterns.

---

### Notebook break — Consultant calls in action

[Switch the screen to the notebook.]

Here's the same team, this time wired up as AgentTool consultants. Same prompts as before. Greeting first. [Run the cell.] Watch what's different in the event stream this time. The coordinator emits a tool call, but the tool is `greeter`, the specialist. The specialist returns its output as a tool-response event. And then the coordinator, not the specialist, produces the final reply to the user. Now the weather question. [Run the next cell.] Same shape: coordinator calls `weather_specialist` as a tool, gets the response, and writes the final user-facing reply itself.

[Switch back to the slide deck.]

---

## Slide 11 — The event stream: note the author

Here on the slide is the same event stream from the consultant pattern, laid out for reference. The coordinator called `weather_specialist` as a tool. A tool-response event came back with the result. And then the coordinator, not the specialist, produced the final reply to the user.

That's the consultant pattern in action. The specialist answered a specific question and stepped back, while the coordinator stayed in charge of speaking to the user.

---

## Slide 12 — The tell-tale sign

Here's the tell-tale sign on one slide. Look at the author of the final response.

If the specialist is the author, you're looking at a transfer, which means the sub_agents pattern.

If the coordinator is the author, you're looking at a consultant call, which means the AgentTool pattern.

That's the diagnostic. Print the event stream, read the last author, and you know which pattern is in use.

---

## Slide 13 — When to pick which

So when should you pick which? Let me give you four markers for each side.

Use sub_agents, the transfer pattern, when the specialist should own the dialog. When the specialist might take multiple turns with the user before handing back. When a topic shift means the specialist is really the right conversation partner for that whole topic. And when you want the user to perceive they're talking to a specialist.

Use AgentTool, the consultant pattern, when the specialist answers one question and steps back. When the specialist has a clean input-output contract. When the coordinator needs to compose the specialist's output with other sources, like multiple tools or other specialists. And when you want the user to perceive they're talking to one assistant that just has specialists behind the scenes.

---

## Slide 14 — Concrete examples

Let me ground those rules with two concrete examples.

First, a sub_agents scenario. Imagine an IT support desk with a billing specialist and a hardware specialist. The user says "my laptop won't boot." The coordinator routes to hardware. Over the next five turns of the session, the hardware specialist walks the user through diagnosis: power, connections, BIOS, boot order. That's an extended conversation the coordinator shouldn't mediate. So you transfer once, and let the specialist handle the whole topic.

Now an AgentTool scenario. Think of a coding assistant whose orchestrator wraps a specialist code-analyzer, a specialist docs-lookup, and a specialist test-runner. The user asks "why is my test failing?" The orchestrator decides all three specialists are relevant, calls all three in one turn, reads their three tool-responses, and synthesizes one answer. Each specialist contributes a single structured response, and the orchestrator owns the composition.

---

## Slide 15 — Multi-Agent Decomposition

Time for a quick interlude from the Agentic Design Patterns publication, chapter eight, on multi-agent decomposition. Some theory on when multi-agent architectures pay for their coordination tax, and just as importantly, when they don't.

---

## Slide 16 — The coordination tax

Multi-agent architectures are fashionable. They're also expensive. Before you decompose a task into specialists, you have to consider the coordination tax, and it has three parts.

First, extra LLM calls. Every transfer, and every AgentTool call, is an additional model invocation. A two-specialist system makes at least two calls per user turn: one to route, one to resolve. A five-specialist system can make ten or more. This compounds latency and cost in production.

Second, routing errors. Every routing decision is a chance to pick the wrong specialist. The more specialists you have, the wider the miss surface. You have to design descriptions carefully enough that the coordinator's LLM never gets confused, and when it inevitably does, your testing has to catch it.

And third, context fragmentation. Each child has its own system prompt, which means information you put in the coordinator's instruction does not automatically reach the children. Specialists sometimes fail because they lack context the coordinator had. In a monolithic single agent, this problem simply doesn't exist; there's just one prompt.

---

## Slide 17 — Three tests before you decompose

The publication gives you three tests to apply before you decompose.

First, the reuse test. Will any of these specialists be used elsewhere, by a different top-level agent, in a different product, or by a different team? If yes, decomposition makes sense, because the specialists become reusable components. If no, consider staying with one agent and just adding more tools.

Second, the model-heterogeneity test. Does each specialist benefit from a different model? Cheap routing decisions on Haiku, hard resolutions on Opus, that mix is only possible if you decompose. But if all your specialists use the same model anyway, the decomposition buys you less.

And third, the instruction-scale test. Is a single system prompt getting unmanageable, say five hundred lines, with overlapping rules for different scenarios? Breaking it up into specialists with narrower prompts is a legitimate way to reduce each prompt to its core job. But if your single-agent prompt is only thirty lines, don't split it just because you can.

---

## Slide 18 — The default

So what should you do when none of the three tests pass? The default is to keep it to one agent with tools. A single well-written agent with eight tools is almost always simpler, cheaper, and faster than a coordinator-plus-specialists architecture doing the same work. Multi-agent is sometimes the right answer. It is just not the right answer by default.

---

## Slide 19 — Up next

Up next, callbacks as middleware. Six lifecycle hooks wrap every invocation: `before_agent`, `after_agent`, `before_model`, `after_model`, `before_tool`, and `after_tool`. Return `None`, and things proceed normally. Return a response object, and you short-circuit the LLM or tool altogether. Think Django middleware, Express middleware, or plugin hooks, but for agents. The blocklist-guardrail demo is small, visual, and really the cleanest example in the course of code-level safety. See you there.
