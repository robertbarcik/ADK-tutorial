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

The first one is `tool_trajectory_avg_score`, and it asks whether the agent called the right tools, in the right order, and with the right arguments. The scale is zero to one, and the default threshold is one-point-zero, meaning you get an exact match on every tool call or the test fails.

The second one is `response_match_score`, and it asks how close the agent's actual final response is to the expected one. The scale is again zero to one, calculated as ROUGE-1 unigram overlap, with a default threshold of zero-point-eight.

The trajectory metric is really the novel one. Most eval frameworks on the market score only outputs, meaning they ask whether the agent's final answer looks right. ADK adds how-it-got-there as equal-weight information. And that really matches reality for tool-heavy agents.

---

## Slide 4 — Why trajectory matters

So why does trajectory matter so much? The core point on the slide is this. A correct answer reached via the wrong reasoning is a bug waiting to happen. If your agent gave a correct answer today by calling the wrong tool, or by skipping a required verification step, it will fail on a slightly different input tomorrow. And the failure will be confusing, because the previous correct answer fooled you into thinking the agent was working.

That's exactly what trajectory testing catches. It locks in the reasoning path, not just the output. So if the agent stops using the tool you expected, you'll see it on the next CI run, not after a customer complains.

---

## Slide 5 — The eval loop

Let me walk through what the daily workflow looks like. It's really just three commands that fit into a tight feedback loop, and you'll be running this loop while you iterate on your agent.

First, run `adk web` locally and have a conversation with your agent. When the agent does something good, whether it's answering correctly, calling the right tools, or handling an edge case, click the "Save as eval" button. That exports the conversation as a `.test.json` file, right next to your agent code.

Second, run `adk eval` pointed at your agent directory and the eval file. It runs all the test cases, scores them against the thresholds, and reports pass or fail for each one.

Third, you go back and tweak the agent. Maybe you change an instruction, add a new tool, or swap to a different model. Then you re-run `adk eval` to see whether the change helped, and you repeat the whole cycle.

The loop is fast enough to use while prototyping, so build your evalset incrementally as you iterate. Whenever an agent handles something tricky, save that conversation as a test case. Weeks later, you'll have dozens of these cases quietly protecting against regressions.

---

## Slide 6 — A minimal test.json

What a test file actually looks like is on the slide. Each case is a conversation, and inside each turn you declare three things. The first is what the user says. The second is what the agent should ultimately reply with. And the third is what tools the agent should call along the way.

You can hand-author these files, or save them from the dev UI. For a one-off test, hand-authoring is fine. For a real project, though, always save from the UI. It captures the exact event structure ADK expects, including things like invocation IDs and response content shapes that you'd otherwise have to read the schema for.

---

### Notebook break — Strict eval reveals the ROUGE-1 weakness

[Switch the screen to the notebook.]

Let me run the evaluator with a deliberately strict threshold of zero-point-nine-five on response match. The expected answer is one phrasing of the weather, while the agent's actual answer is a slightly different phrasing of the same fact. [Run the cell.] Watch the output. The trajectory score comes back as a perfect one-point-zero, so the agent did the right thing structurally. But the response match score lands at zero-point-eight-seven, against the threshold of zero-point-nine-five. The test fails, even though a human reading the two sentences would call them equivalent.

[Switch back to the slide deck.]

---

## Slide 7 — The failure tells a story

So what did that run actually show us? Let me walk through the numbers, which you can see on the slide.

The expected response was "The weather in Prague is cloudy and 14 degrees Celsius." The agent's actual response was "The weather in Prague is cloudy, and the temperature is 14 degrees Celsius." The response-match score came in at zero-point-eight-seven, against a threshold of zero-point-nine-five, so the test failed.

Both sentences carry the same information, just in slightly different words. The first one says "cloudy and 14 degrees", and the second one says "cloudy, and the temperature is 14 degrees". If you read those aloud to a human, they would score them as equivalent. ROUGE-1, on the other hand, scores them at zero-point-eight-seven.

And notice the other half of the picture. The trajectory score came back as a clean one-point-zero, which means the agent did the right thing structurally. The failure here is entirely about wording.

---

## Slide 8 — The honest summary

Let me give you the honest summary of what we just saw. Trajectory testing is genuinely useful, and you should be running it on every change. ROUGE-1 response matching, on the other hand, is a weak metric, and you'll want to be careful with how you use it in practice.

ROUGE-1 punishes legitimate stylistic variation. It's fine as a gross sanity check, asking whether the output contained at least some of the expected words. But it's really not a reliable proxy for correctness, which means you shouldn't rely on it for production evaluation.

---

## Slide 9 — Adjust the thresholds

So what should you actually do in practice? The first step is to override the default thresholds, which you do by placing a `test_config.json` file next to your test file. Here's what I'd recommend you put in there.

For trajectory, you keep it strict. Set it at one-point-zero for exact match on tool calls, because you want to know immediately if the agent starts doing something different than what it used to do.

For response match, the working range is roughly zero-point-six to zero-point-seven for short text. Below that, almost anything passes the test. Above that, even legitimate stylistic variation fails it. And for long-form text, like multi-paragraph summaries or explanations, just give up on `response_match_score` entirely, because it's not the right tool for that job.

Now, I'll be honest with you. Dropping the threshold isn't really a win. It's more of an admission that the metric itself is the wrong tool for measuring response quality. And that's exactly why the real upgrade is LLM-as-judge, which the next slide gets into.

---

## Slide 10 — LLM-as-judge

LLM-as-judge is the production pattern for evaluating response quality, and the pseudocode on the slide sketches the idea. For each test case, you run the agent and capture its actual response. Then you call a second LLM, passing it the original prompt, the expected answer, and the actual response. You ask that second LLM to score semantic correctness, and you get a number back.

ADK 1.29 and later ships a Gen AI Evaluation Service integration that does this for you out of the box, currently in public preview at time of recording. If you're on Vertex AI, you can point your eval sets at it, and Google runs the judge for you. For self-hosted work, you wire the judge yourself with a separate LiteLLM call, a grading rubric written into the prompt, and the score returned as the output.

The key shift here is really in the framing. Trajectory testing asks whether the agent did the right things along the way. LLM-as-judge, on the other hand, asks whether the agent said the right thing in its final answer. Both questions matter for real-world correctness, and neither of them is answered by ROUGE-1.

---

## Slide 11 — The full picture

The slide pulls together the full picture of what production-grade evaluation looks like. There are four evaluation layers, and you combine them at different cadences so they reinforce each other.

The first layer is the trajectory score, which you run on every pull request. It's fast, it's deterministic, and it catches structural regressions early, before they reach customers.

The second layer is ROUGE-1, used as a rough regression check rather than a real quality measure. What matters here isn't the absolute number, but how that number trends over time.

The third layer is LLM-as-judge, which you'd run nightly rather than on every PR. It's more expensive than the first two, because it adds a second LLM call per test case, but it catches the things ROUGE-1 misses. You point it at your full evalset and review the cases it flags as borderline.

And the fourth layer is human review, sitting at the tail of the pipeline. This one is unavoidable for the cases that really matter, like new agent deployments, customer-reported issues, or anything high-stakes. You have a human eyeball the actual responses on a weekly or per-release cadence.

The point of the picture is that you don't pick just one of these layers. You combine them at the right cadences so they reinforce each other.

---

## Slide 12 — Production gotcha: read-only filesystems

Before we wrap up, there's one more gotcha worth naming. `adk eval` writes files back to the agents directory, because it persists updated session histories for the eval runs. So if your deployment image is read-only, which is common in Kubernetes with read-only root filesystems, eval hits a PermissionError.

The upstream issue is adk-python number 3887.

The workaround is straightforward. You either mount the agents directory as writable during eval runs, or you run eval outside the deployed image entirely, whether that's in CI, on a developer machine, or in a separate eval pipeline. The agent code is exactly the same; only the runtime environment is different. It doesn't block classroom use, but it becomes a real concern when you wire eval into CI/CD against a production-shaped container.

---

## Slide 13 — What to carry forward

So what should you carry forward from this module? Three things really matter.

The first is to test trajectory strictly. That's the high-value metric ADK gives you that nobody else does as cleanly, so use it.

The second is to test response quality with LLM-as-judge, not ROUGE-1, for any real work. The pseudocode pattern from a few slides ago is the foundation, and ADK's Vertex integration packages it for you if you're on that path.

And the third is to not trust ROUGE-1 past the sanity-check tier. It's useful as a low-effort regression signal. It is not a measure of correctness, and acting on its number as if it were one will mislead you.

---

## Slide 14 — Up next

Up next, deployment. We'll cover `adk deploy cloud_run` as the one-command story, a vanilla Dockerfile that runs the same agent on any cloud, and a brief look at Vertex AI Agent Engine as the opinionated managed path. After that, Part 2 of the course begins, where we get into the Gemini-specific features you lose by going fully vendor-neutral. See you there.
