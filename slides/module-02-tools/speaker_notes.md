# M02 — Speaker notes

Written as spoken delivery. Read one section per slide.

---

## Slide 1 — Title

Module two. Tools as verbs. If module one gave you the mental model of an agent, this module is where the agent starts doing things. Tools are the verbs. An agent without tools can only produce text — that's a chatbot. An agent with tools can look up data, call APIs, run code, talk to other agents. That's software. Four flavors of tools, one mental model, one design rule, one interlude on risk. Let's go.

---

## Slide 2 — Without / with tools

Here's the framing. Without tools, an agent is a chatbot. It produces text. That's the entire scope. With tools, an agent is software — it can reach out to the world, change state, make decisions that stick. Everything interesting about agent development happens at the tool boundary. So we spend a full module here.

---

## Slide 3 — The tool mental model

The picture. When the model decides a tool is needed, it emits a structured call — tool name, arguments. ADK catches the call, finds the code behind it, runs the code, wraps the return value, and feeds it back to the model as a tool-response event. Then the model produces a final answer based on what the tool returned.

This is the same shape regardless of what kind of tool you're wiring up. What changes between the four flavors is only where the schema comes from and where the code runs. That's it.

---

## Slide 4 — Four flavors differ only in two things

Here's the table you should carry in your head. Four flavors.

FunctionTool — the schema comes from your Python function's docstring and type hints. The code lives in your file. We used one in module one.

OpenAPIToolset — the schema comes from an OpenAPI specification. The code lives in a remote HTTP API.

MCPToolset — the schema comes from an MCP server's list-tools response. The code lives in a separate process.

AgentTool — the schema comes from another agent's name and description. The code is that other agent.

Same abstraction to the model. The model cannot tell the difference between these four at the schema level. We'll build one of each today.

---

## Slide 5 — Flavor 1 header

Flavor one. FunctionTool. Plain Python functions.

---

## Slide 6 — The docstring is the schema

The thing to internalize about FunctionTool: **the docstring is the schema.** ADK reads your function's docstring and type hints and generates the JSON schema the LLM provider expects — OpenAI-style, Gemini-style, whichever.

Three practical consequences. First, write the docstring for the model to read, not for a human code reviewer. The model has no channel to ask you what a parameter means. Every argument needs an unambiguous description.

Second, type hints are load-bearing. A missing type hint degrades to string, often silently. Always type your tool functions.

Third, return a JSON-serializable dict or string. Not a custom class, not a NumPy array. The return value is sent verbatim to the model as a tool-response event — it has to be serializable.

---

## Slide 7 — Code example

Here's what a richer FunctionTool looks like. Two parameters, one optional with a default. The Args block in the docstring becomes the parameter descriptions the model sees. The Python default becomes an optional argument in the schema. The typing `city: str` becomes `"type": "string"` in the emitted schema.

One small design note: I tell the model explicitly when to use fahrenheit. Without that sentence, the model guesses.

---

## Slide 8 — Live: FunctionTool

Switch to the notebook. Cell thirteen. The weather agent gets a Munich question with a Fahrenheit qualifier. Watch the tool call arguments: the model picks `units='fahrenheit'` because the instruction told it to, and the tool returns a number the model then formats as English.

---

## Slide 9 — Flavor 2 header

Flavor two. OpenAPIToolset. Consume an entire REST API.

---

## Slide 10 — When to use OpenAPI

When the thing you want to call is a REST API that already has an OpenAPI spec, you don't want to hand-write a FunctionTool per endpoint. Hand ADK the spec; get N tools automatically.

The use case in production: your company already has an API with a spec — that same spec your web frontend is using. Point the agent at it. The agent gets to call every endpoint. No glue code per endpoint.

One quirk to know: ADK snake-cases operation IDs. If your spec says `operationId: getLatestRate`, the tool the model sees is named `get_latest_rate`. If a call isn't happening and you're sure the instruction is right, check whether ADK renamed the tool.

---

## Slide 11 — OpenAPI code

Three lines to integrate. A spec dict (or JSON string, or YAML string) goes into OpenAPIToolset. The toolset goes into the agent's tools list. Done.

I'm using the Frankfurter currency API for the demo — it's free, no auth, public. The spec I'm passing is minimal, just one endpoint. In production your spec would be larger and every path would become a tool.

---

## Slide 12 — Live: OpenAPI

Switch to the notebook. Cell sixteen. I ask the fx agent for the CHF to JPY rate. Watch the tool call arguments: `base='CHF'`, `symbols='JPY'`. The tool response is the raw JSON body from the Frankfurter API, unmodified. The model reads the rate field and produces the final answer.

ADK doesn't transform the API's output — it passes it through as-is. That's useful for debugging; you can see the API's actual contract in the event stream.

---

## Slide 13 — Flavor 3 header

Flavor three. MCPToolset. Talk to a separate tool server.

---

## Slide 14 — What MCP is

Model Context Protocol. Anthropic's standard for exposing tools to agents. It was donated to the Linux Foundation in December 2025, and it is now the de facto standard for agent-to-tool communication across the industry — Anthropic, Google, OpenAI, Microsoft, the open-source stack, all of them support it.

An MCP server is a separate process. Your agent connects over stdin/stdout (or HTTP, or Server-Sent Events) and uses the server's tools as if they were local.

The reason MCP matters: the server can be written in any language. TypeScript, Go, Rust, whatever. It can run on any machine. It can own any state — database connections, API credentials, caches. The agent doesn't know. It speaks MCP; the tools show up.

---

## Slide 15 — MCP code

Connect to an MCP server — two concepts. The connection parameters say how to reach it: stdio, which language to run the server in, what script file. Then MCPToolset spawns the server, speaks the handshake, and lists its tools.

This repo ships three ready-made MCP servers in the `mcp_servers/` folder — one for tickets, one for a knowledge base, one for system monitoring. We're using the ticket server here. It exposes five tools; five tools appear in the agent with no extra code.

---

## Slide 16 — Live: MCP

Switch to the notebook. Cell nineteen. The ticket agent gets a WiFi question. Watch the event stream — the tool called is `search_tickets`, which came from the MCP server. The response is the server's payload, wrapped in an MCP content envelope. The model extracts the ticket and produces the final answer.

The MCP subprocess is running on your laptop right now, in the background, holding the ticket database. When we end the notebook we'll close it; otherwise it leaks.

---

## Slide 17 — Flavor 4 header

Flavor four. AgentTool. Wrap an agent as a tool.

---

## Slide 18 — AgentTool vs sub_agents

This one has a conceptual subtlety worth getting right. ADK has two ways to put one agent inside another.

AgentTool is the consultant pattern. The parent calls the specialist like a function. The parent stays in charge. The child answers, and control goes back to the parent automatically.

sub_agents is the transfer pattern. The parent hands the conversation over. The child owns the conversation — for one turn or twenty turns — until the child itself decides to transfer back.

AgentTool when the child has a clean I/O contract. sub_agents when the child should drive the dialog. M06 does this comparison in detail. For today — focus on the consultant pattern.

---

## Slide 19 — AgentTool code

A translator wrapped as a tool. The translator is itself an agent — it has a model, an instruction, a purpose. But instead of giving it to `sub_agents`, we wrap it in `AgentTool` and hand that to the parent.

Now the parent's model sees `translator` in its tools list, with the translator's description as the tool description. When a user asks for a translation, the parent calls the translator, gets its response, and incorporates it.

---

## Slide 20 — Live: AgentTool

Cell twenty-two of the notebook. The orchestrator gets asked for a Slovak translation of a phrase. Watch the event stream. The orchestrator calls the `translator` tool. The translator runs as its own LLM call, produces a translation, and the response comes back. The orchestrator then produces the final user-facing reply. Two model calls, one observable event trace.

---

## Slide 21 — Interlude header

Quick interlude. Two minutes. Theory. Risk-based tool design — one of the ten patterns from the Agentic Design Patterns publication. The idea matters enough to pause the flavor tour and make you think about it.

---

## Slide 22 — Risk tiers

Not all tools are equal. A tool that reads a ticket is not in the same category as a tool that deletes the database. The difference is blast radius — the scope of damage a misfiring tool call can do before anyone notices.

A practical taxonomy. Four tiers.

Read-only: no external change. `get_weather`, `search_tickets`. No guard needed.

Mutating, reversible: writes, but undoing the write is cheap. `create_ticket`, `send_draft_email`. Log every call; that's the audit trail.

Mutating, irreversible: writes that are hard to roll back. `charge_card`, `post_to_slack`. These need explicit confirmation — not just an instruction to the model, but a code-level gate.

Catastrophic: destructive, multi-user, loud. `drop_database`, `delete_user`, `publish_press_release`. Humans in the loop. Do not let the agent call these directly.

The temptation is to treat every tool the same because the framework treats them the same. Don't.

---

## Slide 23 — Where to put the guard

The rule, on one slide. **Put the guard in the tool code.** Not in the instruction.

An instruction is a polite request the model can ignore or misread. Code is a wall. If your delete-ticket tool checks for a confirmation token in Python, no instruction in the world can bypass it. If your check is only "please ask the user first" in the system prompt, the model will skip it sometimes, and the first time that costs you data, you'll wish you'd enforced it in code.

---

## Slide 24 — Confirmation gate code

Here's the pattern. The tool takes an extra argument — `confirmation_token`, defaulted to empty. If the token matches the expected string for this specific ticket, the delete proceeds. If the token is empty or wrong, the function returns a preview and does nothing.

Now the instruction to the model can say "call with empty token first, show the preview, confirm with the user, and only retry with the real token if they explicitly confirm." But if the model skips any of that — if it tries to short-cut — the tool returns a preview anyway, and the delete does not happen.

Notice the subtle detail: the expected token is computed from the ticket ID. That way a model that somehow learned a fixed token string from training data can't just hardcode it.

---

## Slide 25 — Live: guarded delete

Cell twenty-five. The user says "delete ticket T-1001." Watch the event stream.

The agent calls `delete_ticket` without a confirmation token. The tool returns a preview, not a delete. The agent surfaces the preview to the user and asks for confirmation. Only on a second turn, with the right token, would the delete actually happen. The data is safe.

---

## Slide 26 — Choosing a flavor

A quick reference before we wrap. If the thing you want is a Python function running in-process — FunctionTool. If it's an existing REST API with a spec — OpenAPIToolset. If it's a tool server written in any language with its own state — MCPToolset. If it's a specialist sub-agent the parent should call like a function — AgentTool.

The FunctionTool is the default. Reach for the others when you have a specific reason — a language mismatch, an existing spec, a shared tool catalog.

---

## Slide 27 — Gotchas

Three real gotchas to pre-empt.

One: built-in Google tools — Search, code execution, Vertex Search — cannot coexist with other tools in the same agent. There's an exception for Search on ADK 1.16 or later via `bypass_multi_tools_limit=True`. Otherwise, wrap each built-in tool in its own sub-agent. We'll do this in module eleven.

Two: MCP stdio in Jupyter or Colab. Jupyter replaces `sys.stderr` with an object without a `.fileno()`, which breaks subprocess spawn. The notebook patches this in the setup cell automatically. If you ever write your own MCP integration in a notebook, patch `sys.stderr` first.

Three: LiteLLM plus tool calls plus streaming is known-flaky on non-Gemini models. ADK defaults tool-calling demos to non-streaming, which is the right choice for our purposes. If you turn streaming back on for production, test the tool paths hard.

---

## Slide 28 — Takeaway

What to carry forward. Tools come in four flavors. Same abstraction to the model; different integration targets. FunctionTool, OpenAPIToolset, MCPToolset, AgentTool.

And the design rule. Blast radius matters. Put the guard in the tool code, not in the instruction.

---

## Slide 29 — Next

Module three. Sessions, State, Events, Artifacts. Where the conversation's memory actually lives. See you there.
