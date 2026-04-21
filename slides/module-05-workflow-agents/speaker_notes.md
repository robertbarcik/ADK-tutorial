# M05 — Speaker notes

---

## Slide 1 — Title

Welcome to module five — workflow agents. Four modules in, every demo we've built has had exactly one agent doing the work. That's fine for toy problems, but real work needs composition. This module gives you three ways to compose agents without writing any orchestration code yourself — Sequential, Parallel, and Loop. Named workflows, expressed as Python classes. And then we'll build the canonical ADK wow demo — a generator plus a critic in a loop, which is really what people gasp at when they see ADK for the first time. Let's go.

---

## Slide 2 — One / Real

The framing for this module is this. One agent is enough for toy problems, but real work needs composition. That's why we're spending a whole module on workflows — because once you step beyond a single agent, you need a way to wire several of them together without reinventing an orchestrator every time.

---

## Slide 3 — Three primitives

ADK ships three first-class workflow primitives, and between them they cover most of what you'll ever need.

First, SequentialAgent. It runs its children in order, like a shell pipeline — so each child finishes before the next one starts.

Second, ParallelAgent. It runs all children concurrently, like `asyncio.gather`. Whichever finishes first, finishes first.

And third, LoopAgent. It runs children in a cycle until somebody calls the `exit_loop` tool, or the iteration ceiling is hit. Think of it as a while loop with an escape hatch.

This is really ADK's strongest pedagogical differentiator. LangGraph makes you draw your control flow as a node-and-edge graph. CrewAI hides it behind a role-playing DSL. ADK, on the other hand, just lets you name the workflow — Sequential, Parallel, Loop. If that reads like Python, that's the point.

---

## Slide 4 — Visual

What you see on this slide is the three primitives side by side. Sequential on the left — children run top to bottom. Parallel in the middle — children run concurrently. And Loop on the right — children cycle until exit.

Same Runner, same event stream, same state dict. Only the composition class changes. Everything else you've learned for the last four modules still works.

---

## Slide 5 — State is the pipe

Between children, state is the pipe that carries data from one to the next. Use `output_key="summary"` on a child, and that child's result writes to `state["summary"]`. Then in a later child's instruction, use `{summary}` — curly braces — and ADK substitutes the value from state before the model ever sees the prompt.

There's also an optional variant — `{summary?}` with a question mark. That means "substitute if present, leave empty if missing." It's useful for loop iterations where early passes haven't written the key yet.

So the rule is simple — write with `output_key`, read with curly-brace substitution. That's really the entire orchestration vocabulary for workflow agents.

---

## Slide 6 — SequentialAgent header

Let's start with primitive one — SequentialAgent. Ordered pipeline, and state flows downstream.

---

## Slide 7 — Two-step pipeline code

A two-step pipeline looks like this. A summarizer with `output_key="summary"` writes to state. A translator with `{summary}` in its instruction reads from state. You wire them into a SequentialAgent, give it a name, and you're done.

You don't write a for-loop that calls the children. You don't pass state manually between them. The SequentialAgent is the loop, and ADK passes state implicitly through the session.

---

## Slide 8 — Live: Sequential

Switch to the notebook — cell nine. We pass in three sentences about a hungry cat. The summarizer condenses them into one. The translator then reads the summary out of state and returns Slovak. So that's two LLM calls, one composition, and no glue code between them.

---

## Slide 9 — ParallelAgent header

On to primitive two — ParallelAgent. Concurrent fan-out, which means wall time is approximately equal to the slowest child, not the sum of children.

---

## Slide 10 — Three-way fan-out code

A three-way fan-out looks like this. Three researchers, each with a different instruction, each writing to a different state key. Wire them into a ParallelAgent, and ADK uses asyncio under the hood to run them concurrently.

The pattern is exactly like `asyncio.gather(task_a, task_b, task_c)` — except each task is an LLM agent, and each result lands in its own state slot.

---

## Slide 11 — Live: Parallel

Switch to the notebook — cell twelve. Three researchers, one timer. Notice the authors interleave in finish order — so `cz_researcher` might print before `de_researcher`, even though we declared it second. That's just concurrency at work. And as a result, the wall time is about one second, not three.

---

## Slide 12 — What to notice

Three observations worth calling out from that run.

First, authors interleave in finish order, not declaration order. So when you read events from a parallel run, don't assume ordering.

Second, wall time is one child's duration, not the sum. If each LLM call takes one second, sequential takes three seconds, while parallel takes about one point one. The savings scale with the width of the fan-out.

And third, each child writes to its own state key, so they don't collide. If two children tried to write to the same key, whichever wrote last would win — so don't do that.

A common production pattern is to fan out independent research or lookups in parallel, and then feed the collected state into a sequential synthesizer. We'll build exactly that in a minute.

---

## Slide 13 — LoopAgent header

Primitive three is LoopAgent — the canonical ADK wow demo. Generator plus critic, refining until satisfied.

---

## Slide 14 — The pattern

Let me walk through the pattern. A LoopAgent with two children. The generator writes a draft to state. The critic then reads the draft and decides whether it's good enough. If it's not, the critic writes a critique back to state and the loop continues — so the generator reads the critique on the next pass and revises. If the critic is satisfied, it calls `exit_loop`, which ADK intercepts and terminates the loop.

This pattern has many names in the literature — self-correction, critic-driven refinement, Reflexion, draft-and-review. Whatever you call it, in ADK it's just a LoopAgent with two children.

Without LoopAgent, you'd write a `while True` with an exit condition in Python. With LoopAgent, on the other hand, ADK handles the looping, the state passing, the iteration counting, and the exit-signal mechanism. You just declare the two children and the max iterations, and ADK runs the pattern.

---

## Slide 15 — The generator

Think about the generator first. Its instruction reads the previous draft and previous critique from state — using `{draft?}` and `{critique?}` with the question mark, because on iteration one neither exists yet. The instruction says something like: if both exist, revise; otherwise, draft from scratch. Output goes to `state["draft"]`.

One subtle but important design rule here. The generator's output is text, so make the instruction really clear that the output should ONLY be the tagline — no preamble, no explanation, no markdown. In workflow compositions, drift in output formatting cascades. For example, if the generator adds "Here's my draft:" as a prefix, the critic then sees that as part of the draft and critiques it. So be strict.

---

## Slide 16 — The critic

Now for the critic. Its instruction reads the current draft and evaluates it against named criteria. If any criterion fails, it writes a one-sentence critique to state. If all criteria pass, it calls the `exit_loop` tool.

`exit_loop` is imported from `google.adk.tools`. It's a built-in tool that signals to the parent LoopAgent — "we're done." The critic gets it in its `tools=` list. So when the critic's model emits a call to `exit_loop`, ADK catches it and terminates the loop. Clean signal, no magic.

And then the LoopAgent itself. Two children, max_iterations equals five. Always set max_iterations. If your critic is impossible to satisfy, the loop runs forever — and your API bill runs forever with it. Five is usually enough. If the critic can't be satisfied in five rounds, it probably can't be satisfied at all.

---

## Slide 17 — Live: Loop

Over in cell fifteen of the notebook, the user asks for a tagline. Watch the iterations. The generator produces a draft with the word "Master," which violates the cliche rule. The critic flags it. The generator revises. The critic approves. `exit_loop` fires. And you'll see it in the event stream as a tool call to `exit_loop` with empty arguments.

---

## Slide 18 — What to always do

Three rules to always follow with LoopAgent.

First, always set max_iterations. If the critic is impossible to satisfy, the agent runs forever. Five is usually enough. For reference — I've seen production LoopAgents with max_iterations at ten. I've never seen one higher than twenty.

Second, pair `exit_loop` with the child that has the exit condition — usually the critic, reviewer, or gate-keeper. Don't scatter `exit_loop` across multiple children unless you have a specific reason, because it makes the exit condition really hard to reason about.

And third, use the question-mark syntax for state keys that might not exist yet. `{draft?}` means "substitute if present, empty string if not." Iteration one has no previous draft, so the question mark is what prevents a KeyError.

---

## Slide 19 — Composing workflows header

Now let's put it all together. Workflow agents are themselves agents, which means you can nest them inside other workflow agents.

---

## Slide 20 — Parallel inside Sequential

The classic composition looks like this — a SequentialAgent whose first child is a ParallelAgent. So you fan out independent research in parallel, and then synthesize sequentially.

Five LLM calls in total — three parallel researchers, and then one synthesizer that reads all three results. Wall time comes in around two calls' worth, not five. The synthesizer's instruction uses `{germany_fact}`, `{slovakia_fact}`, and `{czech_fact}` to read all three parallel results from state.

This is really the shape most production agents take. Not one monolithic agent. Not even five children in a flat list. Instead, a pipeline of phases — some parallel within a phase, some sequential across phases.

---

## Slide 21 — Live: composition

Over in cell eighteen, we run parallel researchers followed by a sequential synthesizer. The final report connects the three facts thematically.

---

## Slide 22 — Workflow vs LLM-driven

The big alternative to workflow agents is letting the LLM decide. You build one agent with all the sub-agents in its `sub_agents=` list, and the model at the top picks which one to call. That's what module six will cover.

Both styles work. But they're not interchangeable.

Use a workflow agent when the control flow is fixed — for example, always summarize, then translate. Use one when you need determinism for tests or evals. When latency matters, because parallel fans out without a deliberation turn. And when the workflow should be auditable from a diagram.

Use LLM-driven, on the other hand, when the control flow depends on user input. When flexibility is the point. When the model's judgment is what actually adds value. And when conversations can go anywhere, and pre-canning the flow would constrain the product.

---

## Slide 23 — The rule

So the rule of thumb, on one slide, is this. If you can name the workflow, use a workflow agent. If you can't, let the LLM decide.

Sequential, Parallel, and Loop cover the named-workflow cases cleanly. Anything more complex, start composing them. And if the composition gets unwieldy, that's a signal the workflow shouldn't be named after all — so let the LLM drive.

---

## Slide 24 — Next

Up next is module six — multi-agent hierarchies. That's the LLM-driven alternative to workflow agents. Sub-agents for transfer, and AgentTool for the consultant pattern — we saw a glimpse of AgentTool back in module two. Now we'll put it in context against sub-agents, and see when each one is right. See you there.
