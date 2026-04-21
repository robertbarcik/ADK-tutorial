# M10 — Speaker notes

---

## Slide 1 — Title

Module ten. The last module of Part 1. Deployment. Nine modules of building agents that run in notebooks, in `adk web`, in test scripts. This module is about turning them into products — HTTP services running in production.

---

## Slide 2 — From notebooks to products

The frame. Nine modules of agents in notebooks. Module ten turns them into products. The difference is mechanical: the agent becomes an HTTP service, runs in a container, lives on a platform that bills you by the hour. The interesting work happened in the previous nine modules; this module is about the deploy mechanics.

---

## Slide 3 — Three paths

ADK offers three deployment paths.

`adk deploy cloud_run` — one command, deploys to Google Cloud Run. Fast path if you're fine with GCP.

Vanilla Docker — you write a Dockerfile, docker build, deploy wherever containers run. AWS, Azure, fly.io, a Raspberry Pi on your desk. Vendor-neutral.

Vertex AI Agent Engine — the managed, opinionated path. More batteries included — Memory Bank, Agent Identity, built-in eval. Deepest Google lock-in.

All three produce the same thing at the agent layer. They differ only in who runs the container and what comes with it.

---

## Slide 4 — Foundation header

The foundation. The deployable repo layout. What every ADK deployment mechanism expects to see.

---

## Slide 5 — The shape

Four files. An `__init__.py` — empty, marks the directory as a Python package. An `agent.py` — the thing everyone looks at; it must export `root_agent`. A `requirements.txt` with your pinned Python deps. An optional `.env` for secrets.

`adk api_server`, `adk web`, `adk deploy cloud_run`, `AgentEvaluator.evaluate` — all of them look for this shape. The convention isn't hard-enforced, but if you stray from it you're writing custom plumbing.

`adk create` scaffolds exactly this layout for you — one command, done.

---

## Slide 6 — api_server header

Path one. `adk api_server`. The way to see your agent as an HTTP service locally, before you commit to any cloud.

---

## Slide 7 — Start it, hit it

Two commands. First — start it. From the parent directory of your agent folder, run `adk api_server .`. That starts a FastAPI server at localhost:8000. It hosts every agent folder it finds in the directory you gave it.

Second — hit it. The API is documented at `/docs` if you want the Swagger UI. The key endpoints: `/list-apps` returns the agents hosted; create a session by POSTing to `/apps/<app>/users/<user>/sessions/<session_id>`; send a message by POSTing to `/run` with the session triple and the user's content.

---

## Slide 8 — Live: api_server + curl

Switch to the notebook. Cells seven through nine. We start `adk api_server` as a background process inside the notebook. Then we use Python's `urllib` to make real HTTP calls against it — list apps, create a session, send a message, collect events.

Every call in that cell is JSON over HTTP to a FastAPI endpoint. Zero magic. Your production agent will be exactly this same thing, running somewhere else.

---

## Slide 9 — The production shape

What you saw, on one slide. This is the production shape. Cloud Run is the same FastAPI app, running on Google's infrastructure instead of your laptop. Swap the URL, the client code doesn't change.

If you built a web frontend that talks to `http://localhost:8000/run`, and tomorrow you deploy to Cloud Run at `https://my-agent-xyz.run.app`, the only change is one URL constant. Everything else — session creation, message format, event streaming — is identical.

---

## Slide 10 — Docker header

Path two. Vanilla Docker. Deploy to any container platform.

---

## Slide 11 — The Dockerfile

Ten lines. Slim Python base image, copy in the requirements, install them, copy in the agent folder, set a PORT env var, and the CMD runs `adk api_server` listening on all interfaces at the cloud-provided port.

No ADK-specific platform code. Just a FastAPI app in a container. That's what lets it deploy anywhere containers run.

---

## Slide 12 — Where the image runs

And the list. AWS Fargate or App Runner. Azure Container Apps. fly.io. Kubernetes with your usual Helm chart. Your own server with `docker run`.

The important property worth stating explicitly: **there's no ADK-specific deployment story for non-Google clouds.** It's regular container deployment. You write the same Dockerfile you'd write for any Python web app. ADK's FastAPI output runs everywhere FastAPI runs.

---

## Slide 13 — Cloud Run header

Path three. `adk deploy cloud_run`. One command, minutes to production. If you're already on GCP and in a hurry, this is the shortest path.

---

## Slide 14 — The one-liner

Here it is. Four flags: project, region, service name, agent folder. Run it. Under the hood: ADK generates a Dockerfile, builds the image with Cloud Build, pushes to Artifact Registry, deploys a Cloud Run service. The output is a URL.

Pros — fast, sensible defaults for agent workloads, integrates with Cloud Trace and Cloud Logging naturally. Cons — Google Cloud only, less control than writing your own container, you pay the Cloud Run runtime margin.

Good default for "I'm on GCP and I want to ship." Bad default for "I care about the details."

---

## Slide 15 — Agent Engine header

Path four — mention only, not hands-on. Vertex AI Agent Engine. The most opinionated option. You deploy; Google runs.

---

## Slide 16 — What Agent Engine adds

Four things Agent Engine adds over Cloud Run that matter.

Managed sessions. You don't run your own Postgres for session state; Google does.

Memory Bank. The managed long-term memory service we mentioned in module eight — LLM-distilled facts, auto-consolidation, auto-decay. A real upgrade over hand-rolled InMemoryMemoryService.

Agent Identity. Per-agent IAM principals with certificate-bound credentials. Your agent has its own identity, separate from any service account. Stolen credentials are un-replayable outside the trusted runtime. This is the strongest enterprise-governance primitive Google ships in the agent stack.

Built-in evaluation and observability that integrate with the Gen AI Evaluation Service we mentioned in module nine.

---

## Slide 17 — Agent Engine pricing

The pricing picture as of April 2026.

Runtime is the same rate as Cloud Run — $0.0864 per vCPU-hour, $0.0090 per GiB-hour. No margin at the compute layer; they're not soaking you on CPU time.

Sessions are $0.25 per thousand events. If your agent averages ten events per conversation and you have a thousand conversations a day, that's $2.50 a day in session costs.

Memory Bank storage: $0.25 per thousand memories per month. Retrieval: $0.50 per thousand, first thousand retrieved per month free.

Trade-off framing. Pick Agent Engine if you want Memory Bank and Agent Identity without building them. That's the real pitch. Pick Cloud Run if you want portability — the same container runs elsewhere tomorrow — or if you're running at a scale where managed-service margins matter. Pick neither if you're not on Google Cloud.

---

## Slide 18 — Plugins header

One more thing. Plugins. The production-grade cross-cutting mechanism that rounds out module seven's callbacks.

---

## Slide 19 — Callbacks vs Plugins

Module seven covered callbacks — per-agent lifecycle hooks. Six of them — before and after agent, model, and tool. Good for agent-specific guards.

Plugins are the same idea at a different scope. Attached to the Runner, not to individual agents. Every agent managed by that Runner goes through the plugin. Good for org-wide policy — audit logging, per-user rate-limits, token-budget enforcement, PII redaction that applies to the whole app, not one specialist.

Rule of thumb, same as module seven: callbacks for agent-specific logic; plugins for app-wide policy. In production, you'll usually have both. Callbacks on specialists for their specific guards. Plugins on the runner for organizational concerns.

Plugins are newer in the ADK — Google recommends them over app-wide callbacks for new code. If you're refactoring an existing deployment, migrate toward them.

---

## Slide 20 — Production readiness

Production readiness checklist. Things to sort out beyond "does the agent work."

Persistence — DatabaseSessionService against managed Postgres. Not in-memory, not SQLite on ephemeral disk.

Secrets — out of the container. Cloud Run secrets, AWS Secrets Manager, whatever your platform provides. Never bake keys into images.

Callbacks for guardrails — the blocklist, PII, mocking patterns from module seven.

Plugins for observability — audit, cost tracking, rate-limiting.

Eval in CI — `adk eval` runs on every PR against your curated evalset. Module nine wiring.

Trace backend — Cloud Trace, Langfuse, Arize, your own OpenTelemetry collector. Every event is already instrumented; you just need to receive them.

Auth — ADK doesn't ship auth. Put an API gateway in front or run in an authenticated subnet.

None of these are ADK-specific. They're what any Python service needs. Worth stating explicitly, though — the ADK demos give you the agent. Everything else is yours to build.

---

## Slide 21 — Part 1 wrap

Ten modules. From "what is an agent" to "how do I ship one."

---

## Slide 22 — What you can build

The summary. After ten modules, here's what you can build.

Agents with tools — four flavors. Persistent state with scope prefixes. Vendor-neutral model swapping — the same agent on Claude, GPT, Qwen, Gemini. Compositions — Sequential, Parallel, Loop workflow agents, plus LLM-driven routing with sub_agents and AgentTool. Guardrails, caches, PII redaction via callbacks. Long-term memory via MemoryService. Automated eval with trajectory testing and LLM-as-judge. Deployable as an HTTP service anywhere.

All on whichever model you want. Claude, GPT, Gemini, Qwen, Gemma. Because the LiteLLM wrapper made the model a configuration, not a dependency.

---

## Slide 23 — Next / Part 2

Module eleven. Part 2 begins. We switch gears. From vendor-neutral to Gemini-specific. Google Search grounding with inline citations. Long-context windows with context caching — 90% discount on cached tokens. Thinking budgets that let you trade latency for reasoning quality. And in module thirteen, the Live API voice agent — the single most differentiated Gemini-only capability in the market.

Switch your `.env` to include `GOOGLE_API_KEY`. The free tier at aistudio.google.com is enough for modules 11 through 13. See you in Part 2.
