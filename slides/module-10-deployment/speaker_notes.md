# M10 — Speaker notes

---

## Slide 1 — Title

Welcome to module ten — the last module of Part 1, and it's about deployment. So far we've had nine modules of building agents that run in notebooks, in `adk web`, or in test scripts. This module is about turning them into products — so HTTP services running in production.

---

## Slide 2 — From notebooks to products

Here's the framing for this module. We've had nine modules of agents living in notebooks, and module ten turns them into products. The difference is really mechanical — the agent becomes an HTTP service, runs in a container, and lives on a platform that bills you by the hour. The interesting work happened in the previous nine modules, which means this module is just about the deploy mechanics.

---

## Slide 3 — Three paths

ADK offers three deployment paths, and they differ in how much Google you want in the loop.

First, `adk deploy cloud_run` — one command, and it deploys to Google Cloud Run. This is the fast path if you're fine with GCP.

Second, vanilla Docker — you write a Dockerfile, run `docker build`, and deploy wherever containers run. So AWS, Azure, fly.io, or even a Raspberry Pi on your desk. Fully vendor-neutral.

And third, Vertex AI Agent Engine — the managed, opinionated path. More batteries included, with things like Memory Bank, Agent Identity, and built-in eval. It's also the deepest Google lock-in.

All three produce the same thing at the agent layer. They differ only in who runs the container and what comes with it.

---

## Slide 4 — Foundation header

Let's start with the foundation — the deployable repo layout, and what every ADK deployment mechanism expects to see.

---

## Slide 5 — The shape

Every deployable ADK agent has the same four-file shape. First, an `__init__.py` — empty, and it just marks the directory as a Python package. Second, an `agent.py` — this is the thing everyone looks at, and it must export `root_agent`. Third, a `requirements.txt` with your pinned Python deps. And finally, an optional `.env` for secrets.

`adk api_server`, `adk web`, `adk deploy cloud_run`, and `AgentEvaluator.evaluate` — all of them look for this shape. The convention isn't hard-enforced, but if you stray from it, you're writing custom plumbing.

And `adk create` scaffolds exactly this layout for you — one command, done.

---

## Slide 6 — api_server header

Path one is `adk api_server`. It's the way to see your agent as an HTTP service locally, before you commit to any cloud.

---

## Slide 7 — Start it, hit it

Running it is really just two commands. First — start it. From the parent directory of your agent folder, run `adk api_server .`. That starts a FastAPI server at localhost:8000, and it hosts every agent folder it finds in the directory you gave it.

Second — hit it. The API is documented at `/docs` if you want the Swagger UI. The key endpoints are these: `/list-apps` returns the agents hosted; you create a session by POSTing to `/apps/<app>/users/<user>/sessions/<session_id>`; and you send a message by POSTing to `/run` with the session triple and the user's content.

---

## Slide 8 — Live: api_server + curl

Switch to the notebook — cells seven through nine. We start `adk api_server` as a background process inside the notebook. Then we use Python's `urllib` to make real HTTP calls against it — so list apps, create a session, send a message, and collect events.

Every call in that cell is just JSON over HTTP to a FastAPI endpoint. Zero magic. Your production agent will be exactly this same thing, running somewhere else.

---

## Slide 9 — The production shape

What you see on this slide is the production shape, captured in one picture. Cloud Run is really the same FastAPI app, just running on Google's infrastructure instead of your laptop. Swap the URL, and the client code doesn't change.

So if you built a web frontend that talks to `http://localhost:8000/run`, and tomorrow you deploy to Cloud Run at `https://my-agent-xyz.run.app`, the only change is one URL constant. Everything else — session creation, message format, event streaming — is identical.

---

## Slide 10 — Docker header

Path two is vanilla Docker. Deploy to any container platform you like.

---

## Slide 11 — The Dockerfile

The Dockerfile itself is about ten lines. You take a slim Python base image, copy in the requirements, install them, copy in the agent folder, set a PORT env var, and the CMD runs `adk api_server` listening on all interfaces at the cloud-provided port.

No ADK-specific platform code. Just a FastAPI app in a container. That's really what lets it deploy anywhere containers run.

---

## Slide 12 — Where the image runs

And here's the list of places that image can run. AWS Fargate or App Runner. Azure Container Apps. fly.io. Kubernetes with your usual Helm chart. Or your own server with `docker run`.

The important property worth stating explicitly is this: **there's no ADK-specific deployment story for non-Google clouds.** It's just regular container deployment, which means you write the same Dockerfile you'd write for any Python web app. ADK's FastAPI output runs everywhere FastAPI runs.

---

## Slide 13 — Cloud Run header

Path three is `adk deploy cloud_run`. One command, and minutes to production. If you're already on GCP and in a hurry, this is the shortest path.

---

## Slide 14 — The one-liner

In code, the one-liner takes four flags — project, region, service name, and agent folder. Run it. Under the hood, ADK generates a Dockerfile, builds the image with Cloud Build, pushes to Artifact Registry, and deploys a Cloud Run service. The output is a URL.

On the pros side — it's fast, it has sensible defaults for agent workloads, and it integrates naturally with Cloud Trace and Cloud Logging. On the cons side — it's Google Cloud only, you get less control than writing your own container, and you pay the Cloud Run runtime margin.

So it's a good default for "I'm on GCP and I want to ship," and a bad default for "I care about the details."

---

## Slide 15 — Agent Engine header

Path four is a mention only, not a hands-on — Vertex AI Agent Engine. It's the most opinionated option. You deploy; Google runs.

---

## Slide 16 — What Agent Engine adds

There are four things Agent Engine adds over Cloud Run that actually matter.

First, managed sessions. You don't run your own Postgres for session state; Google does.

Second, Memory Bank. This is the managed long-term memory service we mentioned in module eight — so LLM-distilled facts, auto-consolidation, and auto-decay. A real upgrade over hand-rolled InMemoryMemoryService.

Third, Agent Identity. Per-agent IAM principals with certificate-bound credentials. Your agent has its own identity, separate from any service account. As a result, stolen credentials are un-replayable outside the trusted runtime. This is really the strongest enterprise-governance primitive Google ships in the agent stack.

And finally, built-in evaluation and observability that integrate with the Gen AI Evaluation Service we mentioned in module nine.

---

## Slide 17 — Agent Engine pricing

Let me walk through the pricing picture as of April 2026.

Runtime is the same rate as Cloud Run — $0.0864 per vCPU-hour, and $0.0090 per GiB-hour. So there's no margin at the compute layer; they're not soaking you on CPU time.

Sessions are $0.25 per thousand events. So if your agent averages ten events per conversation and you have a thousand conversations a day, that's $2.50 a day in session costs.

Memory Bank storage is $0.25 per thousand memories per month. Retrieval is $0.50 per thousand, and the first thousand retrieved per month are free.

And here's the trade-off framing. Pick Agent Engine if you want Memory Bank and Agent Identity without building them — that's really the pitch. Pick Cloud Run if you want portability — so the same container runs elsewhere tomorrow — or if you're running at a scale where managed-service margins matter. And pick neither if you're not on Google Cloud.

---

## Slide 18 — Plugins header

One more thing before we wrap — plugins. The production-grade cross-cutting mechanism that rounds out module seven's callbacks.

---

## Slide 19 — Callbacks vs Plugins

Module seven covered callbacks — so per-agent lifecycle hooks. Six of them in total — before and after agent, model, and tool. Good for agent-specific guards.

Plugins are really the same idea at a different scope. They're attached to the Runner, not to individual agents, which means every agent managed by that Runner goes through the plugin. That's good for org-wide policy — things like audit logging, per-user rate-limits, token-budget enforcement, or PII redaction that applies to the whole app, not just one specialist.

So the rule of thumb is the same as module seven — callbacks for agent-specific logic, plugins for app-wide policy. In production, you'll usually have both. Callbacks on specialists for their specific guards. Plugins on the runner for organizational concerns.

Plugins are newer in the ADK — Google recommends them over app-wide callbacks for new code. So if you're refactoring an existing deployment, migrate toward them.

---

## Slide 20 — Production readiness

Let me walk through a production readiness checklist — things to sort out beyond "does the agent work."

First, persistence — so DatabaseSessionService against managed Postgres. Not in-memory, and not SQLite on ephemeral disk.

Second, secrets — out of the container. Things like Cloud Run secrets, AWS Secrets Manager, or whatever your platform provides. Never bake keys into images.

Third, callbacks for guardrails — so the blocklist, PII, and mocking patterns from module seven.

Fourth, plugins for observability — things like audit, cost tracking, and rate-limiting.

Fifth, eval in CI — `adk eval` runs on every PR against your curated evalset. That's the module nine wiring.

Sixth, a trace backend — Cloud Trace, Langfuse, Arize, or your own OpenTelemetry collector. Every event is already instrumented; you just need to receive them.

And finally, auth — ADK doesn't ship auth, so you put an API gateway in front, or run in an authenticated subnet.

None of these are ADK-specific. They're really what any Python service needs. Worth stating explicitly though — the ADK demos give you the agent. Everything else is yours to build.

---

## Slide 21 — Part 1 wrap

That's ten modules done. From "what is an agent" to "how do I ship one."

---

## Slide 22 — What you can build

Here's the summary of what you can build after ten modules.

Agents with tools — four flavors. Persistent state with scope prefixes. Vendor-neutral model swapping — so the same agent on Claude, GPT, Qwen, or Gemini. Compositions — Sequential, Parallel, and Loop workflow agents, plus LLM-driven routing with sub_agents and AgentTool. Guardrails, caches, and PII redaction via callbacks. Long-term memory via MemoryService. Automated eval with trajectory testing and LLM-as-judge. And deployable as an HTTP service anywhere.

All on whichever model you want — Claude, GPT, Gemini, Qwen, or Gemma. Because the LiteLLM wrapper made the model a configuration, not a dependency.

---

## Slide 23 — Next / Part 2

Up next is module eleven, where Part 2 begins. We switch gears — from vendor-neutral to Gemini-specific. So Google Search grounding with inline citations. Long-context windows with context caching — so a 90% discount on cached tokens. Thinking budgets that let you trade latency for reasoning quality. And in module thirteen, the Live API voice agent — the single most differentiated Gemini-only capability in the market.

Switch your `.env` to include `GOOGLE_API_KEY`. The free tier at aistudio.google.com is enough for modules 11 through 13. See you in Part 2.
