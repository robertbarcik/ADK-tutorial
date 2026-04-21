# M07 — Speaker notes

---

## Slide 1 — Title

Module seven. Callbacks as middleware. Six lifecycle hooks wrap every invocation of your agent, and they all follow the same simple rule: return `None` to proceed normally, return a value to short-circuit. That single convention turns the hook mechanism into a general-purpose guardrail and interception layer. Guardrails, caches, PII redaction, test mocks — all the same pattern.

---

## Slide 2 — Middleware analogy

The analogy. Callbacks are for agents what middleware is for web handlers. If you've used Express middleware, Django middleware, or plugin hooks in any framework, you already know the shape — a pipeline of pre- and post-hooks around each step of the request lifecycle. ADK takes the same idea and applies it to the agent lifecycle.

---

## Slide 3 — Six hooks

Three lifecycle events, each wrapped by a before/after pair.

Agent runs — `before_agent_callback` and `after_agent_callback`. Fire at the boundaries of the whole invocation.

Model call — `before_model_callback` and `after_model_callback`. Fire around every LLM request.

Tool call — `before_tool_callback` and `after_tool_callback`. Fire around every tool execution.

Plus two error-handling hooks for recovering from exceptions: `on_model_error_callback` and `on_tool_error_callback`. Less commonly used; default is the error propagates.

---

## Slide 4 — Return-to-override header

The one rule. Return-to-override. Return `None`, things proceed. Return a value, things short-circuit.

---

## Slide 5 — The entire API

Here it is. The entire callback API, on one slide. A function that takes a context and some hook-specific arguments. Inside, you observe, log, or validate. At the end, decide.

`return None` means "I'm just observing, let the real call happen."

`return <a value>` means "skip the real call and use this instead."

That's it. Same pattern across all six hooks. The only thing that varies is what type of value each hook accepts as a replacement.

---

## Slide 6 — Demo 1 header

Demo one. `before_model_callback`. The canonical 5-line blocklist guardrail.

---

## Slide 7 — Five lines of safety gate

Here's the code. A blocklist of words, a callback function that checks the latest user message against the list, and if it matches, returns a canned `LlmResponse`. The LLM is never called.

Two details worth noticing. The `llm_request.contents` list has the full chat history; the latest turn is the last entry. And the returned value is a proper `LlmResponse` object with model-role content — that's what ADK expects when you short-circuit.

---

## Slide 8 — Live: blocklist

Switch to the notebook. Cell eleven. Two queries: a harmless one about photosynthesis passes through to the LLM. A query containing "password" hits the callback, gets short-circuited, never touches the LLM. Watch the event stream — the blocked run has no model-deliberation events. Just the callback's canned response.

---

## Slide 9 — LLM never called

The payoff, on one slide. On the blocked run, the LLM was never called. Zero tokens billed. Guaranteed refusal.

Compare this to a soft guardrail — an instruction that says "refuse to discuss passwords." An instruction is a polite request the model can misinterpret or be jailbroken around. A code-level check in a callback is a wall. It cannot be bypassed by anything the user types, because the text never reaches the model.

This is the single most important reason to learn callbacks: they're how you enforce safety at the framework layer, not the prompt layer.

---

## Slide 10 — Demo 2 header

Demo two. `after_tool_callback`. PII redaction.

---

## Slide 11 — Redact fields

The pattern. A tool returns a dict with some sensitive fields. The callback runs after the tool, before the model sees the result. It checks if the return is a dict, copies it, replaces sensitive keys with `[REDACTED]`, returns the cleaned version. ADK uses the cleaned version as the tool-response the model sees.

The sensitive-fields set here is salary, SSN, home address — typical PII. In your own code, put whatever fields you don't want to leak.

---

## Slide 12 — Live: PII redaction

Notebook cell fourteen. The HR agent looks up Alice. The tool returns her full record — email, department, salary, SSN, home address. The callback intercepts it on the way back. The model sees only email and department as real values; salary, SSN, and home address come through as `[REDACTED]`. The final response is appropriately cagey.

---

## Slide 13 — Why this matters

The key observation. The tool function itself returned the full record. Your Python code, your audit logs, your database writes — they all saw the real values. But the model saw the redacted version.

That's the production value. You contain the PII blast radius at the callback layer, not at the tool-function layer. Other systems that legitimately need the full data — your billing pipeline, your HR database — can still call the tool function directly without the callback, and they get the real values.

---

## Slide 14 — Demo 3 header

Demo three. `before_tool_callback`. Mocking for tests.

---

## Slide 15 — Short-circuit expensive tools

The pattern. A dict of mock responses, keyed by ticker. The callback checks if the tool being called is `fetch_stock_price` and whether the ticker has a mock entry. If yes, returns the mock; the real tool never runs. If no, returns `None`; the real tool runs normally.

---

## Slide 16 — Production win

The production value, on one slide. Same agent code, tests without hitting real APIs. Inject the callback in tests, leave it off in production. No separate test doubles, no test-only code paths in your agent. The callback is the test seam.

This is how you make agent code unit-testable. It's also how you build resilience — if the real API is down, a `before_tool_callback` can return a cached fallback instead of failing the request.

---

## Slide 17 — Six hooks reference

All six hooks, with one-line use cases.

Agent-level hooks are less common. Before-agent for pre-flight setup; after-agent for final-output logging.

Model-level hooks are where guardrails, caching, and prompt-injection checks live.

Tool-level hooks are where mocking, PII redaction, and argument validation live.

Memorize the three "before" hooks at minimum — they're the ones you reach for when you want to short-circuit something.

---

## Slide 18 — Callbacks vs alternatives

When to pick callbacks versus other mechanisms. Four ways to intervene in an agent's lifecycle.

Instruction prompt — soft preferences, style. One agent's behavior.

Tool function code — guards on irreversible operations. One tool's safety.

Callbacks — cross-cutting concerns for one agent's whole lifecycle. Guardrails, PII, caching.

Plugins — newer, broader, applies across all agents in a runner. Org-wide policies, audit logging.

The rule: callbacks for agent-specific logic, plugins for app-wide policy. If the same policy must fire on every agent in your app, reach for a plugin. If it's specific to one agent, callbacks are right.

Plugins are out of scope today — module ten touches on them for production deployments.

---

## Slide 19 — Observability gotcha

A real gotcha worth naming so you're not surprised. Callback execution does not automatically appear in ADK's OpenTelemetry traces. At least as of version 1.28 — check release notes if you're on a newer version, this might change.

Concretely: if you're using Cloud Trace, Langfuse, or Arize to observe runs, you'll see LLM calls, tool calls, state deltas. You will not see "before_model_callback ran, returned None" as a span.

If you rely on callbacks for policy decisions and you need the callback execution to be observable in production, instrument your callbacks manually. Print statements, log lines, or manual spans via the OpenTelemetry API. Documented gap; Google's own ADK blog acknowledges it.

---

## Slide 20 — What to carry forward

What to carry forward. Six hooks. One rule: return `None` or return a value. The pattern generalizes to guardrails, redactors, mocks, caches — pick the hook that fits and write the check.

---

## Slide 21 — Next

Module eight. Memory. We've been on in-memory session state for seven modules. Module eight is where sessions get real persistence — we swap to `DatabaseSessionService` backed by SQLite, introduce the `load_memory` tool and `MemoryService` for explicit long-term recall, and revisit the Skeptical Memory pattern from module three with more depth. See you there.
