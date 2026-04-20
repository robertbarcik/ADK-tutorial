# Callbacks as middleware

Six lifecycle hooks wrap every invocation of an ADK agent. You can intercept any step — the agent starting, the LLM being called, a tool running — observe it, transform it, or **short-circuit it entirely**. This is the cleanest mechanism in the framework for guardrails, caching, PII redaction, mocking, and every other cross-cutting concern that should apply to an agent's lifecycle without polluting its instruction.

If you have used Express.js middleware, Django middleware, or plugin hooks in any framework, the shape is familiar. **Callbacks are for agents what middleware is for web handlers.** A pipeline of before- and after-hooks around each meaningful step, each of which can decide to let the step proceed or replace it with something else.

## The six hooks

Three lifecycle events, each wrapped by a before/after pair:

| Event | Before | After |
|---|---|---|
| Agent runs | `before_agent_callback` | `after_agent_callback` |
| Model call | `before_model_callback` | `after_model_callback` |
| Tool call | `before_tool_callback` | `after_tool_callback` |

Plus two error-handling hooks for recovering from exceptions: `on_model_error_callback` and `on_tool_error_callback`. Less common; default behavior is the error propagates.

All six are passed to `LlmAgent(...)` as named arguments. All six are plain Python functions.

## The return-to-override pattern

This is the rule. Every callback follows the same convention:

```python
def my_callback(context, request_or_response_or_args):
    # Observe, log, validate — whatever.
    if <some condition>:
        return <a replacement value>   # ← ADK uses this; real call skipped
    return None                        # ← real call proceeds
```

`None` means "carry on." A returned object means "use this instead of doing the thing."

The type of the "thing" depends on the hook:
- A `before_model_callback` returning a value must return an `LlmResponse` (what the model would have produced).
- A `before_tool_callback` returning a value must return whatever the tool would have returned (usually a dict).
- An `after_tool_callback` returning a value replaces the tool's actual return.
- And so on.

That single convention — return `None` or return a replacement value — is what makes callbacks a general-purpose interception layer. Same API, different hooks, different things get short-circuited.

## Demo 1 — `before_model_callback`: the blocklist guardrail

The canonical 5-line safety gate. Runs just before every LLM call. Sees the full request — user message, system instruction, chat history, tool definitions.

```python
from google.adk.models.llm_response import LlmResponse

BLOCKED_WORDS = ["password", "secret", "credit card"]

def blocklist_guardrail(callback_context, llm_request):
    latest_user = ""
    if llm_request.contents:
        for part in llm_request.contents[-1].parts or []:
            if part.text:
                latest_user = part.text.lower()
                break

    for bad in BLOCKED_WORDS:
        if bad in latest_user:
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=(
                        f"I can't help with '{bad}'. Please rephrase."
                    ))],
                )
            )
    return None

guarded_agent = LlmAgent(
    name="guarded_agent",
    model=LiteLlm(model=MODEL_STRING),
    instruction="You are helpful and concise.",
    before_model_callback=blocklist_guardrail,
)
```

Two runs demonstrate the behavior:

- **"What is photosynthesis?"** — no blocked words. Callback returns `None`. LLM runs. Normal answer.
- **"What's the CEO's password?"** — callback returns a canned `LlmResponse`. The LLM is **never called**. ADK uses the callback's response as if it came from the model.

You will not see any LLM-deliberation events in the blocked run. Zero tokens billed. Guaranteed refusal.

This is the single most important reason to learn callbacks: they are how you enforce safety at the **framework layer**, not the prompt layer. An instruction like "refuse to discuss passwords" is a polite request the model can misinterpret or be jailbroken around. A code-level check in a callback is a wall — the text never reaches the model.

The pattern scales. Swap the `in` check for regex, a PII classifier, a toxicity model, or anything else that can decide yes/no in Python. The returned `LlmResponse` can be whatever you want: a refusal, a redirect, a templated answer. You own the decision.

## Demo 2 — `after_tool_callback`: PII redaction

Runs just after a tool returns, before the result goes back to the model. Sees the tool, the arguments it was called with, the context, and the return value.

```python
SENSITIVE_FIELDS = {"salary", "ssn", "home_address", "date_of_birth"}

def redact_pii(tool, args, tool_context, tool_response):
    if isinstance(tool_response, dict):
        cleaned = dict(tool_response)
        for key in SENSITIVE_FIELDS & cleaned.keys():
            cleaned[key] = "[REDACTED]"
        return cleaned
    return None  # No change

hr_agent = LlmAgent(
    name="hr_agent",
    model=LiteLlm(model=MODEL_STRING),
    instruction="Use lookup_employee to answer.",
    tools=[lookup_employee],
    after_tool_callback=redact_pii,
)
```

When the HR agent runs, the tool function itself returns the full record — including salary, SSN, home address. The callback intercepts the return value on the way back. The model's tool-response event contains only the cleaned dict; salary, SSN, home address appear as `[REDACTED]`.

The key observation: **the tool function itself returned the full record**. Your Python code is still aware of the sensitive fields. Audit logs, downstream pipelines, and systems that legitimately need the data can still use the unredacted return. Only the model's view is redacted.

This contains the PII blast radius at the callback layer rather than hard-coding redaction into the tool function. If the same tool has ten callers — some of which need the full data, some of which don't — the callback gives you per-agent redaction policy without forking the tool.

The pattern scales to anything "filter outputs on the way out": truncate overly long results, rename fields the model keeps getting confused by, add audit tags, strip base64-encoded blobs, normalize currency units.

## Demo 3 — `before_tool_callback`: mocking for tests

Runs just before a tool executes. Sees the tool and the args the model wants to call it with.

```python
MOCK_RESPONSES = {
    "AAPL": {"ticker": "AAPL", "price": 180.00, "currency": "USD", "source": "mock"},
    "GOOG": {"ticker": "GOOG", "price": 140.00, "currency": "USD", "source": "mock"},
}

def mock_in_tests(tool, args, tool_context):
    if tool.name == "fetch_stock_price":
        ticker = args.get("ticker", "").upper()
        if ticker in MOCK_RESPONSES:
            return MOCK_RESPONSES[ticker]
    return None  # Let the real tool run.

stock_agent = LlmAgent(
    ...,
    tools=[fetch_stock_price],
    before_tool_callback=mock_in_tests,
)
```

When you ask the agent for AAPL, the callback matches the ticker against its mock dictionary, returns the mock, and the real `fetch_stock_price` never runs. When you ask for MSFT, the callback returns `None` and the real tool runs.

This is the cleanest pattern for making agent code **unit-testable**. Inject the callback in tests — no real API hits, no fixtures, no separate test doubles. Leave it off in production. The same agent code runs both paths without modification.

It's also useful in production: a cache hit check before running an expensive tool, a circuit-breaker that returns a fallback when an external API is degraded, environment-specific behavior (canned data in dev, real data in prod).

## When to use callbacks vs alternatives

Callbacks are not the only way to intervene in an agent's lifecycle. ADK offers several mechanisms, each with its place.

| Mechanism | Scope | When |
|---|---|---|
| **Instruction prompt** | One agent | Soft preferences, style, default behavior |
| **Tool function code** | One tool | Guards on irreversible operations (covered in M02) |
| **Callback** | One agent's lifecycle | Cross-cutting concerns — guardrails, PII, caching, mocking |
| **Plugin** | Whole runner, all agents | Org-wide policies; audit logging; compliance |

**Rule of thumb: callbacks for agent-specific logic, plugins for app-wide policy.**

A blocklist that applies to one specialist agent → callback. A company-wide audit trail that must fire on every agent in the app → plugin.

Plugins are out of scope for this chapter — M10 touches on them for production deployments. For most day-to-day work, callbacks are the right reach.

## The observability gotcha

Worth naming so you're not surprised in production. **Callback execution does not automatically appear in the OpenTelemetry traces ADK emits** — at least as of v1.28 (check release notes on newer versions; this may be addressed).

Concretely: if you use Cloud Trace, Langfuse, Arize, or any other observability tool consuming ADK's OTel output, you will see LLM calls, tool calls, and state deltas as spans. You will **not** see "before_model_callback ran, returned None" as a span.

If you rely on callbacks for policy decisions in production and need to observe them, instrument your callbacks manually — a print, a log line, or an explicit OpenTelemetry span created from inside the callback. The documentation gap is known; Google's own ADK blog posts acknowledge it.

## Putting callbacks in a larger architecture

Callbacks, workflow agents, sub_agents, and AgentTool combine cleanly. A real production architecture often has:

- Workflow agents for the top-level flow (Sequential, Parallel, Loop).
- Sub-agents or AgentTools for specialization.
- Callbacks on each agent for its specific policies — guardrails, redaction, mocks.
- Plugins on the runner for org-wide concerns — audit, billing, global rate-limit.

All four layers are compositional. You can add a callback to a sub-agent inside a LoopAgent inside a SequentialAgent and everything still works. The interception mechanism is orthogonal to the composition mechanism.

## What to carry forward

- **Six lifecycle hooks:** before/after × agent/model/tool. Plus two error hooks.
- **Return-to-override:** `None` proceeds, a value short-circuits with your replacement.
- **`before_model_callback`** is the guardrail hook — short-circuits the LLM, zero tokens billed.
- **`after_tool_callback`** is the output-filter hook — redact PII, truncate, reshape.
- **`before_tool_callback`** is the mocking/cache hook — the test-seam.
- **Callbacks for agent-specific logic; Plugins for app-wide policy.**
- **Observability gap:** callbacks don't automatically appear in OTel traces. Instrument manually if needed.

Module 08 picks up **memory**. Session state was short-term memory — tied to one session, or at best carried across sessions within one user via scope prefixes. M08 is the long-term version: swapping `InMemorySessionService` for a SQLite-backed `DatabaseSessionService`, introducing `MemoryService` and the `load_memory` tool for explicit recall across time, and revisiting the Skeptical Memory pattern from Module 03 — now with teeth, because at long time horizons staleness is the default.
