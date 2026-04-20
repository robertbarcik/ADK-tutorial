# Evaluation

The first eight chapters have answered "does the agent work?" by printing events and reading them. That works for demos. It stops working the moment you have more than one use case, more than one agent, more than one prompt iteration. Eyeballing doesn't scale; automated evaluation does.

This chapter introduces ADK's evaluation framework. You describe a conversation as a **test case** — input, expected tool trajectory, expected response — the framework runs the agent against it, scores what actually happened against what you expected, and reports pass or fail. Like a unit test suite, but for agent behavior.

ADK ships two built-in metrics, and one of them — trajectory testing — is the genuine differentiator. The other — ROUGE-1 response match — needs honest framing.

## The two metrics

| Metric | Asks | Scale | Default threshold |
|---|---|---|---|
| `tool_trajectory_avg_score` | Did the agent call the right tools in the right order with the right args? | 0–1 | 1.0 (strict) |
| `response_match_score` | How similar is the actual response to the expected one? | 0–1 (ROUGE-1) | 0.8 |

### Trajectory is the novel one

Most evaluation frameworks for LLM agents score only the final output — did the answer look right? ADK weights *how the agent got there* equally. For tool-heavy agents, this is the correct framing.

A correct answer via the wrong reasoning is a bug waiting to happen. If your agent answered correctly today by skipping a verification step or by calling a tool you didn't expect, you were lucky — tomorrow's slightly different input will expose the structural problem. Trajectory testing catches this class of bug immediately; response-only testing misses it.

### Response match uses ROUGE-1 — and ROUGE-1 is weak

ROUGE-1 is unigram overlap between expected and actual text. Great for machine translation benchmarks where the answer space is narrow. Weak for free-form agent responses where the same information can be expressed in many ways.

The default threshold of 0.8 means "80% of the words in the expected response must appear in the actual response." In practice this fails on semantically-correct answers that happen to use different wording — which is most of them. You will fight this metric as you iterate your agent.

The honest summary: **trajectory testing is useful; ROUGE-1 response matching is weak.** Use trajectory strictly. Use response match loosely or not at all, and plan for LLM-as-judge as the real upgrade.

## The `.test.json` format

Eval files are JSON documents with one or more test cases. The canonical shape for a minimal case:

```json
{
  "eval_set_id": "weather_basic",
  "name": "weather basic",
  "description": "One test case for the weather agent.",
  "eval_cases": [
    {
      "eval_id": "case_prague",
      "conversation": [
        {
          "invocation_id": "inv-1",
          "user_content": {
            "parts": [{"text": "What is the weather in Prague?"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "The weather in Prague is cloudy and 14 degrees Celsius."}],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "get_weather", "args": {"city": "Prague"}}
            ],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "weather_agent",
        "user_id": "tester",
        "state": {}
      }
    }
  ]
}
```

Each case has a conversation. Each turn in the conversation has user input, expected final response, and expected intermediate data (the tool calls the agent should make along the way). Optionally, a `session_input` pre-populates the state.

You can hand-author these — fine for a one-off test. In practice, author them from the dev UI: run `adk web`, have a conversation you're happy with, click "Save as eval," enter a name. ADK writes exactly this format. The programmatic path and the UI path produce identical files.

## The eval loop in daily use

Three commands:

```bash
# Step 1: run the agent in the dev UI
adk web

# ... chat, click "Save as eval", name it

# Step 2: run the evals
adk eval ./my_agent ./my_agent/my_evals.test.json

# Step 3: tweak the agent; re-run
adk eval ./my_agent ./my_agent/my_evals.test.json
```

Chat, save, tweak, re-run. The loop is fast enough to use while prototyping — a few seconds per eval run on a simple agent. Build your evalset incrementally: when the agent handles something tricky, save it. Over a few weeks you accumulate dozens of cases that protect against regressions.

The programmatic API exposed in the notebook (`AgentEvaluator.evaluate(agent_module=..., eval_dataset_file_path_or_dir=...)`) does the same thing without the CLI. Handy for unit-test integration — the eval becomes a `pytest` case.

## The ROUGE-1 failure mode — live

The notebook runs an eval with a deliberately strict threshold of 0.95. It fails, and the failure is the teaching moment.

```
expected:  "The weather in Prague is cloudy and 14 degrees Celsius."
actual:    "The weather in Prague is cloudy, and the temperature is 14 degrees Celsius."

response_match_score: 0.87  (threshold 0.95)  → FAIL
```

Same information, different words. The trajectory score was 1.0 — the agent called the right tool. The entire failure is stylistic. ROUGE-1 counts overlapping unigrams; "cloudy, and the temperature is" replaces "cloudy and" with more words, and the count drops.

In practice, this means:
- **Don't use 0.8 as a threshold.** Relax to 0.6 for short responses. Give up on the metric entirely for long-form text.
- **Don't chase the metric.** Tweaking an agent's prompt to pass ROUGE-1 optimizes for word choice, not correctness. That's backwards.
- **Do use LLM-as-judge for production.** ROUGE-1 is fine as a structural sanity check — did the agent even produce a response with the right shape? — and nothing more.

## LLM-as-judge: the production upgrade

The pattern: for each test case, after running the agent and capturing the actual response, call a **second** LLM with the prompt, the expected answer, and the actual answer. Ask it to score semantic correctness.

```python
# Sketch — not built into ADK < 1.29, straightforward to wire up
def judge(prompt, expected, actual) -> float:
    response = judge_llm(
        f"Is this a reasonable answer to the prompt?\n"
        f"Prompt: {prompt}\n"
        f"Expected: {expected}\n"
        f"Actual: {actual}\n"
        f"Score 0-1 on semantic correctness. Just the number."
    )
    return float(response.strip())
```

ADK 1.29+ ships a Gen AI Evaluation Service integration that does this built-in (public preview). Vertex AI users point their eval sets at it and get LLM-graded metrics alongside trajectory. Self-hosted deployments wire the judge themselves — a second LiteLLM call with a grading rubric.

The framing shift is what matters: trajectory asks *did the agent do the right things*; LLM-judge asks *did it say the right thing*. Both matter; neither is ROUGE-1.

## A full evaluation strategy

In real projects, evaluation is not one layer. It's four, run at different cadences:

| Layer | Answers | Cost | When to run |
|---|---|---|---|
| **Trajectory score** | Did it call the right tools in the right order? | Free (structural) | On every PR |
| **ROUGE-1 response match** | Is the text lexically close? | Free, weak signal | For regressions only |
| **LLM-as-judge** | Is the answer semantically correct? | One extra LLM call per case | Nightly or pre-release |
| **Human review** | Is it actually good? | Expensive; unavoidable | For flagged cases, high-stakes deployments |

You don't pick one. You combine them. Trajectory gives fast, deterministic CI signal. LLM-as-judge gives semantic scoring at moderate cost. Human review is the tail — the cases the automated layers flag as uncertain, plus new-agent deployments, plus customer-reported issues.

## Production gotcha — read-only filesystems

Worth naming before you deploy. `adk eval` **writes files back to the `agents_dir`** during eval runs — it persists updated session histories into the directory containing your agent. If your deployment image has a read-only root filesystem — a common Kubernetes hardening pattern — eval runs hit `PermissionError`.

Upstream issue: adk-python #3887.

**Workaround:** either make the `agents_dir` writable during eval runs (mount a writable volume), or run eval **outside** the deployed image. Most real deployments do the latter: the agent code is the same in production and in CI, but eval runs in CI against a fresh checkout, not inside the locked-down production image. Doesn't block classroom use; becomes a real concern as you wire eval into a production CI/CD pipeline.

## What to carry forward

- **Two built-in metrics**: `tool_trajectory_avg_score` (strict, useful) and `response_match_score` (ROUGE-1, weak).
- **Trajectory is ADK's differentiated contribution to eval.** Use it strictly. Lock in the tool-call path.
- **ROUGE-1 punishes stylistic variation.** Don't chase the default 0.8 threshold. Relax, or replace with LLM-as-judge.
- **LLM-as-judge is the production upgrade.** ADK 1.29+ ships a Gen AI Evaluation Service path; self-host with a second LiteLLM call.
- **`.test.json`** authored by hand or saved from `adk web`. Build evalsets incrementally as you iterate.
- **`adk eval`** writes to `agents_dir` — breaks in read-only containers. Run eval outside the deployed image.
- **Full strategy**: trajectory on every PR; LLM-judge nightly; human review at the tail. Don't pick one.

Module 10 — the last module of Part 1 — picks up **deployment**. `adk deploy cloud_run` as the one-command story, a vanilla Dockerfile that runs the same agent on any cloud, Vertex AI Agent Engine mentioned as the opinionated managed path. Then Part 2 begins: Gemini-specific features you lose when you're vendor-neutral.
