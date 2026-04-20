# M09 — Speaker notes

Spoken delivery. One section per slide.

---

## Slide 1 — Title

Module nine. Evaluation. The first eight modules have all ended with "does it work? let's look at the event stream." That's fine for demos. It doesn't scale. As soon as you have more than one use case, more than one agent, more than one prompt iteration, eyeballing stops being enough. Module nine is where we stop eyeballing.

---

## Slide 2 — Eight modules / eyeballing

The frame. Eight modules of "does the agent work?" answered by looking at printed output. Today we replace that with tests that run automatically, on every change, and report pass-or-fail against named criteria.

---

## Slide 3 — Two metrics

ADK ships two built-in evaluation metrics out of the box.

The first — tool_trajectory_avg_score — asks: did the agent call the right tools in the right order, with the right arguments? Scale zero to one. Default threshold is one-point-zero — strict, exact match.

The second — response_match_score — asks: how close is the agent's actual final response to the expected one? Scale zero to one, calculated as ROUGE-1 unigram overlap. Default threshold is zero-point-eight.

The trajectory metric is the novel one. Most eval frameworks on the market score only outputs — did the agent's final answer look right? ADK adds how-it-got-there as equal-weight information. That matches reality for tool-heavy agents.

---

## Slide 4 — Why trajectory matters

The framing, on one slide. A correct answer reached via the wrong reasoning is a bug waiting to happen. If your agent gave a correct answer today by calling the wrong tool or skipping a required verification step, it will fail on a slightly different input tomorrow — and the failure will be confusing because the previous correct answer fooled you.

Trajectory testing catches this. It locks in the reasoning path, not just the output. If the agent stops using the tool you expected, you see it on the next CI run, not after a customer complains.

---

## Slide 5 — The eval loop

The daily workflow. Three commands and a feedback loop.

Run `adk web` locally. Have a conversation with your agent. When the agent does something good — answers correctly, calls the right tools, handles an edge case — click the "Save as eval" button. That exports the conversation as a dot-test-dot-json file next to your agent code.

Run `adk eval` pointed at your agent directory and the eval file. It runs all the test cases, scores them against the thresholds, reports pass or fail.

Tweak the agent. Change an instruction, add a tool, swap a model. Re-run eval. Repeat.

The loop is fast enough to use while prototyping. Build your evalset incrementally as you iterate. When an agent handles something tricky, save it. Weeks later you have dozens of cases protecting against regressions.

---

## Slide 6 — Minimal test.json

Here's what a test file looks like. Each case has a conversation; each turn has three parts. What the user says. What the agent should ultimately reply with. What tools the agent should call along the way.

You can hand-author these or save them from the dev UI. For a one-off test, hand-author is fine. For a real project, always save from the UI — it captures the exact event structure ADK expects, including invocation IDs and response content shapes you'd otherwise have to read the schema for.

---

## Slide 7 — Live: strict eval fails

Switch to the notebook. Cell thirteen. We run the evaluator with a deliberately strict threshold of 0.95 on response match. Watch what happens.

---

## Slide 8 — The failure tells a story

Back on the slide. Here's what cell thirteen showed.

Expected response — "The weather in Prague is cloudy and 14 degrees Celsius." Actual response — "The weather in Prague is cloudy, and the temperature is 14 degrees Celsius." Response match score: 0.87 against a threshold of 0.95. Failed.

Same information. Different words. "Cloudy and 14 degrees" versus "cloudy, and the temperature is 14 degrees" — if you read those aloud to a human, they'd score them equivalent. ROUGE-1 scores them 0.87.

And notice: the trajectory score was a clean 1.0. The agent did the right thing structurally. The failure is entirely about wording.

---

## Slide 9 — The honest summary

The honest summary. Trajectory testing is useful. ROUGE-1 response matching is weak.

ROUGE-1 punishes legitimate stylistic variation. It's fine as a gross sanity check — did the output contain at least some of the expected words? — but it's not a reliable proxy for correctness. Don't rely on it for production evaluation.

---

## Slide 10 — Working range

What people actually do. A test_config.json next to your test file lets you override the default thresholds.

Keep trajectory strict — 1.0 exact match on tool calls. You want to know immediately if the agent starts doing something different.

For response match, the working range is 0.6 to 0.7 for short text. Below that, almost anything passes. Above that, stylistic variation fails tests. For long-form text — multi-paragraph summaries, explanations — just give up on response_match_score. It's not the right tool for that job.

Dropping the threshold isn't a win. It's an admission the metric is the wrong tool. The real upgrade is LLM-as-judge.

---

## Slide 11 — LLM-as-judge

LLM-as-judge is the production pattern. The pseudocode on the slide: for each test case, run the agent, capture the actual response, call a SECOND LLM with the prompt, the expected answer, and the actual answer. Ask it to score semantic correctness. Get a number back.

ADK 1.29 and later ships a Gen AI Evaluation Service integration that does this built-in — public preview at time of recording. Vertex AI users point their eval sets at it; Google runs the judge for you. For self-hosted work, you wire the judge yourself — a separate LiteLLM call, a grading rubric in the prompt, the score as the output.

The key shift is framing. Trajectory asks: did the agent do the right things? LLM-judge asks: did it say the right thing? Both matter. Neither is ROUGE-1.

---

## Slide 12 — Full picture

The full picture. Four evaluation layers, combined at different cadences in production.

Trajectory score on every pull request. Fast, deterministic, catches structural regressions.

ROUGE-1 as a rough regression check. Don't trust the number; trust the trend.

LLM-as-judge nightly. More expensive — a second LLM call per test case — but it catches the things ROUGE-1 misses. Run it on your full evalset; look at the ones it flags.

Human review at the tail. Unavoidable. For the cases that matter most — new agent deployments, customer-reported issues, high-stakes tasks — a human eyeballs the actual responses. Weekly or per-release cadence.

You don't pick one. You combine them at appropriate cadences.

---

## Slide 13 — Production gotcha

One more gotcha worth naming. `adk eval` writes files back to the agents_dir — it persists updated session histories for the eval runs. If your deployment image is read-only, common in Kubernetes with read-only root filesystems, eval hits a PermissionError.

Upstream issue: adk-python number 3887.

The workaround is straightforward: either mount the agents_dir as writable during eval runs, or run eval outside the deployed image. In CI. On a developer machine. In a separate eval pipeline. The agent code is the same; the runtime environment is different. Doesn't block classroom use; becomes a real concern when you wire eval into CI/CD against a production-shaped container.

---

## Slide 14 — What to carry forward

What to carry forward. Test trajectory strictly — that's the high-value metric ADK gives you that nobody else does as cleanly. Test response quality with LLM-as-judge, not ROUGE-1, for any real work. Don't trust ROUGE-1 past the sanity-check tier.

---

## Slide 15 — Next

Module ten. The last module of Part 1. Deployment. `adk deploy cloud_run` as the one-command story, a vanilla Dockerfile that runs the same agent on any cloud, a brief look at Vertex AI Agent Engine as the opinionated managed path. Then Part 2 begins — Gemini-specific features you lose when you're vendor-neutral.
