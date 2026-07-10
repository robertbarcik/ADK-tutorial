# M05 — Speaker notes

---

## Slide 1 — Title

Welcome to module five: workflow agents. This module gives you three ways to compose multiple agents without writing any orchestration code yourself: Sequential, Parallel, and Loop. Named workflows, expressed as Python classes. And we'll build the canonical ADK wow demo: a generator plus a critic in a loop, which is really what people gasp at when they see ADK for the first time. Let's go.

---

## Slide 2 — One agent / Real work

The framing for this module is on the slide. One agent is enough for toy problems, but real work needs composition. That's why we're spending a whole module on workflows. Once you step beyond a single agent, you need a way to wire several of them together without reinventing an orchestrator every time.

---

## Slide 3 — Three first-class primitives

ADK ships three first-class workflow primitives, and between them they cover most of what you'll ever need.

First, SequentialAgent. It runs its children in order, like a shell pipeline. Each child finishes before the next one starts.

Second, ParallelAgent. It runs all children concurrently, like `asyncio.gather`. Whichever finishes first, finishes first.

And third, LoopAgent. It runs children in a cycle until somebody calls the `exit_loop` tool, or the iteration ceiling is hit. Think of it as a while loop with an escape hatch.

This is really ADK's strongest pedagogical differentiator. LangGraph makes you draw your control flow as a node-and-edge graph. CrewAI hides it behind a role-playing DSL. ADK, by contrast, just lets you name the workflow: Sequential, Parallel, Loop. If that reads like Python, that's the point.

---

## Slide 4 — Visual

What you see on this slide is the three primitives side by side. Sequential on the left: children run top to bottom. Parallel in the middle: children run concurrently. And Loop on the right: children cycle until exit.

Same Runner, same event stream, same state dict. Only the composition class changes. Everything else you've learned so far in the course still works.

---

## Slide 5 — State is the pipe

Between children, state is the pipe that carries data from one to the next. Use `output_key="summary"` on a child, and that child's result writes to `state["summary"]`. Then in a later child's instruction, use `{summary}`, with curly braces, and ADK substitutes the value from state before the model ever sees the prompt.

There's also an optional variant: `{summary?}` with a question-mark suffix. That means "substitute if present, leave empty if missing." It's useful for loop iterations where early passes haven't written the key yet.

So the rule is simple. Write with `output_key`, read with curly-brace substitution. That's really the entire orchestration vocabulary for workflow agents.

---

## Slide 6 — SequentialAgent

Let's start with primitive one: SequentialAgent. Ordered pipeline, and state flows downstream.

---

## Slide 7 — A two-step pipeline

Here on the slide we have a two-step pipeline written out. A summarizer agent on top, a translator agent in the middle, and a SequentialAgent at the bottom that wraps them both into one composition.

Walk through how state flows. The summarizer has `output_key="summary"`, which means its result writes to `state["summary"]`. The translator's instruction contains `{summary}`, which means ADK substitutes the value from state before the translator's model sees the prompt. So the translator works on the summary, not on the original user input.

You don't write a for-loop that calls the children. You don't pass state manually between them. The SequentialAgent is the loop, and ADK passes state implicitly through the session.

---

### Notebook break — Sequential pipeline in action

[Switch the screen to the notebook.]

Here's the Sequential pipeline wired up and ready to run. I'll feed it three sentences about a hungry cat. [Run the cell.] Watch the event stream. The summarizer runs first and writes a one-sentence summary into `state["summary"]`. Then the translator picks up, reads the summary out of state through curly-brace substitution, and produces a Slovak translation. Two LLM calls, one composition, no glue code between them.

[Switch back to the slide deck.]

---

## Slide 8 — ParallelAgent

On to primitive two: ParallelAgent. Concurrent fan-out, which means wall time is approximately equal to the slowest child, not the sum of children's durations.

---

## Slide 9 — Three-way fan-out

On the slide we have a three-way fan-out. Three researcher agents, one for Germany, one for Slovakia, one for Czech Republic, each with its own instruction and its own state key. The ParallelAgent at the bottom wraps them together as one composition.

When the ParallelAgent runs, ADK uses asyncio under the hood to fire off all three children concurrently. The pattern is exactly like `asyncio.gather(task_a, task_b, task_c)`, except each task is an LLM agent, and each result lands in its own state slot.

---

### Notebook break — Three researchers in parallel

[Switch the screen to the notebook.]

Here's the parallel trio of researchers we just defined. I'll start a timer and run them. [Run the cell.] Watch the event stream as it scrolls. Notice the authors interleave in whichever order they finish, not the order we declared them. Sometimes `cz_researcher` lands first, sometimes `de_researcher` does. That's concurrency at work. And the timer at the bottom: about one second of wall time, instead of the roughly three seconds you'd see if they ran one after another.

[Switch back to the slide deck.]

---

## Slide 10 — What to notice

Three observations worth calling out from that run.

First, authors interleave in finish order, not declaration order. So when you read events from a parallel run, don't assume any particular ordering.

Second, wall time is one child's duration, not the sum. If each LLM call takes one second, sequential takes three seconds, while parallel takes about one point one. The savings scale with the width of the fan-out.

And third, each child writes to its own state key, so they don't collide. If two children tried to write to the same key, whichever wrote last would win. Don't do that.

A common production pattern is to fan out independent research or lookups in parallel, and then feed the collected state into a sequential synthesizer. We'll build exactly that in a minute.

---

## Slide 11 — LoopAgent

Primitive three is LoopAgent: the canonical ADK wow demo. Generator plus critic, refining until satisfied.

---

## Slide 12 — The pattern

Let me walk through the pattern on the slide. A LoopAgent with two children. The generator writes a draft to state. The critic then reads the draft and decides whether it's good enough. If it's not, the critic writes a critique back to state and the loop continues, so the generator reads the critique on the next pass and revises. If the critic is satisfied, it calls `exit_loop`, which ADK intercepts and terminates the loop.

This pattern has many names in the literature: self-correction, critic-driven refinement, Reflexion, draft-and-review. Whatever you call it, in ADK it's just a LoopAgent with two children.

Without LoopAgent, you'd write a `while True` with an exit condition in Python. With LoopAgent, by contrast, ADK handles the looping, the state passing, the iteration counting, and the exit-signal mechanism. You declare the two children and the max iterations, and ADK runs the pattern.

---

## Slide 13 — The generator

Here on the slide is the generator code. It's an LlmAgent with one job: produce or revise a tagline. Its instruction reads the previous draft and the previous critique out of state, using `{draft?}` and `{critique?}` with the question-mark suffix, because on iteration one neither key exists yet. The instruction says something like: if both exist, revise the draft based on the critique; otherwise, draft from scratch. Output goes to `state["draft"]`.

One subtle but important design rule here. The generator's output is text, so make the instruction really clear that the output should be only the tagline. No preamble, no explanation, no markdown. In workflow compositions, drift in output formatting cascades. If the generator adds "Here's my draft:" as a prefix, the critic then sees that as part of the draft and critiques it. So be strict.

---

## Slide 14 — The critic

On the slide is the critic, plus the LoopAgent that wraps it together with the generator. The critic's instruction reads the current draft out of state and evaluates it against named criteria. If any criterion fails, it writes a one-sentence critique back to state. If all criteria pass, it calls the `exit_loop` tool.

`exit_loop` is imported from `google.adk.tools`. It's a built-in tool that signals to the parent LoopAgent: "we're done." The critic gets it in its `tools=` list. So when the critic's model emits a call to `exit_loop`, ADK catches it and terminates the loop. Clean signal, no magic.

Then there's the LoopAgent itself, at the bottom of the slide. Two children, and max_iterations set to five. That ceiling is important; the next slide unpacks why.

---

### Notebook break — Generator and Critic refining a draft

[Switch the screen to the notebook.]

Now let me run the generator-plus-critic loop. The user asks for a tagline. [Run the cell.] Watch the iterations roll. The generator produces a first draft that contains the word "Master", which violates one of the critic's rules about cliches. The critic flags it in a one-sentence critique. The generator reads that critique on the next pass and revises. This time the critic approves, and you can see the `exit_loop` tool call right there in the event stream with empty arguments. That's the signal that terminates the loop.

[Switch back to the slide deck.]

---

## Slide 15 — What to always do

Three rules to always follow with LoopAgent.

First, always set max_iterations. If the critic is impossible to satisfy, the agent runs forever, and your API bill runs forever with it. Five is usually enough. For reference: I've seen production LoopAgents with max_iterations at ten. I've never seen one higher than twenty.

Second, pair `exit_loop` with the child that has the exit condition: usually the critic, reviewer, or gate-keeper. Don't scatter `exit_loop` across multiple children unless you have a specific reason, because it makes the exit condition really hard to reason about.

And third, use the question-mark syntax for state keys that might not exist yet. `{draft?}` means "substitute if present, empty string if not." Iteration one has no previous draft, so the question mark is what prevents a KeyError.

---

## Slide 16 — Composing workflows

Now let's put it all together. Workflow agents are themselves agents, which means you can nest them inside other workflow agents.

---

## Slide 17 — Parallel inside Sequential

Here on the slide is the classic composition. A SequentialAgent whose first child is a ParallelAgent. So you fan out independent research in parallel as the first step, and then synthesize sequentially as the second step.

Five LLM calls in total: three parallel researchers running concurrently, then one synthesizer that reads all three results out of state. Wall time comes in around two calls' worth, not five. The synthesizer's instruction uses `{germany_fact}`, `{slovakia_fact}`, and `{czech_fact}` to pull all three parallel results from state.

This is really the shape most production agents take. Not one monolithic agent. Not even five children in a flat list. Instead, a pipeline of phases, some parallel within a phase, some sequential across phases.

---

### Notebook break — Composition: parallel inside sequential

[Switch the screen to the notebook.]

Here's the composition we just defined: ParallelAgent inside SequentialAgent. I'll start a timer and run it. [Run the cell.] Watch what happens. Three researchers fire off concurrently, each writing to its own state slot. As soon as all three finish, the synthesizer picks up, reads `{germany_fact}`, `{slovakia_fact}`, and `{czech_fact}` from state, and writes a final report that ties the three together. Total wall time: about two calls' worth, even though there are five LLM calls. The fan-out paid for itself.

[Switch back to the slide deck.]

---

## Slide 18 — Workflow agent vs. LLM-driven flow

The big alternative to workflow agents is letting the LLM decide. You build one agent with all the sub-agents in its `sub_agents=` list, and the model at the top picks which one to call. That's what the next module is about.

Both styles work. But they're not interchangeable.

Use a workflow agent when the control flow is fixed: for example, always summarize, then translate. When you need determinism for tests or evals. When latency matters, because parallel fans out without a deliberation turn. And when the workflow should be auditable from a diagram.

Use LLM-driven, on the other hand, when the control flow depends on user input. When flexibility is the point. When the model's judgment is what actually adds value. And when conversations can go anywhere, and pre-canning the flow would constrain the product.

---

## Slide 19 — The rule of thumb

The rule of thumb is on the slide. If you can name the workflow, use a workflow agent. If you can't, let the LLM decide.

Sequential, Parallel, and Loop cover the named-workflow cases cleanly. Anything more complex, start composing them. And if the composition gets unwieldy, that's a signal the workflow shouldn't be named after all. Let the LLM drive instead.

One more thing worth knowing, and you can see it in the small print on the slide. The 2.0 release of ADK added a graph-based workflow runtime, where agents and tools become nodes in an explicit graph with edges between them. It targets exactly those unwieldy cases, conditional branches and cyclic flows that outgrow composition. For everything in this course, the three template agents remain the right tool, so that is what we build with.

---

## Slide 20 — Up next

Up next, multi-agent hierarchies. That's the LLM-driven alternative to workflow agents. Sub-agents for transfer, and AgentTool for the consultant pattern. We saw a glimpse of AgentTool earlier when we covered tools. Now we'll put it in context against sub-agents, and see when each one is right. See you there.
