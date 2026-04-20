# Workflow agents

Four chapters in, every example has featured one agent doing the work. One agent is enough for toy problems, and nothing more. Real agent software is composition — several agents arranged into pipelines, fan-outs, refinement loops — because the interesting problems never fit one prompt.

This chapter introduces ADK's three first-class composition primitives: `SequentialAgent`, `ParallelAgent`, and `LoopAgent`. Each takes a list of child agents and runs them according to a fixed control-flow pattern. You don't write orchestration code; you name the pattern.

This is the single strongest pedagogical differentiator ADK has against the alternatives. LangGraph asks you to draw control flow as a node-and-edge graph. CrewAI hides it behind a role-playing DSL. ADK lets you *name the workflow*: Sequential, Parallel, Loop. Three Python classes, no graph diagrams, no metaphor.

## The three primitives, at a glance

```
SequentialAgent       ParallelAgent          LoopAgent
─────────────────     ─────────────────      ─────────────────
                                             ┌────────────────┐
   child 1               child 1             │   child 1      │
      │                     │                │      │         │
      ▼                     ▼                │      ▼         │
   child 2       ──>    child 2    <──       │   child 2      │
      │                     │                │      │         │
      ▼                     ▼                │      ▼ (loop)  │
   child 3               child 3             │   child 1 ...  │
                                             └────────────────┘
   ordered              concurrent           until exit_loop
   pipeline             fan-out              or max_iterations
```

Same `Runner`, same event stream, same session state — only the composition class differs. Everything from the first four chapters — tools, events, state prefixes — still applies inside each child.

## State is the pipe

Between children, state is how data flows. Two pieces of syntax do the entire orchestration.

**`output_key="summary"` on a child** — the child's final text is written to `state["summary"]` automatically. This is the same `output_key=` parameter we covered in Module 03; here it takes on a second role as the "output port" of a child in a workflow.

**`{summary}` in a later child's instruction** — ADK substitutes the value from state before the model sees the prompt. The `?` suffix (`{summary?}`) means "substitute if present, empty string if missing." The `?` matters for LoopAgent children that run before the key exists.

Write with `output_key=`. Read with `{key}`. That is the entire orchestration vocabulary for workflow agents.

## SequentialAgent — ordered pipeline

`SequentialAgent` runs children one after another. Child 1 finishes, child 2 starts, and so on. The first child's output is in state by the time the second child runs, so the second child can read it.

```python
summarizer = LlmAgent(
    name="summarizer",
    model=MODEL,
    instruction="Read the user input. Summarize it in one sentence. Output only the summary.",
    output_key="summary",
)

translator = LlmAgent(
    name="translator",
    model=MODEL,
    instruction="Translate this English sentence to Slovak: {summary}. Output only the translation.",
    output_key="translation",
)

pipeline = SequentialAgent(
    name="summarize_then_translate",
    sub_agents=[summarizer, translator],
)
```

Run this on "The cat sat on the mat. It was hungry. It meowed loudly until fed." and you get two state entries: `summary` with a one-sentence condensation, `translation` with that sentence in Slovak. The translator's `{summary}` slot was filled in from state before the model saw the prompt, so the translator worked on the summary rather than the original.

When to reach for SequentialAgent: whenever the workflow is a fixed chain of transformations. Data preparation pipelines. Multi-step research. Any "do X, then do Y with X's result" shape.

## ParallelAgent — concurrent fan-out

`ParallelAgent` runs all children concurrently via `asyncio`, each writing to its own state key. Total wall time is approximately the slowest child, not the sum of children.

```python
de_researcher = LlmAgent(name="de_researcher", ...,
    instruction="State one interesting fun fact about Germany.",
    output_key="germany_fact")
sk_researcher = LlmAgent(name="sk_researcher", ...,
    instruction="State one interesting fun fact about Slovakia.",
    output_key="slovakia_fact")
cz_researcher = LlmAgent(name="cz_researcher", ...,
    instruction="State one interesting fun fact about Czech Republic.",
    output_key="czech_fact")

trio = ParallelAgent(
    name="trio",
    sub_agents=[de_researcher, sk_researcher, cz_researcher],
)
```

Run this and you get three state keys populated. Key properties:

- **Authors interleave in finish order** — cz_researcher might print before de_researcher even though it was declared second. When you read events from a parallel run, don't assume declaration order.
- **Wall time ≈ slowest child.** Three ~1-second LLM calls in parallel take ~1.2 seconds, not 3. The savings scale with the width of the fan-out.
- **Children must write to different state keys.** If two children try to write to the same key, whichever wrote last wins. The framework won't warn you; design your keys to avoid collision.

When to reach for ParallelAgent: whenever you're doing several independent things that don't depend on each other. Calling three APIs. Researching three topics. Running three different evaluators on the same input.

## LoopAgent — the canonical wow demo

The third primitive, and the one people remember. `LoopAgent` runs its children in a cycle until one of them calls the `exit_loop` tool or the `max_iterations` ceiling is reached.

The archetypal pattern is a **Generator + Critic** pair. The generator produces a draft. The critic evaluates it. If the critic isn't satisfied, it writes a critique back to state and the loop continues; on the next iteration, the generator reads the critique and revises. When the critic is satisfied, it calls `exit_loop` and the loop terminates.

This pattern has many names — *self-correction*, *critic-driven refinement*, *reflexion*, *draft-and-review*. In a plain agent framework you'd implement it as:

```python
# The manual version
state = {"draft": None, "critique": None}
for i in range(5):
    state["draft"] = await generator.run(state)
    state["critique"] = await critic.run(state)
    if critic_is_satisfied(state["critique"]):
        break
```

In ADK it's a `LoopAgent` with two children. The framework handles the looping, the state passing, the iteration counting, and the exit-signal mechanism.

```python
from google.adk.tools import exit_loop

generator = LlmAgent(
    name="generator",
    model=MODEL,
    instruction="""Write or revise a tagline. If a previous draft and critique
exist, revise to address the critique. Otherwise, draft fresh.

Previous draft:    {draft?}
Previous critique: {critique?}

Output ONLY the new tagline.""",
    output_key="draft",
)

critic = LlmAgent(
    name="critic",
    model=MODEL,
    instruction="""Draft: {draft}

If the draft FAILS any criterion, write a one-sentence critique.
If the draft PASSES all criteria, call exit_loop. Do NOT output text.""",
    output_key="critique",
    tools=[exit_loop],
)

refiner = LoopAgent(
    name="tagline_refiner",
    sub_agents=[generator, critic],
    max_iterations=5,   # always set
)
```

Three things worth flagging in the code:

**The `?` suffix on `{draft?}` and `{critique?}`.** Iteration 1 has no previous draft and no previous critique. Without the `?`, ADK would throw a KeyError when it tried to substitute the template. With it, the template substitutes to an empty string.

**`exit_loop` is a built-in tool.** You import it from `google.adk.tools` and give it to whichever child has the authority to terminate the loop — usually the critic or reviewer. When the critic's model emits a `function_call` to `exit_loop`, ADK catches it and stops iteration.

**`max_iterations=5` is the safety net.** If the critic is impossible to satisfy, the loop runs forever — and so does your API bill. Always set this. In practice I've seen production LoopAgents set to 5 or 10; I've never seen one set higher than 20.

### The event stream of a running Loop

When you run the generator-critic loop, here's the shape of what you see:

```
USER: Write a tagline.

[generator] Build secure, high-performance Android applications with the
           Google ADK. Master device integration and data management.
[critic]    The draft uses the marketing cliche "Master," which the
           criterion rejects.
[generator] Develop secure, high-performance Android applications using the
           Google ADK. Handle device integration and data management.
[tool_call] exit_loop({})
```

Two iterations. The critic rejected "Master" as a cliche. The generator revised. The critic approved and called `exit_loop`. The loop terminated.

In production you'd want the critic to be stricter about cliches and the generator to push toward specific, vivid language. The demo here shows the mechanism; the prompt engineering is the separate craft of making the loop converge on something actually good.

## Composing workflows

Workflow agents are themselves agents. You can nest them — put a `ParallelAgent` as a child of a `SequentialAgent`, put a `SequentialAgent` inside a `LoopAgent`, and so on.

The most useful composition in practice: **fan out independent work in parallel, then synthesize sequentially.**

```python
synthesizer = LlmAgent(
    name="synthesizer",
    model=MODEL,
    instruction="""You have three country facts in session state.
Write a short 3-sentence combined report connecting them thematically.

Germany: {germany_fact}
Slovakia: {slovakia_fact}
Czech Republic: {czech_fact}

Output only the report.""",
    output_key="report",
)

pipeline = SequentialAgent(
    name="research_pipeline",
    sub_agents=[
        trio,           # ParallelAgent from earlier
        synthesizer,    # reads all three parallel results from state
    ],
)
```

Five LLM calls total — three parallel researchers, then one synthesizer. Wall time comes in around two calls' worth, not five. Production agents are built out of compositions like this. Not one monolithic agent. Not a flat list of five children. A pipeline of phases, some parallel within a phase, some sequential across phases.

## When to use workflow agents vs. LLM-driven flow

The alternative to workflow agents is **LLM-driven flow**: build one agent with several sub-agents in its `sub_agents=` list, let the model decide which to transfer control to. Module 06 covers this in depth.

Both styles work. They are not interchangeable.

| Use a **workflow agent** when... | Use **LLM-driven flow** when... |
|---|---|
| The control flow is fixed — always summarize, then translate | The control flow depends on user input |
| You need determinism for tests or evals | You need flexibility |
| Latency matters — Parallel fans out without a deliberation turn | The model's judgment is the point |
| The workflow should be auditable from a diagram | The conversation can go anywhere |

**The rule of thumb:** if you can *name* the workflow, use a workflow agent. If you can't, let the LLM decide.

Sequential, Parallel, Loop cover the named-workflow cases cleanly. Most compositions are either purely these three, or a mix of workflow agents and LLM-driven top levels. If your composition gets unwieldy, that's usually a signal that the workflow shouldn't be named — let the LLM drive.

## What to carry forward

- **Three workflow primitives:** `SequentialAgent` (ordered pipeline), `ParallelAgent` (concurrent fan-out), `LoopAgent` (cycle until `exit_loop` or `max_iterations`).
- **State is the pipe.** `output_key="foo"` writes to state; `{foo}` in a later instruction reads. `{foo?}` is "optional, don't error if missing."
- **Always set `max_iterations`** on a LoopAgent. The critic might be impossible to satisfy.
- **`exit_loop`** is a built-in tool; give it to the child with the exit condition (usually the critic).
- **Compose freely.** Workflow agents are agents; they nest. Parallel-inside-Sequential is the classic production shape.
- **Name it if you can.** If you can name the workflow, use a workflow agent. If you can't, that's what M06 is for — LLM-driven routing.

Module 06 picks up where this one leaves off. Where workflow agents give you control flow by declaration, `sub_agents` and `AgentTool` give you control flow driven by the LLM's judgment. Two patterns, different trade-offs, same underlying machinery.
