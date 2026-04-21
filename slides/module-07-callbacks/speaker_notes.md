# M07 — Speaker notes

---

## Slide 1 — Title

Welcome to module seven — callbacks as middleware. Six lifecycle hooks wrap every invocation of your agent, and they all follow the same simple rule — return `None` to proceed normally, or return a value to short-circuit. That single convention turns the hook mechanism into a general-purpose guardrail and interception layer, which is why the same pattern covers things like guardrails, caches, PII redaction, and test mocks.

---

## Slide 2 — Middleware analogy

The analogy to hold in your head is that callbacks are for agents what middleware is for web handlers. If you've used something like Express middleware, Django middleware, or plugin hooks in any framework, you already know the shape — a pipeline of pre- and post-hooks around each step of the request lifecycle. ADK takes the same idea and applies it to the agent lifecycle.

---

## Slide 3 — Six hooks

Let me walk through the six hooks. There are three lifecycle events, and each one is wrapped by a before/after pair.

First, the agent run itself — so `before_agent_callback` and `after_agent_callback`. These fire at the boundaries of the whole invocation.

Second, the model call — `before_model_callback` and `after_model_callback`. These fire around every LLM request.

And third, the tool call — `before_tool_callback` and `after_tool_callback`. These fire around every tool execution.

On top of those six, there are two error-handling hooks for recovering from exceptions — `on_model_error_callback` and `on_tool_error_callback`. They're less commonly used, because the default is that the error just propagates.

---

## Slide 4 — Return-to-override header

If you remember one rule about callbacks, remember this — return-to-override. Return `None`, and things proceed. Return a value, and things short-circuit.

---

## Slide 5 — The entire API

What you see on this slide is the entire callback API, on one slide. A function that takes a context and some hook-specific arguments. Inside, you observe, log, or validate. And at the end, you decide.

`return None` means "I'm just observing, let the real call happen."

`return <a value>` means "skip the real call and use this instead."

That's it — the same pattern across all six hooks. The only thing that varies is what type of value each hook accepts as a replacement.

---

## Slide 6 — Demo 1 header

Time for demo one — `before_model_callback`, the canonical five-line blocklist guardrail.

---

## Slide 7 — Five lines of safety gate

In code, the blocklist guardrail looks like this. A list of forbidden words, a callback function that checks the latest user message against the list, and if it matches, the callback returns a canned `LlmResponse`. As a result, the LLM is never called.

Two details worth noticing. First, the `llm_request.contents` list has the full chat history, and the latest turn is the last entry. Second, the returned value is a proper `LlmResponse` object with model-role content — that's what ADK expects when you short-circuit.

---

## Slide 8 — Live: blocklist

Switch to the notebook — cell eleven. We'll run two queries. First, a harmless one about photosynthesis, which passes through to the LLM. Second, a query containing "password", which hits the callback, gets short-circuited, and never touches the LLM. Watch the event stream — the blocked run has no model-deliberation events at all, just the callback's canned response.

---

## Slide 9 — LLM never called

The payoff of that demo, on one slide. On the blocked run, the LLM was never called. Zero tokens billed. Guaranteed refusal.

Compare this to a soft guardrail — so an instruction that says "refuse to discuss passwords." An instruction is really just a polite request the model can misinterpret or be jailbroken around. A code-level check in a callback, on the other hand, is a wall. It cannot be bypassed by anything the user types, because the text never reaches the model.

This is the single most important reason to learn callbacks — they're how you enforce safety at the framework layer, not at the prompt layer.

---

## Slide 10 — Demo 2 header

On to demo two — `after_tool_callback`, applied to PII redaction.

---

## Slide 11 — Redact fields

The redaction pattern looks like this. A tool returns a dict with some sensitive fields. The callback runs after the tool, but before the model sees the result. It checks if the return is a dict, copies it, replaces sensitive keys with `[REDACTED]`, and returns the cleaned version. ADK then uses the cleaned version as the tool-response the model sees.

The sensitive-fields set here is salary, SSN, and home address — so typical PII. In your own code, you'd put whatever fields you don't want to leak.

---

## Slide 12 — Live: PII redaction

Over in cell fourteen of the notebook, the HR agent looks up Alice. The tool returns her full record — email, department, salary, SSN, and home address. The callback intercepts it on the way back. As a result, the model sees only email and department as real values; salary, SSN, and home address all come through as `[REDACTED]`. And the final response is appropriately cagey.

---

## Slide 13 — Why this matters

The key observation from that demo is this. The tool function itself returned the full record — which means your Python code, your audit logs, your database writes all saw the real values. But the model saw the redacted version.

That's the production value. You contain the PII blast radius at the callback layer, not at the tool-function layer. Other systems that legitimately need the full data — things like your billing pipeline or your HR database — can still call the tool function directly without the callback, and they get the real values.

---

## Slide 14 — Demo 3 header

And now demo three — `before_tool_callback`, applied to mocking for tests.

---

## Slide 15 — Short-circuit expensive tools

The mocking pattern looks like this. A dict of mock responses, keyed by ticker. The callback checks whether the tool being called is `fetch_stock_price` and whether the ticker has a mock entry. If yes, it returns the mock, and the real tool never runs. If no, it returns `None`, and the real tool runs normally.

---

## Slide 16 — Production win

The production value of that pattern, on one slide. Same agent code, tests without hitting real APIs. You inject the callback in tests, and you leave it off in production. No separate test doubles, no test-only code paths in your agent. The callback is the test seam.

That's how you make agent code unit-testable. It's also how you build resilience — so if the real API is down, a `before_tool_callback` can return a cached fallback instead of failing the request.

---

## Slide 17 — Six hooks reference

What you see on this slide is all six hooks, with one-line use cases.

Agent-level hooks are less common — before-agent is for pre-flight setup, and after-agent is for final-output logging.

Model-level hooks are where guardrails, caching, and prompt-injection checks live.

And tool-level hooks are where mocking, PII redaction, and argument validation live.

Memorize the three "before" hooks at minimum — they're the ones you reach for when you want to short-circuit something.

---

## Slide 18 — Callbacks vs alternatives

So when should you pick callbacks versus other mechanisms? There are really four ways to intervene in an agent's lifecycle.

First, the instruction prompt — good for soft preferences and style. So one agent's behavior.

Second, tool function code — good for guards on irreversible operations. So one tool's safety.

Third, callbacks — for cross-cutting concerns across one agent's whole lifecycle. Things like guardrails, PII, and caching.

And finally, plugins — newer, broader, and applied across all agents in a runner. Things like org-wide policies and audit logging.

So the rule of thumb is this — callbacks for agent-specific logic, plugins for app-wide policy. If the same policy must fire on every agent in your app, reach for a plugin. If it's specific to one agent, callbacks are the right tool.

Plugins are out of scope today — module ten touches on them for production deployments.

---

## Slide 19 — Observability gotcha

Before we wrap, there's a real observability gotcha worth naming so you're not surprised. Callback execution does not automatically appear in ADK's OpenTelemetry traces — at least as of version 1.28, so check the release notes if you're on a newer version, because this might change.

Concretely, if you're using something like Cloud Trace, Langfuse, or Arize to observe runs, you'll see LLM calls, tool calls, and state deltas. You will not see "before_model_callback ran, returned None" as a span.

That's why, if you rely on callbacks for policy decisions and you need that execution to be observable in production, you'll want to instrument your callbacks manually. Things like print statements, log lines, or manual spans via the OpenTelemetry API. It's a documented gap — Google's own ADK blog acknowledges it.

---

## Slide 20 — What to carry forward

So what should you carry forward from today? Six hooks. One rule — return `None` or return a value. The pattern generalizes to guardrails, redactors, mocks, and caches — so pick the hook that fits and write the check.

---

## Slide 21 — Next

Up next in module eight, we get into memory. We've been on in-memory session state for seven modules now, and module eight is where sessions get real persistence — we swap to `DatabaseSessionService` backed by SQLite, introduce the `load_memory` tool and `MemoryService` for explicit long-term recall, and revisit the Skeptical Memory pattern from module three with more depth. See you there.
