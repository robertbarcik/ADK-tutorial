# M10 — Speaker notes

---

## Slide 1 — Title

Deployment. That's what this module covers: taking an agent that runs in a notebook and turning it into an HTTP service you can call from anywhere.

Up to now, every agent we built has run inside a notebook, in `adk web`, or in a test script. This module changes that. The agent becomes a FastAPI server, the server runs in a container, and the container goes onto whatever platform you choose.

---

## Slide 2 — Up to now / This module

The framing on this slide puts the whole course in perspective. So far, every agent we built ran locally. This module is where that changes: the agent becomes a product.

The mechanical difference is smaller than it sounds. The agent code stays the same. What changes is how it's invoked: instead of a test script calling it directly, an HTTP client calls it through a FastAPI server that ADK provides.

---

## Slide 3 — Three paths

Three deployment paths, and they differ in how much Google you want in the loop.

The first is `adk deploy cloud_run`, one command to Google Cloud Run. Fastest option if you're already on GCP.

The second is vanilla Docker. Write a Dockerfile, build an image, deploy wherever containers run. No Google required.

The third is Vertex AI Agent Engine, the managed and opinionated path. More batteries included, with Memory Bank and Agent Identity built in. Also the deepest Google lock-in.

All three produce the same thing at the agent layer. They differ only in who runs the container and what comes with it.

---

## Slide 4 — Foundation header

Before we get into each path, there's a common foundation: the folder layout that every ADK tool expects.

---

## Slide 5 — The shape every tool expects

Four files. That's the deployable layout every ADK tool looks for. An `__init__.py` that marks the directory as a Python package. An `agent.py` that exports `root_agent`. A `requirements.txt` with pinned dependencies. And an optional `.env` for secrets.

`adk api_server`, `adk web`, `adk deploy cloud_run`, and `AgentEvaluator.evaluate` all look for this same shape. The convention is not hard-enforced, but straying from it means writing your own plumbing. `adk create` scaffolds it in one command.

---

## Slide 6 — Path 1: adk api_server header

`adk api_server` is the way to see your agent as an HTTP service locally, before committing to any cloud.

---

## Slide 7 — Start it / Hit it

Starting the server takes one command. From the parent directory of your agent folder, run `adk api_server .`. That starts a FastAPI server at localhost:8000 and hosts every agent folder it finds.

Calling it is plain JSON over HTTP. `/list-apps` returns the agents hosted; you create a session by POSTing to the sessions endpoint with a user ID and session ID; and you send a message by POSTing to `/run` with the session triple and the user's content. Zero magic. These are the same endpoints your production client will call.

---

### Notebook break — api_server + real HTTP calls

[Switch the screen to the notebook.]

Run cells 7 and 8. Cell 7 starts `adk api_server` as a background process inside the notebook, then cell 8 sends real HTTP calls against it: list apps, create a session, post a message, collect events. Cell 10 cleans up the process when you're done.

Every call you see is JSON over HTTP to a FastAPI endpoint. This is exactly what a production client would do, just pointing at a different URL.

[Switch back to the slide deck.]

---

## Slide 8 — The production shape

Cloud Run is the same FastAPI app, running on Google's infrastructure instead of your laptop. Swap the URL, and the client code doesn't change.

If you built a frontend that talks to `http://localhost:8000/run`, and tomorrow you deploy to Cloud Run at `https://my-agent-xyz.run.app`, the only change is one URL constant. Session creation, message format, event streaming: all identical.

---

## Slide 9 — Vanilla Docker header

Vanilla Docker is the second path. Deploy to any container platform you like.

---

## Slide 10 — The Dockerfile — 10 lines

The Dockerfile is about ten lines. Take a slim Python base image, copy in the requirements, install them, copy in the agent folder, set a PORT env var, and the CMD runs `adk api_server` listening on all interfaces at whatever port the cloud provides.

No ADK-specific platform code. Just a FastAPI app in a container, which is what lets it deploy anywhere containers run.

---

## Slide 11 — Where you can ship the image

AWS Fargate, Azure Container Apps, fly.io, Kubernetes, your own server with `docker run`: the image runs on all of them. The slide lists the main options with the relevant commands.

The property worth naming explicitly: there's no ADK-specific deployment story for non-Google clouds. It's regular container deployment. ADK's FastAPI output runs anywhere FastAPI runs.

---

## Slide 12 — Path 3: adk deploy cloud_run header

Path 3 gives you a one-command deploy to Cloud Run. If you're already on GCP and want to ship quickly, this is the shortest path.

---

## Slide 13 — The one-liner

The code shows four flags: project, region, service name, and agent folder. Run it. Under the hood, ADK generates a Dockerfile, builds the image with Cloud Build, pushes to Artifact Registry, and deploys a Cloud Run service. The output is a URL.

On the pros side: fast, sensible defaults for agent workloads, integrates naturally with Cloud Trace and Cloud Logging. On the cons side: Google Cloud only, less control than writing your own container, and you pay the Cloud Run runtime margin.

Good default for "I'm on GCP and I want to ship." Bad default for "I care about the details."

---

## Slide 14 — Vertex AI Agent Engine header

The fourth and final path is mention-only: Vertex AI Agent Engine. You deploy; Google runs.

---

## Slide 15 — What Agent Engine adds

Agent Engine adds four things over Cloud Run that actually matter.

First, managed sessions. There's no separate database to run; Google handles session state.

Second, Memory Bank. LLM-distilled long-term memory with auto-consolidation and auto-decay, a real upgrade over a hand-rolled `InMemoryMemoryService`.

Third, Agent Identity. Per-agent IAM principals with certificate-bound credentials. Stolen credentials are un-replayable outside the trusted runtime. This is the strongest enterprise-governance primitive Google ships in the agent stack.

Fourth, built-in evaluation and observability that integrates with Google's Gen AI Evaluation Service.

---

## Slide 16 — Pricing picture

Pricing breaks into four line items, and the most important one is the first: runtime costs the same as Cloud Run. There's no margin at the compute layer.

The usage-based costs are sessions at $0.25 per thousand events, and Memory Bank at $0.25 per thousand memories stored per month, with retrieval at $0.50 per thousand and the first thousand free.

Pick Agent Engine when you want Memory Bank and Agent Identity without building them. Pick Cloud Run when you want portability. Pick neither if you're not on Google Cloud.

---

## Slide 17 — Plugins header

One more concept before we wrap: plugins. They round out the callbacks pattern from earlier in the course and are the right tool for production cross-cutting concerns.

---

## Slide 18 — Callbacks vs Plugins

The slide puts the two mechanisms side by side. Callbacks are per-agent: attached to an `LlmAgent` and good for agent-specific guards like a blocklist or PII redaction on one particular specialist. Plugins are whole-runner: attached to the `Runner` and applied to every agent it manages.

That scope difference is what makes plugins the right tool for organizational concerns. Audit logging, per-user rate limits, token-budget enforcement, org-wide PII redaction: these need to apply consistently across the whole app, not just one agent.

The rule of thumb is the same as with callbacks: per-agent logic stays in callbacks, app-wide policy goes in plugins. In production you'll usually have both. Plugins are newer in the ADK, and Google recommends them over app-wide callbacks for new code.

---

## Slide 19 — Production readiness checklist

Seven concerns worth naming explicitly, beyond "does the agent work."

Persistence and secrets are table stakes: `DatabaseSessionService` against managed Postgres, keys out of the container. Then the ADK-specific layer: callbacks for guardrails, plugins for observability, eval in CI on every pull request. On top of that, a trace backend so you can see what the agent is doing in production. And auth, because ADK doesn't ship auth: that's an API gateway or an authenticated subnet.

None of these are ADK-specific. They're what any Python service needs. Worth naming them here because the demos don't include them.

---

## Slide 20 — Part 1 wrap

That wraps Part 1. From "what is an agent" to "how do I ship one."

---

## Slide 21 — What you can build now

Part 1 covered a lot of ground. Agents with tools in four flavors. Persistent state with scope prefixes. Vendor-neutral model swapping: the same agent on Claude, GPT, Qwen, or Gemini. Workflow compositions and LLM-driven routing. Guardrails, caches, and PII redaction via callbacks. Long-term memory via MemoryService. Automated evaluation with trajectory testing and LLM-as-judge. And deployment as an HTTP service, anywhere containers run.

All of it against whichever model you want, because LiteLLM made the model a configuration, not a dependency.

---

## Slide 22 — Up next / Part 2

Part 2 starts in the next module. The shift is from vendor-neutral to Gemini-specific: Google Search grounding with inline citations, context caching that cuts token costs on repeated prompts, and later in Part 2, thinking budgets and the Live API voice agent.

Switch your `.env` to include `GOOGLE_API_KEY`. The free tier at aistudio.google.com is enough for the Gemini modules. See you in Part 2.
