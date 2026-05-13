# M09 — Speaker notes

---

## Slide 1 — Title

Evaluation. That's the topic of this module, and it's the natural next step now that we know how to build agents that actually work. We'll cover ADK's two built-in evaluation metrics, why one of them is a clean win and the other one is mostly weak, and the daily workflow for catching regressions in your agents before they reach customers.

---

## Slide 2 — Up to now / This module

The framing for today is on the slide. We've been answering "does the agent work?" by looking at printed output, the way you would during prototyping. In this module, we replace that with tests that run automatically, on every change, and report pass-or-fail against named criteria.

---

## Slide 3 — Two built-in metrics

ADK ships two built-in evaluation metrics out of the box, and they sit at opposite ends of what you'd want to check.

The first one is `tool_trajectory_avg_score`, which asks: did the agent call the right tools, in the right order, with the right arguments? The scale is zero to one, and the default threshold is one-point-zero. Strict, exact match.

The second one is `response_match_score`, which asks: how close is the agent's actual final response to the expected one? Same zero-to-one scale, calculated as ROUGE-1 unigram overlap, with a default threshold of zero-point-eight.

The trajectory metric is really the novel one. Most eval frameworks on the market score only outputs, meaning they ask whether the agent's final answer looks right. ADK adds how-it-got-there as equal-weight information. And that really matches reality for tool-heavy agents.

---

## Slide 4 — Why trajectory matters

So why does trajectory matter so much? The core point is on the slide: a correct answer reached via the wrong reasoning is a bug waiting to happen. If your agent gave a correct answer today by calling the wrong tool, or by skipping a required verification step, it will fail on a slightly different input tomorrow. And the failure will be confusing, because the previous correct answer fooled you into thinking the agent was working.

That's exactly what trajectory testing catches. It locks in the reasoning path, not just the output. So if the agent stops using the tool you expected, you see it on the next CI run, not after a customer complains.

---

## Slide 5 — The eval loop

Let me walk through what the daily workflow looks like. Three commands and a feedback loop.

First, run `adk web` locally and have a conversation with your agent. When the agent does something good, whether it's answering correctly, calling the right tools, or handling an edge case, click the "Save as eval" button. That exports the conversation as a `.test.json` file, right next to your agent code.

Second, run `adk eval` pointed at your agent directory and the eval file. It runs all the test cases, scores them against the thresholds, and reports pass or fail.

Third, tweak the agent. Change an instruction, add a tool, swap a model. Re-run eval. Repeat.

The loop is fast enough to use while prototyping, so build your evalset incrementally as you iterate. When an agent handles something tricky, save it. Weeks later, you'll have dozens of cases protecting against regressions.

---

## Slide 6 — A minimal test.json

What a test file actually looks like is on the slide. Each case has a conversation, and each turn has three parts: what the user says, what the agent should ultimately reply with, and what tools the agent should call along the way.

You can hand-author these, or save them from the dev UI. For a one-off test, hand-authoring is fine. For a real project, though, always save from the UI. It captures the exact event structure ADK expects, including things like invocation IDs and response content shapes that you'd otherwise have to read the schema for.

---

### Notebook break — Strict eval reveals the ROUGE-1 weakness

[Switch the screen to the notebook.]

Let me run the evaluator with a deliberately strict threshold of zero-point-nine-five on response match. The expected answer is one phrasing of the weather; the agent's actual answer is a slightly different phrasing of the same fact. [Run the cell.] Watch the output. The trajectory score is a perfect one-point-zero, so the agent did the right thing structurally. But the response match score comes in at zero-point-eight-seven, against the threshold of zero-point-nine-five. So the test fails, even though a human reading the two sentences would call them equivalent.

[Switch back to the slide deck.]

---

## Slide 7 — The failure tells a story

So what did that run actually show us? Let me walk through the numbers, which you can see on the slide.

Expected response: "The weather in Prague is cloudy and 14 degrees Celsius." Actual response: "The weather in Prague is cloudy, and the temperature is 14 degrees Celsius." Response match score: zero-point-eight-seven, against a threshold of zero-point-nine-five. Failed.

Same information. Different words. "Cloudy and 14 degrees" versus "cloudy, and the temperature is 14 degrees". If you read those aloud to a human, they'd score them equivalent. ROUGE-1, on the other hand, scores them zero-point-eight-seven.

And notice the other half of the picture: the trajectory score was a clean one-point-zero. The agent did the right thing structurally. The failure is entirely about wording.

---

## Slide 8 — The honest summary

Time for the honest summary. Trajectory testing is useful. ROUGE-1 response matching, on the other hand, is weak.

ROUGE-1 punishes legitimate stylistic variation. It's fine as a gross sanity check, asking whether the output contained at least some of the expected words. But it's really not a reliable proxy for correctness. So don't rely on it for production evaluation.

---

## Slide 9 — Adjust the thresholds

So what should you actually do in practice? A `test_config.json` file, placed next to your test file, lets you override the default thresholds.

First, keep trajectory strict. Set it at one-point-zero for exact match on tool calls. You want to know immediately if the agent starts doing something different.

Second, for response match, the working range is roughly zero-point-six to zero-point-seven for short text. Below that, almost anything passes. Above that, stylistic variation fails tests. And for long-form text, like multi-paragraph summaries or explanations, just give up on `response_match_score` entirely. It's not the right tool for that job.

Dropping the threshold isn't a win. It's really an admission that the metric is the wrong tool. Which is why the real upgrade is LLM-as-judge.

---

## Slide 10 — LLM-as-judge

LLM-as-judge is the production pattern, and the pseudocode on the slide sketches the idea. For each test case, you run the agent, capture the actual response, and then call a second LLM with the prompt, the expected answer, and the actual answer. Ask that second LLM to score semantic correctness. Get a number back.

ADK 1.29 and later ships a Gen AI Evaluation Service integration that does this built-in, currently in public preview at time of recording. Vertex AI users can point their eval sets at it, and Google runs the judge for you. For self-hosted work, you wire the judge yourself: a separate LiteLLM call, a grading rubric in the prompt, and the score as the output.

The key shift here is really the framing. Trajectory asks: did the agent do the right things? LLM-judge asks: did it say the right thing? Both matter. Neither is ROUGE-1.

---

## Slide 11 — The full picture

The slide pulls together the full picture: four evaluation layers, combined at different cadences in production.

First, trajectory score on every pull request. Fast, deterministic, catches structural regressions.

Second, ROUGE-1 as a rough regression check. Don't trust the number; trust the trend.

Third, LLM-as-judge nightly. It's more expensive, because it adds a second LLM call per test case, but it catches the things ROUGE-1 misses. Run it on your full evalset, and look at the ones it flags.

And finally, human review at the tail. Unavoidable. For the cases that matter most, like new agent deployments, customer-reported issues, or high-stakes tasks, a human eyeballs the actual responses. Weekly or per-release cadence.

So you don't pick one. You combine them at appropriate cadences.

---

## Slide 12 — Production gotcha: read-only filesystems

Before we wrap up, there's one more gotcha worth naming. `adk eval` writes files back to the agents directory; it persists updated session histories for the eval runs. So if your deployment image is read-only, which is common in Kubernetes with read-only root filesystems, eval hits a PermissionError.

The upstream issue is adk-python number 3887.

The workaround is straightforward. Either mount the agents directory as writable during eval runs, or run eval outside the deployed image: in CI, on a developer machine, or in a separate eval pipeline. The agent code is the same; only the runtime environment is different. It doesn't block classroom use, but it becomes a real concern when you wire eval into CI/CD against a production-shaped container.

---

## Slide 13 — What to carry forward

So what should you carry forward from this module? Three things really matter.

The first is to test trajectory strictly. That's the high-value metric ADK gives you that nobody else does as cleanly, so use it.

The second is to test response quality with LLM-as-judge, not ROUGE-1, for any real work. The pseudocode pattern from a few slides ago is the foundation; ADK's Vertex integration packages it for you if you're on that path.

And the third is to not trust ROUGE-1 past the sanity-check tier. It's useful as a low-effort regression signal. It is not a measure of correctness, and acting on its number as if it were one will mislead you.

---

## Slide 14 — Up next

Up next, deployment. We'll cover `adk deploy cloud_run` as the one-command story, a vanilla Dockerfile that runs the same agent on any cloud, and a brief look at Vertex AI Agent Engine as the opinionated managed path. After that, Part 2 of the course begins, where we get into the Gemini-specific features you lose by going fully vendor-neutral. See you there.
