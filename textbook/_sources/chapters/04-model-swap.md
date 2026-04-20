# The one-line model swap

Three chapters into this course, every example has used a single model string: `openrouter/google/gemini-2.5-flash-lite`. This chapter opens that abstraction up. By the end of the matching notebook, the *same* agent code will have run on five different providers — Claude, GPT, Gemini, Qwen, and Llama — with one line of configuration changing each time. The rest of the code is untouched.

That is the shape of vendor-neutrality in ADK. This chapter explains how it works, when to use it, and the one prefix gotcha that bites anyone who tries to run a local model without reading the docs first.

## What `LiteLlm` actually is

ADK was written by Google. It speaks Gemini natively — pass `model="gemini-2.5-flash"` to an `LlmAgent` and ADK goes directly to the `google-genai` SDK. No wrappers, no translation, just a native call.

Every other model needs a translation layer. That layer is **LiteLLM** — an independent open-source library maintained by a separate team. It sits between your code and roughly one hundred LLM providers. Requests come in shaped like OpenAI's API; LiteLLM translates them to whatever the target expects; responses come back translated the other way.

ADK's `LiteLlm` wrapper is a thin adapter that exposes LiteLLM as an ADK-compatible model. Google wrote this adapter precisely so they didn't have to write a custom shim per vendor. Every time LiteLLM adds support for a new provider, ADK inherits it for free.

At runtime, a call to `model=LiteLlm(model="openrouter/anthropic/claude-haiku-4-5")` goes through two translations — OpenAI-shape in, Anthropic-shape out to the provider, Anthropic-shape response back, OpenAI-shape delivered to ADK:

```
ADK Agent
    │ OpenAI-shaped request
    ▼
LiteLlm wrapper
    │
    ▼
LiteLLM ─── Anthropic format ──▶ OpenRouter ──▶ Anthropic API
    ▲                                              │
    └───── Anthropic response ◀── OpenRouter ◀─────┘
    │ OpenAI-shaped response
    ▼
ADK Agent
```

Small overhead. One very real catch: **the translation is version-sensitive**. Bump `google-adk` independently of `litellm` and the shapes of tool-call payloads can drift — adk-python issues #3713 and #4367 in early 2026 were exactly this, with `litellm ≥ 1.81.3` sending a `responseJsonSchema` field that the older ADK wrapper wasn't expecting. The fix was to pin both versions together in `requirements.txt`. Bump them as a pair, never one alone.

## The OpenRouter model-string convention

OpenRouter is a meta-provider. It routes your request to the actual vendor behind a single billing account and a single API key. Five provider keys becomes one OpenRouter key; per-token prices are within about 5% of hitting the providers direct.

The model string has a fixed shape:

```
openrouter/<provider>/<model>[:tier]
```

The providers we use across this course:

| Provider | Model string |
|---|---|
| Google | `openrouter/google/gemini-2.5-flash-lite` |
| OpenAI | `openrouter/openai/gpt-4o-mini` |
| Anthropic | `openrouter/anthropic/claude-haiku-4-5` |
| Qwen | `openrouter/qwen/qwen3-32b` |
| Meta | `openrouter/meta-llama/llama-3.1-8b-instruct` |

The optional `:tier` suffix picks between `:free`, `:beta`, or `:nitro`. Skip it for real work. Free tiers on OpenRouter are aggressively rate-limited and often flaky — they're fine for kicking the tires once, not for a demo that runs reliably every time you open the notebook. The full catalog lives at [openrouter.ai/models](https://openrouter.ai/models).

## The five-provider demo

The notebook for this chapter ships the complete version. The essential shape:

```python
INSTRUCTION = "You explain technical concepts briefly and clearly. Respond in exactly two sentences."

def make_agent(model_string: str) -> LlmAgent:
    return LlmAgent(
        name="swap_tester",
        model=LiteLlm(model=model_string),
        description="Explains concepts in two sentences.",
        instruction=INSTRUCTION,
    )

MODELS = [
    "openrouter/google/gemini-2.5-flash-lite",
    "openrouter/openai/gpt-4o-mini",
    "openrouter/anthropic/claude-haiku-4-5",
    "openrouter/qwen/qwen3-32b",
    "openrouter/meta-llama/llama-3.1-8b-instruct",
]

for m in MODELS:
    agent = make_agent(m)
    answer, elapsed = await ask(agent, "What is a tool-calling agent?")
    print(m, elapsed, answer)
```

Three things to notice when you run this.

**Answers vary in style, converge on content.** Every model explains tool-calling; none hallucinate badly on a vanilla concept. Real quality differences only show up on hard prompts — obscure math, edge-case code, domain-specific reasoning. For common concepts, you cannot pick "the best model" from its answer quality; you pick on latency, cost, or refusal behavior.

**Latency varies by about three times.** Open-weight models served by their current hosting providers are generally slower than the hosted frontier models. For a tool-heavy agent that makes ten sequential tool calls in a turn, three-times-slower multiplies — what was a 2-second turn becomes 6 seconds, which crosses the UX boundary into "this feels broken." For question-answering, barely noticeable.

**Reasoning traces leak from some models.** Qwen and the DeepSeek-R1 variants emit their chain-of-thought even when you didn't ask. You can suppress it with a specific `extra_body={"reasoning": {"effort": "low"}}` parameter, or pick a non-reasoning variant of the model. For a user-facing agent, be aware of this before shipping — you don't want a raw thought stream showing up in your product UI.

## Local models via Ollama — and the prefix gotcha

The most useful trick for offline development: run an open-weight model on your own machine via [Ollama](https://ollama.com) and point ADK at it. Zero cost per call, no network, fully offline. Great for iterating on an agent before you commit to cloud inference costs.

Setup is three commands:

```bash
brew install ollama      # or download from ollama.com
ollama serve             # runs http://localhost:11434
ollama pull qwen3:8b     # downloads the model
```

Then in your ADK code:

```python
agent = LlmAgent(
    model=LiteLlm(model="ollama_chat/qwen3:8b"),
    ...
)
```

**The gotcha** — and this is the single most important sentence in this chapter — LiteLLM supports two Ollama prefixes and they do different things:

| Prefix | Hits | Tool calls |
|---|---|---|
| `ollama/qwen3:8b` | Completions API | Rendered as text the model must produce verbatim. Causes infinite tool-call loops. |
| `ollama_chat/qwen3:8b` | Chat-completions API | Proper function-calling. **This is what you want.** |

Use `ollama_chat/`, always. You will not see the bug on the plain prefix until the agent has tools — without tools, the two prefixes behave identically. The first time you add a tool is when it breaks, and the error message is unhelpful. This is the single most reported issue in the adk-python repository.

If your Ollama server is on a non-standard port, set `OLLAMA_API_BASE=http://localhost:11434` as an environment variable. The default works for most people.

## Native Gemini vs LiteLLM-wrapped Gemini

A clarification that comes up almost every time someone looks closely at the model strings. You can use Gemini two ways in ADK:

```python
# Native — via google-genai SDK
model="gemini-2.5-flash"

# LiteLLM-wrapped — through OpenRouter, OpenAI-shaped
model=LiteLlm(model="openrouter/google/gemini-2.5-flash-lite")
```

Both work. The native form is the default if you pass a plain string. All Gemini-specific features are available there: Google Search grounding, thinking budgets, the Live API, long-context caching. Module 11 through Module 13 use this form exclusively, because those modules teach Gemini-only features that don't exist in the OpenAI-shaped interface.

The LiteLLM-wrapped form is what lets you use Gemini interchangeably with Claude and GPT. Students who only have an OpenRouter key can still run every Part 1 demo. You lose access to Gemini-specific features, but you gain portability.

**Rule of thumb:** LiteLLM-wrapped for Part 1 of this course (vendor-agnostic). Native for Part 2 (Gemini-specific unlocks).

## Interlude — Prompt priority tiers

*From the Agentic Design Patterns publication, Chapter 5. Relevant here because model-swapping exposes a subtlety about how different models weight prompts differently.*

When you swap models, instructions that worked on one model sometimes partially fail on another. Not because the second model is worse — because models weight different parts of the prompt differently. Claude reads through evenly; GPT prioritizes earliest tokens; Gemini has its own pattern. And long instructions get truncated under context pressure: long system prompt plus long tool descriptions plus long chat history can force ADK to drop parts of what you wrote.

The pattern: **structure your system instruction in priority tiers** so if any tier is lost or de-weighted, the rest still produces acceptable behavior.

Three tiers, read top to bottom:

**Tier 1 — Invariants.** Rules the agent must obey under any circumstance. Safety gates, hard refusals, format constraints. Top of the instruction. Short, declarative, non-negotiable.

> *"Never include credit card numbers in output."*
> *"Refuse to generate API keys, secrets, or credentials."*
> *"Always respond in valid JSON."*

**Tier 2 — Core behavior.** The main job description. What the agent is for, what its goals are, what steps it follows.

> *"You help engineers debug build failures by reading logs and suggesting fixes. For any failure: identify the tool that failed, quote the failing line, and propose one fix to try first."*

**Tier 3 — Preferences.** How the agent communicates — length, tone, markdown versus plaintext, bullet points versus prose. Lowest priority. OK to lose first.

> *"Prefer bullet points over paragraphs when listing."*
> *"Keep prose short; engineers prefer code they can read."*

When ADK truncates the instruction under pressure, the earliest tokens survive. Put the things you cannot afford to lose at the top.

A concrete example:

```python
PRIORITY_TIERED_INSTRUCTION = """
# INVARIANTS (highest priority; never violate)
- Do not execute code; only suggest code to run.
- Refuse to generate credentials, API keys, or secrets.
- If asked about a language you don't know, say so; do not guess.

# CORE BEHAVIOR
You are a coding-help assistant for a small engineering team.
For any code question:
1. Identify the programming language.
2. Give a minimal, runnable example that solves the stated problem.
3. Explain the example in 2-3 sentences.

# PREFERENCES
- Use fenced code blocks for code.
- Keep prose short; engineers prefer code they can read.
- When multiple approaches exist, pick one and note alternatives in a trailing line.
"""
```

The payoff shows up in failure modes, not happy paths. Ask a priority-tiered agent to generate an AWS access key and it refuses, even if the last turn of the conversation tried to jailbreak the style preference. Tier 1 survives pressure on Tier 3.

## When to swap models in production

Vendor-neutrality is a **capability**, not a habit. You don't swap models because you can. You swap for specific reasons. Three scenarios where it actually earns its keep.

**Failover.** A provider has an outage. Claude's API goes down, which happens every few months; GPT rate-limits you during a traffic spike; Gemini has a regional incident. A one-line config change sends traffic to a surviving provider. This is the main reason most production ADK deployments bother with LiteLLM at all. Done well, your users don't notice the failover happened.

**Per-task capability.** Different models are genuinely good at different things. GPT-5 reasons better through obscure math. Claude Opus writes cleaner code in several languages. Gemini grounds in live web results natively (a Gemini-only feature, see Module 11). Instead of forcing one model to do everything, compose with `sub_agents` or `AgentTool` (Module 06) and give each sub-agent the model best suited to its task.

**Cost optimization.** A coarse version: route cheap queries to Haiku / GPT-4o-mini / Flash-lite (cents per million tokens); route hard queries to Opus / GPT-5 / Pro (dollars per million). The agent's model parameter can be different per sub-agent. Module 07 (callbacks as middleware) and Module 09 (evaluation) give you the hooks to measure which queries are "hard" and route accordingly.

What you should **not** do: A/B-test model swaps on live users without measurement. Different models have different refusal patterns, different formatting biases, different accuracy profiles on your specific task. What looks like an improvement on your own eye-test can be a regression on 5% of your real user queries you never see. Always swap with eval.

## What to carry forward

Six things from this chapter:

- **`LiteLlm` is a translation layer.** It translates OpenAI-shaped requests to whatever the target provider expects. Version-pin `google-adk` and `litellm` together.
- **OpenRouter model strings** follow `openrouter/<provider>/<model>`. One key replaces five provider keys. Skip `:free` tiers for real work.
- **Ollama prefix rule:** always `ollama_chat/...`, never `ollama/...`. The plain prefix causes infinite tool-call loops.
- **Native vs LiteLLM-wrapped Gemini:** native unlocks Gemini-specific features (Part 2 of this course). LiteLLM-wrapped keeps your code portable (Part 1).
- **Priority tiers in instructions:** invariants → core behavior → preferences. Top survives pressure.
- **Swap models for failover, per-task capability, or cost.** Always with evaluation, never on hunches.

Module 05 picks up composition. One agent is enough for toy demos; real work needs composition. Sequential, Parallel, Loop — three first-class composition primitives. And the canonical ADK wow demo: a Generator+Critic pair refining a draft in a loop until the critic says it's good enough.
