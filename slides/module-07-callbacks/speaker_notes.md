# M07 — Speaker notes

---

## Slide 1 — Title

Callbacks as middleware. That's what this module is about. Six lifecycle hooks wrap every invocation of your agent, and they all follow the same simple rule: return `None` to proceed normally, or return a value to short-circuit. That single convention turns the hook mechanism into a general-purpose guardrail and interception layer, which is why the same pattern covers things like guardrails, caches, PII redaction, and test mocks.

---

## Slide 2 — Middleware analogy

The analogy to hold in your head is that callbacks are for agents what middleware is for web handlers. If you've used something like Express middleware, Django middleware, or plugin hooks in any framework, you already know the shape: a pipeline of pre- and post-hooks around each step of the request lifecycle. ADK takes the same idea and applies it to the agent lifecycle.

---

## Slide 3 — Six hooks

Let me walk through the six hooks. There are three lifecycle events, and each one is wrapped by a before/after pair.

First, the agent run itself, with `before_agent_callback` and `after_agent_callback`. These fire at the boundaries of the whole invocation.

Second, the model call, with `before_model_callback` and `after_model_callback`. These fire around every LLM request.

And third, the tool call, with `before_tool_callback` and `after_tool_callback`. These fire around every tool execution.

On top of those six, there are two error-handling hooks for recovering from exceptions: `on_model_error_callback` and `on_tool_error_callback`. They're less commonly used, because the default is that the error just propagates.

---

## Slide 4 — Return to override

The whole callback API comes down to one rule, which I call return-to-override. You'll see it on every example in this module. Return `None` from your callback, and things proceed normally. Return a value, and things short-circuit. The next slide unpacks why that single convention does so much work.

---

## Slide 5 — The entire API on one slide

What you see on the slide is the entire callback API. A function that takes a context and some hook-specific arguments. Inside, you observe, log, or validate. And at the end, you decide.

`return None` means "I'm just observing, let the real call happen."

`return <a value>` means "skip the real call and use this instead."

That's it. The same pattern across all six hooks. The only thing that varies is what type of value each hook accepts as a replacement.

---

## Slide 6 — Demo 1: before_model_callback for blocklist

Let's get into the first demo. We're going to use `before_model_callback` to build a blocklist guardrail in just five lines of code. The setup looks trivial, but the implications go pretty far once you see it run.

---

## Slide 7 — Five lines of safety gate

On the slide we have the blocklist guardrail in code. A list of forbidden words at the top, a callback function that checks the latest user message against the list, and if it matches, the callback returns a canned `LlmResponse`. As a result, the LLM is never called.

Two details worth noticing. First, the `llm_request.contents` list has the full chat history, and the latest turn is the last entry. Second, the returned value is a proper `LlmResponse` object with model-role content. That's what ADK expects when you short-circuit.

---

### Notebook break — The blocklist in action

[Switch the screen to the notebook.]

Let me run this. I'll send two prompts through the same agent. The first is a harmless question about photosynthesis. [Run the cell.] The callback runs, sees no blocked words, returns `None`, and the LLM produces a normal answer. Now the second prompt, which contains the word "password". [Run the next cell.] The callback fires, spots the blocked word, and returns its canned `LlmResponse`. Look at the event stream: there are no model-deliberation events at all. The LLM was never called.

[Switch back to the slide deck.]

---

## Slide 8 — On the blocked run, the LLM was never called

Here's the real payoff of what you just saw in the demo. On the blocked run, the LLM was never called at all. That means zero tokens billed, and a guaranteed refusal that doesn't depend on the model's good behavior.

Compare this with a soft guardrail, like an instruction that says "refuse to discuss passwords." An instruction is really just a polite request that the model can misinterpret or get jailbroken around. A code-level check inside a callback, on the other hand, is a wall. It can't be bypassed by anything the user types, because the text never reaches the model in the first place.

This is the single most important reason to learn callbacks. They're how you enforce safety at the framework layer, not at the prompt layer where it can be argued with.

---

## Slide 9 — Demo 2: after_tool_callback for PII redaction

On to demo two: `after_tool_callback`, applied to PII redaction. Same pattern, different lifecycle hook, and a very different production use case.

---

## Slide 10 — Redact sensitive fields

The slide shows the redaction callback in code. The function is called `redact_pii`, and right above it we have a set of sensitive field names: salary, SSN, and home address. Those are the fields we never want the model to see.

The function itself does something simple. It runs after the tool has returned, but before the model gets to look at the response. When the response is a dictionary, the function makes a copy, replaces any of those sensitive keys with the string `[REDACTED]`, and hands the cleaned version back. ADK then uses this cleaned version as the tool-response the model actually sees, while the original tool-function return stays untouched.

In your own code, the sensitive set is whatever you don't want to leak: customer card numbers, employee SSNs, internal IDs. The shape of the function stays the same.

---

### Notebook break — PII redaction in action

[Switch the screen to the notebook.]

The HR agent in the notebook is set up to look up an employee called Alice. [Run the cell.] Look at the tool-response event in the output. The tool function returned Alice's full record, with her email, department, salary, SSN, and home address. But by the time the response reaches the model, the salary, SSN, and home address are all marked `[REDACTED]`. The callback intercepted the tool output on its way back, copied it, and stripped the sensitive fields. The model only sees the safe version, and its final answer is appropriately cagey.

[Switch back to the slide deck.]

---

## Slide 11 — Why this matters

The key observation from that demo is this. The tool function itself returned the full record, which means your Python code, your audit logs, and your database writes all saw the real values. But the model saw the redacted version.

That's the production value. You contain the PII blast radius at the callback layer, not at the tool-function layer. Other systems that legitimately need the full data, like your billing pipeline or your HR database, can still call the tool function directly without the callback, and they get the real values.

---

## Slide 12 — Demo 3: before_tool_callback for test mocks

And now demo three: `before_tool_callback`, applied to mocking expensive or external tools for tests.

---

## Slide 13 — Short-circuit expensive tools

Look at the code on the slide. This is the mocking pattern in practice. A dict of mock responses keyed by ticker, and a callback that fires before the tool runs. The callback checks whether the tool being called is `fetch_stock_price` and whether the ticker has a mock entry. If yes, it returns the mock, and the real tool never runs. If no, it returns `None`, and the real tool runs normally.

---

### Notebook break — Mocking in action

[Switch the screen to the notebook.]

Now let me show this pattern in action. The agent has a `fetch_stock_price` tool that would normally hit a real API, and the callback is wired in with a small dict of mock prices. I'll ask for the AAPL price first, which has a mock entry. [Run the cell.] Watch the event stream. The callback fires before the tool runs, sees that AAPL is in the mock dict, and short-circuits with the mock. The real API call is never made; you'd see a `REAL` print line if it had been, and there's nothing there. Now I'll ask for a ticker that's not in the mocks. [Run the next cell.] This time the callback returns `None`, and the real tool runs.

[Switch back to the slide deck.]

---

## Slide 14 — Production win

The production value of that pattern, on one slide. Same agent code, tests without hitting real APIs. You inject the callback in tests, and you leave it off in production. No separate test doubles, no test-only code paths in your agent. The callback is the test seam.

That's how you make agent code unit-testable. It's also how you build resilience. If the real API is down, a `before_tool_callback` can return a cached fallback instead of failing the request.

---

## Slide 15 — Six hooks reference

Let's look at all six hooks together with their typical use cases, so you have one reference card you can keep in your head.

Agent-level hooks are the least commonly used. The before-agent hook is for pre-flight setup, and the after-agent hook is for final-output logging.

Model-level hooks are where guardrails, caching, and prompt-injection checks live.

And tool-level hooks are where mocking, PII redaction, and argument validation live.

Memorize the three "before" hooks at minimum. They're the ones you reach for when you want to short-circuit something.

---

## Slide 16 — Callbacks vs alternatives

So when should you pick callbacks versus other mechanisms? There are really four ways to intervene in an agent's lifecycle, each with its own use case.

The first is the instruction prompt itself, which is good for soft preferences and style. That covers one agent's behavior at the model level.

The second is the tool function code, which is the right place to put guards on irreversible operations. That covers one tool's safety.

The third is callbacks, the topic of this module. Use them for cross-cutting concerns across one agent's whole lifecycle, like guardrails, PII redaction, and caching.

And the fourth is plugins, which are newer, broader, and applied across every agent in a runner. Plugins are for org-wide policies and audit logging.

So the rule of thumb is this. Callbacks for agent-specific logic, plugins for app-wide policy. If the same policy must fire on every agent in your app, reach for a plugin. If it's specific to one agent, callbacks are the right tool.

Plugins are out of scope today; we'll touch on them later in the course when we cover production deployments.

---

## Slide 17 — Observability gotcha

Before we wrap, there's a real observability gotcha worth naming so you're not surprised. Callback execution does not automatically appear in ADK's OpenTelemetry traces, at least as of version 1.28. So check the release notes if you're on a newer version, because this might change.

Concretely, if you're using something like Cloud Trace, Langfuse, or Arize to observe runs, you'll see LLM calls, tool calls, and state deltas. You will not see "before_model_callback ran, returned None" as a span.

That's why, if you rely on callbacks for policy decisions and you need that execution to be observable in production, you'll want to instrument your callbacks manually. Things like print statements, log lines, or manual spans via the OpenTelemetry API. It's a documented gap; Google's own ADK blog acknowledges it.

---

## Slide 18 — What to carry forward

So what should you carry forward from today? Three things really matter.

The first is the six hooks themselves, and the single rule that governs all of them: return `None` to pass through, or return a value to short-circuit. That's the whole API, and you'll use it the same way every time.

The second is the realization that the same pattern covers very different production needs. Guardrails, PII redaction, test mocks, and caches all use exactly the same callback signature, just at a different point in the lifecycle. Once you've written one, you can write the others.

And the third is the reason to reach for callbacks in the first place. They're how you enforce policy in code rather than in prompts. An instruction can be argued with; a callback cannot. That makes them your default tool for anything that has to behave reliably under adversarial input or production load.

---

## Slide 19 — Up next

Up next, memory. We've been on in-memory session state throughout the vendor-agnostic part of the course, and the next module is where sessions get real persistence. We swap to `DatabaseSessionService` backed by SQLite, introduce the `load_memory` tool and `MemoryService` for explicit long-term recall, and revisit the Skeptical Memory pattern from earlier with more depth. See you there.
