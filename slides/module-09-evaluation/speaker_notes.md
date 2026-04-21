# M09 — Speaker notes

---

## Slide 1 — Title

Welcome to module nine, which is all about evaluation. The first eight modules have all ended with the same question — "does it work? let's look at the event stream." That's fine for demos, but it really doesn't scale. As soon as you have more than one use case, more than one agent, or more than one prompt iteration, eyeballing just stops being enough. So module nine is where we stop eyeballing and start testing.

---

## Slide 2 — Eight modules / eyeballing

Let me frame the problem we're solving today. For eight modules, we've answered "does the agent work?" by looking at printed output. In this module, we replace that with tests that run automatically, on every change, and report pass-or-fail against named criteria.

---

## Slide 3 — Two metrics

ADK ships two built-in evaluation metrics out of the box, and they sit at opposite ends of what you'd want to check.

The first one — tool_trajectory_avg_score — asks: did the agent call the right tools, in the right order, with the right arguments? Scale zero to one. The default threshold is one-point-zero, so strict, exact match.

The second one — response_match_score — asks: how close is the agent's actual final response to the expected one? Scale zero to one, calculated as ROUGE-1 unigram overlap. The default threshold here is zero-point-eight.

The trajectory metric is really the novel one. Most eval frameworks on the market score only outputs — that is, did the agent's final answer look right? ADK, on the other hand, adds how-it-got-there as equal-weight information. And that really matches reality for tool-heavy agents.

---

## Slide 4 — Why trajectory matters

So why does trajectory matter so much? If you remember one thing from this slide, remember that a correct answer reached via the wrong reasoning is a bug waiting to happen. If your agent gave a correct answer today by calling the wrong tool, or by skipping a required verification step, it will fail on a slightly different input tomorrow — and the failure will be confusing, because the previous correct answer fooled you.

That's exactly what trajectory testing catches. It locks in the reasoning path, not just the output. So if the agent stops using the tool you expected, you see it on the next CI run, not after a customer complains.

---

## Slide 5 — The eval loop

Let me walk through what the daily workflow looks like — three commands and a feedback loop.

First, run `adk web` locally. Have a conversation with your agent. When the agent does something good — like answering correctly, calling the right tools, or handling an edge case — click the "Save as eval" button. That exports the conversation as a dot-test-dot-json file, right next to your agent code.

Second, run `adk eval` pointed at your agent directory and the eval file. It runs all the test cases, scores them against the thresholds, and reports pass or fail.

Third, tweak the agent. Change an instruction, add a tool, swap a model. Re-run eval. Repeat.

The loop is fast enough to use while prototyping, so build your evalset incrementally as you iterate — when an agent handles something tricky, save it. Weeks later, you'll have dozens of cases protecting against regressions.

---

## Slide 6 — Minimal test.json

What a test file actually looks like is on the slide. Each case has a conversation, and each turn has three parts — what the user says, what the agent should ultimately reply with, and what tools the agent should call along the way.

You can hand-author these, or save them from the dev UI. For a one-off test, hand-authoring is fine. But for a real project, always save from the UI — it captures the exact event structure ADK expects, including things like invocation IDs and response content shapes that you'd otherwise have to read the schema for.

---

## Slide 7 — Live: strict eval fails

Switch to the notebook, cell thirteen. We run the evaluator with a deliberately strict threshold of 0.95 on response match. Watch what happens.

---

## Slide 8 — The failure tells a story

So what did cell thirteen actually show us? Let me walk through the numbers.

Expected response — "The weather in Prague is cloudy and 14 degrees Celsius." Actual response — "The weather in Prague is cloudy, and the temperature is 14 degrees Celsius." Response match score: 0.87, against a threshold of 0.95. Failed.

Same information. Different words. "Cloudy and 14 degrees" versus "cloudy, and the temperature is 14 degrees" — if you read those aloud to a human, they'd score them equivalent. ROUGE-1, on the other hand, scores them 0.87.

And notice the other half of the picture: the trajectory score was a clean 1.0. The agent did the right thing structurally. As a result, the failure is entirely about wording.

---

## Slide 9 — The honest summary

Time for the honest summary. Trajectory testing is useful. ROUGE-1 response matching, on the other hand, is weak.

ROUGE-1 punishes legitimate stylistic variation. It's fine as a gross sanity check — did the output contain at least some of the expected words? — but it's really not a reliable proxy for correctness. So don't rely on it for production evaluation.

---

## Slide 10 — Working range

So what should you actually do in practice? A test_config.json file, placed next to your test file, lets you override the default thresholds.

First, keep trajectory strict — 1.0, exact match on tool calls. You want to know immediately if the agent starts doing something different.

Second, for response match, the working range is 0.6 to 0.7 for short text. Below that, almost anything passes. Above that, stylistic variation fails tests. And for long-form text — things like multi-paragraph summaries or explanations — just give up on response_match_score. It's not the right tool for that job.

Dropping the threshold isn't a win. It's really an admission that the metric is the wrong tool. Which is why the real upgrade is LLM-as-judge.

---

## Slide 11 — LLM-as-judge

LLM-as-judge is the production pattern, and the pseudocode on the slide sketches the idea. For each test case, run the agent, capture the actual response, then call a SECOND LLM with the prompt, the expected answer, and the actual answer. Ask it to score semantic correctness. Get a number back.

ADK 1.29 and later ships a Gen AI Evaluation Service integration that does this built-in — public preview at time of recording. Vertex AI users can point their eval sets at it, and Google runs the judge for you. For self-hosted work, on the other hand, you wire the judge yourself — so a separate LiteLLM call, a grading rubric in the prompt, and the score as the output.

The key shift here is really the framing. Trajectory asks: did the agent do the right things? LLM-judge asks: did it say the right thing? Both matter. Neither is ROUGE-1.

---

## Slide 12 — Full picture

What you see on this slide is the full picture — four evaluation layers, combined at different cadences in production.

First, trajectory score on every pull request. Fast, deterministic, catches structural regressions.

Second, ROUGE-1 as a rough regression check. Don't trust the number; trust the trend.

Third, LLM-as-judge nightly. It's more expensive — a second LLM call per test case — but it catches the things ROUGE-1 misses. Run it on your full evalset, and look at the ones it flags.

And finally, human review at the tail. Unavoidable. For the cases that matter most — like new agent deployments, customer-reported issues, or high-stakes tasks — a human eyeballs the actual responses. Weekly or per-release cadence.

So you don't pick one. You combine them at appropriate cadences.

---

## Slide 13 — Production gotcha

Before we wrap up, there's one more gotcha worth naming. `adk eval` writes files back to the agents_dir — it persists updated session histories for the eval runs. So if your deployment image is read-only, which is common in Kubernetes with read-only root filesystems, eval hits a PermissionError.

The upstream issue is adk-python number 3887.

The workaround is straightforward. Either mount the agents_dir as writable during eval runs, or run eval outside the deployed image — in CI, on a developer machine, or in a separate eval pipeline. The agent code is the same; just the runtime environment is different. It doesn't block classroom use, but it becomes a real concern when you wire eval into CI/CD against a production-shaped container.

---

## Slide 14 — What to carry forward

So what should you carry forward from this module? First, test trajectory strictly — that's the high-value metric ADK gives you that nobody else does as cleanly. Second, test response quality with LLM-as-judge, not ROUGE-1, for any real work. And third, don't trust ROUGE-1 past the sanity-check tier.

---

## Slide 15 — Next

Up next in module ten — the last module of Part 1 — we turn to deployment. We'll cover `adk deploy cloud_run` as the one-command story, a vanilla Dockerfile that runs the same agent on any cloud, and a brief look at Vertex AI Agent Engine as the opinionated managed path. Then Part 2 begins — the Gemini-specific features you lose when you're vendor-neutral.
