# Multi-agent hierarchies

Chapter 05 gave you workflow agents — named, declarative control flow. `SequentialAgent`, `ParallelAgent`, `LoopAgent`. You use them when you can name the workflow: "always summarize, then translate," "always fan out these three researchers," "always refine with critic feedback."

This chapter gives you the other half. **LLM-driven** control flow. When the user's input decides which specialist runs, you don't want a workflow agent. You want the LLM to route. ADK has two patterns for this.

They look superficially similar. Both let the LLM decide which specialist fires next. They behave very differently once you pay attention to who is in charge of the conversation *after* the specialist finishes.

- **`sub_agents`** — the coordinator *transfers* control to a specialist. The specialist owns the conversation. Call it the **org-chart** pattern.
- **`AgentTool`** — the coordinator *calls* a specialist like a function. The coordinator stays in charge. Call it the **consultant** pattern.

By the end of this chapter the same coordinator-plus-two-specialists team will be wired up both ways. The user's final-facing output looks identical; the event stream tells you which pattern is running.

## The one question that separates them

There is exactly one meaningful difference between `sub_agents` and `AgentTool`. Memorize it now; everything else is mechanics.

**Who is in charge of the conversation after the specialist finishes?**

If the specialist is — use `sub_agents`. If the coordinator is — use `AgentTool`. That's the whole decision.

## Pattern 1 — `sub_agents`: the org-chart transfer

The coordinator has a list of children in its `sub_agents=` parameter. ADK automatically injects a built-in tool called `transfer_to_agent` — you don't register it, it's just there whenever `sub_agents=` is set.

When the coordinator's LLM reads the user's message and decides a specialist is more appropriate, it emits a structured call: `transfer_to_agent(agent_name='weather_specialist')`. ADK catches that call and routes control to the named child. The child runs, produces a response, and **the child's response is what the user sees**.

After the transfer, the child remains the active agent for the rest of the session by default. If the user sends a follow-up, it goes to the specialist — not back to the coordinator. The specialist owns the conversation from that point, unless it itself transfers again.

```python
greeter = LlmAgent(
    name="greeter",
    model=MODEL,
    description="Handles greetings and casual chat.",
    instruction="Respond warmly in one short sentence.",
)

weather_specialist = LlmAgent(
    name="weather_specialist",
    model=MODEL,
    description="Handles weather questions for any city.",
    instruction="Produce a plausible one-sentence weather report.",
)

coordinator = LlmAgent(
    name="coordinator",
    model=MODEL,
    description="Routes user queries to specialists.",
    instruction="Delegate greetings to greeter, weather questions to weather_specialist.",
    sub_agents=[greeter, weather_specialist],   # ← the org chart
)
```

One production-sensitive detail: **the child's `description=` field is what the coordinator's LLM reads to decide routing.** Write descriptions for the model, not for a human reviewer. Ambiguous descriptions produce ambiguous routing.

### The event stream of a transfer

```
USER: What's the weather in Prague?

[coordinator_subagents] → transfer_to_agent({'agent_name': 'weather_specialist'})
[weather_specialist]    The weather in Prague is partly cloudy with a gentle
                        breeze and a temperature of 15 degrees Celsius.
                        ^^^ final response comes from the SPECIALIST
```

Two observations. The coordinator emitted `transfer_to_agent` as a tool call; ADK caught it and routed. And the final response's author is `weather_specialist`, not `coordinator`. That is the tell-tale sign of the transfer pattern.

## Pattern 2 — `AgentTool`: the consultant pattern

Same team, different wiring. Instead of placing the specialists in `sub_agents=`, you wrap each as an `AgentTool` and put them in the coordinator's `tools=` list.

Now — from the coordinator's LLM's perspective — the specialists look like **tools**. No different from a `FunctionTool`, an `OpenAPIToolset` entry, an MCP-server tool. When the coordinator decides a specialist is needed, it emits a regular function call. ADK runs the specialist, captures its output as a tool-response event, and feeds that back to the coordinator. **The coordinator reads the response and produces the final user-facing reply itself.**

```python
from google.adk.tools.agent_tool import AgentTool

coordinator = LlmAgent(
    name="coordinator",
    model=MODEL,
    instruction=(
        "You have exactly two tools: `greeter` and `weather_specialist`. "
        "Call one of them per user message; wrap their result in your own reply."
    ),
    tools=[
        AgentTool(agent=greeter),
        AgentTool(agent=weather_specialist),
    ],
)
```

Specialists in `tools=`, not `sub_agents=`. That single-word difference in the constructor is the whole behavioral difference.

### The event stream of a consultant call

```
USER: What's the weather in Prague?

[coordinator_tools] → weather_specialist({'request': 'Prague'})
[tool_resp]            {'result': 'Prague will experience partly cloudy skies
                        with a high of 18 degrees Celsius today.'}
[coordinator_tools]    The weather in Prague will be partly cloudy with a
                        high of 18 degrees Celsius today.
                        ^^^ final response comes from the COORDINATOR,
                            wrapping the specialist's output
```

Same user input. Same team. Different final-response author. The coordinator called the specialist like a function, got the result, and produced the reply itself — wrapping the specialist's output in its own voice.

## The diagnostic

To tell which pattern is running, look at the author of the final response.

- **Specialist → transfer** (`sub_agents`).
- **Coordinator → consultant** (`AgentTool`).

Print the event stream, read the last author, you know which pattern is in use.

## When to pick which

| Use `sub_agents` (transfer) when... | Use `AgentTool` (consultant) when... |
|---|---|
| The specialist should **own the conversation** after routing | The specialist should **answer one question and step back** |
| The child might take **multiple turns** with the user before handing back | The child has a clean **input/output contract** |
| **Topic shifts** — the specialist is the right partner for the whole topic | The coordinator needs to **compose** the specialist's output with other sources |
| User **perceives** talking to a specialist | User **perceives** one assistant with specialists behind the scenes |

**Rule:** if the specialist's work is part of a larger answer that incorporates other information, use `AgentTool`. If the specialist's work *is* the answer, use `sub_agents`.

Two concrete examples to ground the rule.

**`sub_agents` scenario — IT support desk.** Billing specialist and hardware specialist. User says "my laptop won't boot." Coordinator routes to hardware. Over the next five turns of the session, the hardware specialist walks the user through diagnosis — power, cables, BIOS, boot order. That's an extended conversation the coordinator shouldn't mediate. Transfer once; let the specialist own the topic.

**`AgentTool` scenario — coding assistant.** Orchestrator wraps a code-analyzer specialist, a docs-lookup specialist, and a test-runner specialist. User asks "why is my test failing?" The orchestrator decides all three are relevant, calls all three in one turn, reads their three tool-responses, synthesizes one answer. Each specialist contributes a single structured response; the orchestrator owns composition.

## Interlude — Multi-agent decomposition

*From "Agentic Design Patterns," Chapter 8. Two minutes on when to build multi-agent architectures — and when not to.*

Multi-agent architectures are fashionable. They are also expensive. Before you decompose a task into several specialists, consider whether the **coordination tax** is worth paying.

The tax has three parts:

1. **Extra LLM calls.** Every transfer, every `AgentTool` call, is an additional model invocation. A two-specialist system makes at least two calls per turn. A five-specialist system can make ten or more. This compounds latency and API cost in production in ways that don't show up in a demo notebook.
2. **Routing errors.** Every routing decision is a chance to pick the wrong specialist. The more specialists, the wider the miss surface. You must design descriptions carefully and evaluate routing accuracy separately from answer accuracy.
3. **Context fragmentation.** Each child has its own system prompt. Information you put in the coordinator doesn't automatically reach the children. Specialists fail sometimes because they lack context the coordinator had.

The publication proposes three tests before you decompose.

### Test 1 — Reuse

Will any of the specialists be used elsewhere — by a different top-level agent, in a different product, by a different team? If yes, decomposition is worth it — the specialists become reusable components with independent interfaces. If no, consider keeping everything in one agent with more tools.

### Test 2 — Model heterogeneity

Does each specialist benefit from a different model? Cheap routing decisions on Haiku, hard resolutions on Opus — that mix is only possible if you decompose. If all your specialists would use the same model anyway, the decomposition buys you less; the main win evaporates.

### Test 3 — Instruction scale

Is a single system prompt getting unmanageable — five hundred lines with overlapping rules for different scenarios? Breaking it up into specialists with narrower prompts is a legitimate way to reduce each prompt to its core job. But if your single-agent prompt is thirty lines, don't split it for sport.

### If none of the three tests pass

**Keep it to one agent with tools.** A single well-written agent with eight tools is almost always simpler, cheaper, and faster than a coordinator-plus-specialists architecture doing the same work. Multi-agent is sometimes the right answer. It is not the right answer by default.

This is the most important takeaway from the chapter, and the one most commonly missed: multi-agent architectures are a means, not an end. The pattern only earns its complexity when at least one of the three tests passes.

## What to carry forward

- **`sub_agents` is the transfer pattern.** Coordinator's LLM emits `transfer_to_agent(name=...)`; ADK routes; the specialist owns the response.
- **`AgentTool` is the consultant pattern.** Coordinator calls a specialist like a function; the coordinator composes the final reply.
- **The diagnostic:** final-response author = specialist → transfer; coordinator → consultant.
- **Child's `description=`** is the routing schema the coordinator's LLM reads. Write descriptions for the model.
- **Multi-agent decomposition has a coordination tax.** Decompose only when the reuse, model-heterogeneity, or instruction-scale tests pass.
- **Default:** one agent with tools. Multi-agent is a deliberate choice.

Module 07 picks up callbacks. Six lifecycle hooks — `before_agent`, `after_agent`, `before_model`, `after_model`, `before_tool`, `after_tool` — that let you intercept, log, transform, or short-circuit any step in an agent's lifecycle. It is the cleanest mechanism in the framework for guardrails, caching, PII redaction, and per-agent-specific cross-cutting concerns.
