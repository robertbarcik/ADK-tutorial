# Deployment

The last chapter of Part 1.

Nine chapters of building agents that run in notebooks, in `adk web`, in test scripts. This chapter is about turning them into **products** — HTTP services running in production.

ADK gives you three deployment paths, which differ only in who runs the container and what batteries come with it. Everything at the agent layer is identical — the same `LlmAgent`, the same tools, the same sessions.

- **`adk deploy cloud_run`** — one command; deploys to Google Cloud Run. Fast path if you're fine with GCP.
- **Vanilla Docker** — write a Dockerfile, `docker build`, deploy anywhere containers run. Vendor-neutral.
- **Vertex AI Agent Engine** — the managed, opinionated path. Most batteries included (Memory Bank, Agent Identity, built-in eval). Deepest Google lock-in.

We'll walk the first two hands-on, and sketch Agent Engine in theory.

## The deployable repo layout

Every ADK platform tool — `adk api_server`, `adk web`, `adk deploy cloud_run`, `AgentEvaluator.evaluate` — looks for the same shape:

```
my_agent/
├── __init__.py          # empty; makes it a package
├── agent.py             # exports `root_agent`
├── requirements.txt     # pinned Python deps
└── .env                 # optional; OPENROUTER_API_KEY, etc.
```

The `__init__.py` marks the directory as a Python package. `agent.py` is the file everyone looks at; it must export `root_agent = LlmAgent(...)`. `requirements.txt` pins your dependencies so production installs reproducibly. `.env` is optional — if present, `python-dotenv` loads it before the agent starts.

This is convention, not hard requirement. You can deviate if you have a specific reason. `adk create my_agent` scaffolds exactly this layout — one command, done.

## Path 1 — `adk api_server`: see your agent as an HTTP service

Before any cloud deployment, see the agent running as an HTTP service locally. That's what `adk api_server` does.

```bash
# From the parent of the agent folder
adk api_server .
```

This starts a FastAPI server at `http://localhost:8000`. It hosts every agent folder it finds in the directory you gave it. The API is documented via Swagger at `http://localhost:8000/docs`.

Key endpoints:

- `GET /list-apps` — returns the list of agents hosted.
- `POST /apps/<app>/users/<user>/sessions/<session_id>` — create a session.
- `POST /run` — send a message to an agent; returns an array of events.

A minimal client interaction:

```bash
# Discover what's hosted
curl http://localhost:8000/list-apps

# Create a session
curl -X POST http://localhost:8000/apps/my_agent/users/u/sessions/s1 \
  -H "Content-Type: application/json" -d '{}'

# Run a turn
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" -d '{
    "app_name": "my_agent",
    "user_id": "u",
    "session_id": "s1",
    "new_message": {"role": "user", "parts": [{"text": "hello"}]}
  }'
```

The response is a JSON array of events — the same events you'd iterate over in a Python runner. Text responses, tool calls, tool responses, state deltas. Identical structure; different transport.

This is the **production shape**. Cloud Run is the same FastAPI app running somewhere else. Swap `http://localhost:8000` for the Cloud Run URL and the client code doesn't change.

## Path 2 — vanilla Docker: deploy anywhere

Turn the local setup into a container image, and you can deploy it to anything that runs containers. The Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Python deps first (separate layer, better caching)
COPY my_agent/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY my_agent/ ./my_agent/

# Cloud Run and most PaaS platforms set $PORT; default to 8080 otherwise.
ENV PORT=8080

# Start the ADK API server hosting the agent folder.
# --host 0.0.0.0 so the container is reachable from outside.
CMD ["sh", "-c", "adk api_server /app --host 0.0.0.0 --port ${PORT}"]
```

Ten lines. No ADK-specific platform plumbing. This is just a FastAPI app in a container.

Build and run locally:

```bash
docker build -t my-agent .

docker run -p 8080:8080 \
    -e OPENROUTER_API_KEY=sk-or-... \
    my-agent

curl http://localhost:8080/list-apps
```

Deploy elsewhere:

- **AWS Fargate / App Runner**: `aws ecr` push, point a service at the image.
- **Azure Container Apps**: `az acr build`, `az containerapp create`.
- **Fly.io**: `fly launch --dockerfile ./Dockerfile`.
- **Kubernetes**: your usual Helm chart or Kustomize manifest.
- **Your own server**: `docker run`.

**The important property, worth stating explicitly: there is no ADK-specific deployment story for non-Google clouds.** It's regular container deployment. You write the same Dockerfile you'd write for any Python web app. ADK's FastAPI output runs everywhere FastAPI runs.

## Path 3 — `adk deploy cloud_run`: the one-liner

For Google Cloud, one command does the whole thing:

```bash
adk deploy cloud_run \
    --project YOUR_GCP_PROJECT \
    --region europe-west1 \
    --service_name my-weather-agent \
    my_weather_agent
```

Under the hood: ADK generates a Dockerfile, builds the image via Cloud Build, pushes to Artifact Registry, deploys a Cloud Run service. The output is a URL — your deployed agent's endpoint. Five minutes, end to end, for a fresh project.

**Trade-offs:**

| Pro | Con |
|---|---|
| Minutes to production; one command | Google Cloud only |
| Sensible defaults tuned for agent workloads | Less control than hand-rolling a Dockerfile |
| Integrates with Cloud Trace + Cloud Logging naturally | You pay the Cloud Run runtime margin |

Good default for "I'm on GCP and I want to ship." Bad default for "I care about the details of my deployment" — use the vanilla Docker path for that.

## Path 4 — Vertex AI Agent Engine: the managed path

The most opinionated option. Vertex AI Agent Engine is Google's à la carte managed runtime for agents. You deploy; Google runs.

### What Agent Engine adds over Cloud Run

- **Managed sessions** — no separate database to run. Billed per event.
- **Memory Bank** — LLM-distilled long-term memory with automatic consolidation and decay. A real upgrade over the hand-rolled `InMemoryMemoryService` we used in Module 08.
- **Agent Identity** — per-agent IAM principals with certificate-bound credentials. Your agent has its own identity, separate from any service account; stolen credentials are un-replayable outside the trusted runtime. The strongest enterprise-governance primitive Google ships in the agent stack.
- **Built-in evaluation and observability** — integrates with the Gen AI Evaluation Service mentioned in Module 09.
- **Framework support**: ADK is first-class; LangChain, LangGraph also supported; CrewAI, OpenAI Agents SDK, and FastAPI work via custom templates.

### Pricing (April 2026)

- **Runtime**: $0.0864/vCPU-hour + $0.0090/GiB-hour. Same rate as Cloud Run; no margin on compute.
- **Sessions**: $0.25 per 1,000 events.
- **Memory Bank storage**: $0.25 per 1,000 memories per month.
- **Memory Bank retrieval**: $0.50 per 1,000 retrieved (first 1,000/month free).

### When to pick Agent Engine vs DIY Cloud Run

- **Agent Engine** if you want Memory Bank and Agent Identity without building them yourself. That's the real pitch — the adjacent services, not the runtime.
- **DIY Cloud Run** if you want portability (the same container runs elsewhere tomorrow), or if you're running at a scale where managed-service margins matter.
- **Neither** if you're not on Google Cloud.

Deployment command:

```bash
adk deploy agent_engine \
    --project YOUR_PROJECT \
    --region europe-west1 \
    --staging_bucket gs://your-staging-bucket \
    my_weather_agent
```

## Plugins — the production cross-cutting mechanism

Module 07 covered callbacks — per-agent lifecycle hooks attached to a single `LlmAgent`. Good for agent-specific guards.

Production often needs the same policy applied to **every agent in the app**: audit logging, per-user rate-limits, token-budget enforcement, org-wide PII redaction. That's what **plugins** are for. They attach to the `Runner`, not to individual agents; every agent managed by that Runner goes through the plugin.

Sketch:

```python
from google.adk.plugins import Plugin

class AuditPlugin(Plugin):
    async def before_run(self, context):
        logger.info("agent_invoked",
                    user=context.user_id,
                    agent=context.agent.name)
    async def after_run(self, context):
        logger.info("agent_finished", duration_ms=context.duration_ms)

runner = Runner(
    agent=root_agent,
    app_name="my_app",
    session_service=sessions,
    plugins=[AuditPlugin()],   # ← applies to EVERY agent the runner touches
)
```

**Rule of thumb, carried over from Module 07:**
- Callbacks for agent-specific logic — specific guards on specific specialists.
- Plugins for app-wide policy — audit, rate-limits, cost tracking, compliance.

In production you'll have both. Plugins are the newer mechanism; Google recommends them over app-wide callbacks for new code. If you're refactoring an existing ADK deployment, this is the pattern to migrate toward.

## Production-readiness checklist

Things to have sorted beyond making the agent work. None are ADK-specific — they're what any Python service needs — but they're worth listing because the ADK demos stop at "does the agent work?" and leave the rest to you.

1. **Persistence** — `DatabaseSessionService` pointed at managed Postgres. Not in-memory, not SQLite on ephemeral disk.
2. **Secrets** — out of the container. Cloud Run secrets, AWS Secrets Manager, HashiCorp Vault, whatever your platform provides. Never bake keys into images.
3. **Callbacks for guardrails** — the blocklist, PII redaction, and mocking-in-tests patterns from Module 07.
4. **Plugins for observability** — audit logging, cost tracking, rate-limiting.
5. **Eval in CI** — `adk eval` runs on every PR against your curated evalset. Module 09 wiring.
6. **Trace backend** — Cloud Trace, Langfuse, Arize, or your own OpenTelemetry collector. Every event is already instrumented; you just need to receive them.
7. **Health endpoint** — `adk api_server` exposes `/list-apps`; your load balancer needs to know what counts as healthy.
8. **Auth** — ADK doesn't ship auth. Put an API gateway in front or run it in an authenticated subnet.

## What to carry forward

- **Three deploy paths**: Cloud Run (one command, GCP), Docker (vendor-neutral), Agent Engine (managed, deepest GCP lock-in).
- **The deployable layout** is one folder with `agent.py` exporting `root_agent`, plus `__init__.py` and `requirements.txt`.
- **`adk api_server`** runs the production shape locally; hit it with `curl` to see what your deployed agent will look like.
- **The Dockerfile** is 10 lines; no ADK-specific platform code — just FastAPI in a container.
- **Agent Engine's real pitch is Memory Bank + Agent Identity**, not the runtime (which is Cloud Run priced the same).
- **Plugins** are the production cross-cutting mechanism; callbacks for per-agent, plugins for app-wide.
- **Production readiness** is beyond ADK — persistence, secrets, eval in CI, auth, observability.

## Part 1 wrap

Ten chapters. From "what is an agent" to "how do I ship one."

After these chapters you can build:
- Agents with tools — four flavors (M02)
- Persistent state with scope prefixes (M03, M08)
- Vendor-neutral model swapping (M04)
- Compositions: Sequential, Parallel, Loop, and LLM-driven routing (M05, M06)
- Guardrails, caches, PII redaction via callbacks (M07)
- Long-term memory via `MemoryService` (M08)
- Automated eval with trajectory + LLM-as-judge (M09)
- Deployable as an HTTP service anywhere (this chapter)

All on whichever model you want — Claude, GPT, Gemini, Qwen, Gemma — because the LiteLLM wrapper made the model a configuration, not a dependency.

Module 11 — Part 2 — shifts gears. We switch from LiteLLM-wrapped models to native Gemini and explore the features ADK + Gemini do that nothing else does: Google Search grounding with inline citations, long-context windows with context caching, thinking budgets, and — in Module 13 — the Live API voice agent, the single most differentiated Gemini-only capability in the market.

Switch your `.env` to include `GOOGLE_API_KEY` (free tier at aistudio.google.com is enough for M11–M13). See you in Part 2.
