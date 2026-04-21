# M05 — Speaker notes

---

## Slide 1 — Title

Module five. Workflow agents. Four modules in, every demo has had exactly one agent doing the work. That's fine for toy problems. Real work needs composition. This module gives you three ways to compose agents without writing orchestration code yourself — Sequential, Parallel, Loop. Named workflows as Python classes. And the canonical ADK wow demo — a generator plus critic in a loop, which is what people gasp at when they see ADK for the first time.

---

## Slide 2 — One / Real

One agent is enough for toy problems. Real work needs composition. That's the frame.

---

## Slide 3 — Three primitives

ADK ships three first-class workflow primitives.

SequentialAgent runs its children in order, like a shell pipeline. Each child finishes before the next starts.

ParallelAgent runs all children concurrently, like `asyncio.gather`. Whichever finishes first finishes first.

LoopAgent runs children in a cycle until somebody calls the `exit_loop` tool or the iteration ceiling is hit. A while loop with an escape hatch.

This is ADK's strongest pedagogical differentiator. LangGraph makes you draw your control flow as a node-and-edge graph. CrewAI hides it behind a role-playing DSL. ADK just lets you name the workflow: Sequential, Parallel, Loop. If that reads like Python, that's the point.

---

## Slide 4 — Visual

The picture. Sequential on the left: children run top to bottom. Parallel in the middle: children run concurrently. Loop on the right: children cycle until exit.

Same Runner, same event stream, same state dict. Only the composition class changes. Everything else you've learned for the last four modules still works.

---

## Slide 5 — State is the pipe

Between children, state is the pipe. Use `output_key="summary"` on a child and that child's result writes to `state["summary"]`. In a later child's instruction, use `{summary}` — curly braces — and ADK substitutes the value from state before the model sees the prompt.

There's an optional variant: `{summary?}` — with a question mark. That means "substitute if present, leave empty if missing." Useful for loop iterations where early passes haven't written the key yet.

Write with `output_key`. Read with curly-brace substitution. That's the entire orchestration vocabulary for workflow agents.

---

## Slide 6 — SequentialAgent header

Primitive one. SequentialAgent. Ordered pipeline; state flows downstream.

---

## Slide 7 — Two-step pipeline code

Here's the shape. A summarizer with `output_key="summary"` writes to state. A translator with `{summary}` in its instruction reads state. Wire them into a SequentialAgent; give it a name; done.

You don't write a for-loop that calls the children. You don't pass state manually between them. The SequentialAgent is the loop, and ADK passes state implicitly through the session.

---

## Slide 8 — Live: Sequential

Switch to the notebook. Cell nine. We pass in three sentences about a hungry cat. Summarizer condenses to one. Translator reads the summary out of state and returns Slovak. Two LLM calls, one composition.

---

## Slide 9 — ParallelAgent header

Primitive two. ParallelAgent. Concurrent fan-out. Wall time approximately equals slowest child, not sum of children.

---

## Slide 10 — Three-way fan-out code

Three researchers, each with a different instruction, each writing to a different state key. Wire them into a ParallelAgent. ADK uses asyncio under the hood to run them concurrently.

The pattern is exactly like `asyncio.gather(task_a, task_b, task_c)` — except each task is an LLM agent and each result lands in its own state slot.

---

## Slide 11 — Live: Parallel

Switch to the notebook. Cell twelve. Three researchers, one timer. Notice the authors interleave in finish order — cz_researcher might print before de_researcher even though we declared it second. That's concurrency. And the wall time is about one second, not three.

---

## Slide 12 — What to notice

Three observations.

Authors interleave in finish order, not declaration order. When you read events from a parallel run, don't assume ordering.

Wall time is one child's duration, not the sum. If each LLM call is one second, sequential takes three seconds, parallel takes one point one. The savings scale with the width of the fan-out.

Each child writes to its own state key, so they don't collide. If two children tried to write to the same key, whichever wrote last would win — so don't do that.

A common production pattern is to fan out independent research or lookups in parallel, then feed the collected state into a sequential synthesizer. We'll build exactly that in a minute.

---

## Slide 13 — LoopAgent header

Primitive three. The canonical ADK wow demo. LoopAgent — generator plus critic — refine until satisfied.

---

## Slide 14 — The pattern

The picture. A LoopAgent with two children. Generator writes a draft to state. Critic reads the draft, decides whether it's good enough. If not, writes a critique back to state and the loop continues — the generator reads the critique on the next pass and revises. If the critic is satisfied, it calls `exit_loop`, which ADK intercepts and terminates the loop.

This pattern has many names in the literature. Self-correction. Critic-driven refinement. Reflexion. Draft-and-review. Whatever you call it, in ADK it's a LoopAgent with two children.

Without LoopAgent you'd write a `while True` with an exit condition in Python. With LoopAgent, ADK handles the looping, the state passing, the iteration counting, and the exit-signal mechanism. You declare the two children and the max iterations; ADK runs the pattern.

---

## Slide 15 — The generator

The generator. Its instruction reads the previous draft and previous critique from state — using `{draft?}` and `{critique?}` with the question mark, because on iteration one neither exists yet. The instruction says: if both exist, revise; otherwise, draft from scratch. Output goes to `state["draft"]`.

One subtle but important design rule: the generator's output is text, so make the instruction clear that the output should ONLY be the tagline — no preamble, no explanation, no markdown. In workflow compositions, drift in output formatting cascades. If the generator adds "Here's my draft:" as a prefix, the critic then sees that as part of the draft and critiques it. Be strict.

---

## Slide 16 — The critic

The critic. Its instruction reads the current draft and evaluates it against named criteria. If any criterion fails, it writes a one-sentence critique to state. If all criteria pass, it calls the `exit_loop` tool.

`exit_loop` is imported from `google.adk.tools`. It's a built-in tool that signals to the parent LoopAgent: "we're done." The critic gets it in its `tools=` list. When the critic's model emits a call to `exit_loop`, ADK catches it and terminates the loop. Clean signal, no magic.

Then the LoopAgent itself. Two children, max_iterations equals five. Always set max_iterations. If your critic is impossible to satisfy, the loop runs forever and your API bill runs forever with it. Five is usually enough; if the critic can't be satisfied in five rounds, it probably can't be satisfied at all.

---

## Slide 17 — Live: Loop

Cell fifteen of the notebook. The user asks for a tagline. Watch the iterations. Generator produces a draft with the word "Master," which violates the cliche rule. Critic flags it. Generator revises. Critic approves. exit_loop fires. You see it in the event stream as a tool call to `exit_loop` with empty arguments.

---

## Slide 18 — What to always do

Three rules to always follow.

First: always set max_iterations. If the critic is impossible to satisfy, the agent runs forever. Five is usually enough. For reference: I've seen production LoopAgents with max_iterations at ten. I've never seen one higher than twenty.

Second: pair exit_loop with the child that has the exit condition. Usually the critic, reviewer, or gate-keeper. Don't scatter exit_loop across multiple children unless you have a specific reason — it makes the exit condition hard to reason about.

Third: use the question-mark syntax for state keys that might not exist yet. `{draft?}` means "substitute if present, empty string if not." Iteration one has no previous draft; the question mark prevents a KeyError.

---

## Slide 19 — Composing workflows header

Putting it together. Workflow agents are themselves agents — so you can nest them inside other workflow agents.

---

## Slide 20 — Parallel inside Sequential

The classic composition. A SequentialAgent whose first child is a ParallelAgent. You fan out independent research in parallel, then synthesize sequentially.

Five LLM calls total — three parallel researchers, then one synthesizer that reads all three results. Wall time comes in around two calls' worth, not five. The synthesizer's instruction uses `{germany_fact}`, `{slovakia_fact}`, `{czech_fact}` to read all three parallel results from state.

This is the shape most production agents take. Not one monolithic agent. Not even five children in a flat list. A pipeline of phases, some parallel within a phase, some sequential across phases.

---

## Slide 21 — Live: composition

Cell eighteen. Parallel researchers followed by a sequential synthesizer. The final report connects the three facts thematically.

---

## Slide 22 — Workflow vs LLM-driven

The big alternative to workflow agents is letting the LLM decide. You build one agent with all the sub-agents in its `sub_agents=` list, and the model at the top picks which to call. That's what module six will cover.

Both styles work. They're not interchangeable.

Use a workflow agent when the control flow is fixed — always summarize, then translate. When you need determinism for tests or evals. When latency matters — parallel fans out without a deliberation turn. When the workflow should be auditable from a diagram.

Use LLM-driven when the control flow depends on user input. When flexibility is the point. When the model's judgment is what adds value. When conversations can go anywhere and pre-canning the flow would constrain the product.

---

## Slide 23 — The rule

The rule of thumb, on one slide. If you can name the workflow, use a workflow agent. If you can't, let the LLM decide.

Sequential, Parallel, Loop cover the named-workflow cases cleanly. Anything more complex, start composing them. If the composition gets unwieldy, that's a signal the workflow shouldn't be named after all — let the LLM drive.

---

## Slide 24 — Next

Module six. Multi-agent hierarchies. The LLM-driven alternative to workflow agents. Sub-agents for transfer. AgentTool for the consultant pattern — we saw a glimpse of AgentTool in module two. Now we'll put it in context against sub-agents and see when each is right. See you there.
