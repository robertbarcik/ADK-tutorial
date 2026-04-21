# M02 — Speaker notes

---

## Slide 1 — Title

Welcome to module two — tools as verbs. If module one gave you the mental model of an agent, this module is where the agent actually starts doing things. Tools are the verbs. An agent without tools can only produce text, which really means it's just a chatbot. An agent with tools, on the other hand, can look up data, call APIs, run code, or even talk to other agents — and that's what we'd call software. In this module, we'll cover four flavors of tools, one mental model, one design rule, and a short interlude on risk. Let's go.

---

## Slide 2 — Without / with tools

The framing is this. Without tools, an agent is essentially a chatbot — it produces text, and that's the entire scope. With tools, on the other hand, the agent becomes software — it can reach out to the world, change state, and make decisions that stick. Everything interesting about agent development really happens at this tool boundary. And that's why we spend a full module here.

---

## Slide 3 — The tool mental model

Let me walk through what actually happens when an agent calls a tool. When the model decides a tool is needed, it emits a structured call — so the tool name, plus the arguments. ADK then catches that call, finds the code behind it, runs the code, wraps the return value, and feeds it back to the model as a tool-response event. From there, the model produces a final answer based on what the tool returned.

This is the same shape, regardless of what kind of tool you're wiring up. The only things that change between the four flavors are where the schema comes from, and where the code runs. That's really it — just those two dimensions vary.

---

## Slide 4 — Four flavors differ only in two things

Here's the table you should carry in your head — four flavors in total.

First, FunctionTool. The schema comes from your Python function's docstring and type hints, and the code lives in your file. We already used one of these in module one.

Second, OpenAPIToolset. The schema comes from an OpenAPI specification, and the code lives in a remote HTTP API.

Third, McpToolset. The schema comes from an MCP server's list-tools response, and the code lives in a separate process.

And finally, AgentTool. The schema comes from another agent's name and description, and the code is that other agent.

The key thing is that it's the same abstraction to the model. The model really cannot tell the difference between these four at the schema level. Today, we'll build one of each.

---

## Slide 5 — Flavor 1 header

Let's start with flavor one — FunctionTool, which is just plain Python functions.

---

## Slide 6 — The docstring is the schema

If you remember one thing about FunctionTool, remember this — **the docstring is the schema.** What I mean is, ADK reads your function's docstring and type hints, and from those, it generates the JSON schema that the LLM provider expects — so whether that's OpenAI-style, Gemini-style, or whichever.

This has three practical consequences. First, you want to write the docstring for the model to read, and not for a human code reviewer. The model has no channel to ask you what a parameter means, so every argument really needs an unambiguous description.

Second, the type hints are load-bearing. A missing type hint degrades to a string, often silently — so always type your tool functions.

And third, you want to return a JSON-serializable dict or string. Not a custom class, and not a NumPy array. The return value is sent verbatim to the model as a tool-response event, which means it has to be serializable.

---

## Slide 7 — Code example

A richer FunctionTool example looks like this. There are two parameters, and one of them is optional with a default. The Args block in the docstring becomes the parameter descriptions the model sees. The Python default becomes an optional argument in the schema. And the typing `city: str` becomes `"type": "string"` in the emitted schema.

One small design note worth calling out: I tell the model explicitly when to use fahrenheit. Because without that specific sentence, the model would just guess.

---

## Slide 8 — Live: FunctionTool

Switch to the notebook, cell thirteen. The weather agent gets a Munich question with a Fahrenheit qualifier. Watch the tool call arguments — the model picks `units='fahrenheit'` because the instruction told it to, and the tool then returns a number, which the model formats into English.

---

## Slide 9 — Flavor 2 header

Now on to flavor two — OpenAPIToolset, which lets you consume an entire REST API.

---

## Slide 10 — When to use OpenAPI

When the thing you want to call is a REST API that already has an OpenAPI spec, you don't want to hand-write a FunctionTool per endpoint. Instead, you just hand ADK the spec, and you get N tools automatically.

The use case in production is this. Your company already has an API with a spec — the same spec your web frontend is using. You point the agent at it, and the agent gets to call every endpoint. No glue code per endpoint.

There's one quirk worth knowing about: ADK snake-cases operation IDs. So if your spec says `operationId: getLatestRate`, the tool the model sees is actually named `get_latest_rate`. If a call isn't happening and you're sure the instruction is right, check whether ADK has renamed the tool.

---

## Slide 11 — OpenAPI code

In code, wiring it up is really just three lines. You have a spec dict — or a JSON string, or a YAML string — and it goes into OpenAPIToolset. The toolset then goes into the agent's tools list. And that's it.

For the demo, I'm using the Frankfurter currency API — it's free, no auth, and public. The spec I'm passing is minimal, just one endpoint. In production, your spec would be larger, and every path would become a tool.

---

## Slide 12 — Live: OpenAPI

Switch to the notebook, cell sixteen. I ask the fx agent for the CHF to JPY rate. Watch the tool call arguments — `base='CHF'`, `symbols='JPY'`. The tool response is the raw JSON body from the Frankfurter API, unmodified. The model then reads the rate field and produces the final answer.

Notice that ADK doesn't transform the API's output at all — it just passes it through as-is. That's actually really useful for debugging, because you can see the API's actual contract right there in the event stream.

---

## Slide 13 — Flavor 3 header

Flavor three is McpToolset — where you talk to a separate tool server.

---

## Slide 14 — What MCP is

MCP stands for Model Context Protocol, and it's Anthropic's standard for exposing tools to agents. It was donated to the Linux Foundation in December 2025, and it's now the de facto standard for agent-to-tool communication across the industry — Anthropic, Google, OpenAI, Microsoft, the open-source stack, all of them support it.

An MCP server is essentially a separate process that your agent connects to — over stdin/stdout, or HTTP, or Server-Sent Events — and then uses the server's tools as if they were local.

Here's why MCP really matters. The server can be written in any language — TypeScript, Go, Rust, whatever you want. It can run on any machine. And it can own any state — things like database connections, API credentials, or caches. The agent doesn't need to know any of that. It just speaks MCP, and the tools show up.

---

## Slide 15 — MCP code

Connecting to an MCP server really comes down to two concepts. First, the connection parameters say how to reach it — so things like stdio, which language to run the server in, what script file. Then McpToolset spawns the server, speaks the handshake, and lists its tools.

This repo ships three ready-made MCP servers in the `mcp_servers/` folder — one for tickets, one for a knowledge base, and one for system monitoring. We're using the ticket server here. It exposes five tools, and as a result, five tools appear in the agent with no extra code.

---

## Slide 16 — Live: MCP

Switch to the notebook, cell nineteen. The ticket agent gets a WiFi question. Watch the event stream — the tool being called is `search_tickets`, which came from the MCP server. The response is the server's payload, wrapped in an MCP content envelope. The model then extracts the ticket and produces the final answer.

Worth noting: the MCP subprocess is running on your laptop right now, in the background, holding the ticket database. When we end the notebook, we'll close it — otherwise it leaks.

---

## Slide 17 — Flavor 4 header

And the final flavor is AgentTool — where you wrap an agent as a tool.

---

## Slide 18 — AgentTool vs sub_agents

This fourth flavor has a conceptual subtlety worth getting right. ADK actually has two ways to put one agent inside another — AgentTool and sub_agents — and they are not interchangeable.

AgentTool is the consultant pattern — the parent calls the specialist like a function. The parent stays in charge, the child answers, and then control goes back to the parent automatically.

sub_agents, on the other hand, is the transfer pattern — where the parent hands the conversation over entirely. The child then owns the conversation, whether that's for one turn or twenty turns, until the child itself decides to transfer back.

So the rule of thumb is this. Use AgentTool when the child has a clean I/O contract, and sub_agents when the child should drive the dialog. M06 will do this comparison in detail. But for today, just focus on the consultant pattern.

---

## Slide 19 — AgentTool code

In this example, we wrap a translator as a tool. The translator is itself an agent — it has a model, an instruction, and a purpose. But instead of giving it to `sub_agents`, we wrap it in `AgentTool` and hand that to the parent.

Now the parent's model sees `translator` in its tools list, with the translator's description as the tool description. So when a user asks for a translation, the parent calls the translator, gets its response back, and incorporates it into the reply.

---

## Slide 20 — Live: AgentTool

Over in cell twenty-two of the notebook, the orchestrator gets asked for a Slovak translation of a phrase. Watch the event stream. The orchestrator calls the `translator` tool. The translator runs as its own LLM call, produces a translation, and the response comes back. The orchestrator then produces the final user-facing reply. So you get two model calls, but all captured in a single observable event trace.

---

## Slide 21 — Interlude header

Time for a quick interlude — about two minutes of theory, on risk-based tool design. This is one of the ten patterns from the Agentic Design Patterns publication, and the idea matters enough that I want to pause the flavor tour and make you think about it.

---

## Slide 22 — Risk tiers

Not all tools are equal. A tool that reads a ticket is just not in the same category as a tool that deletes the database. The difference between them is blast radius — the scope of damage a misfiring tool call can do before anyone notices.

A practical taxonomy looks like this — four tiers, going from safest to most dangerous.

First, read-only. These don't change anything external. Things like `get_weather` or `search_tickets`. No guard needed.

Second, mutating but reversible. These do write, but undoing the write is cheap. Things like `create_ticket` or `send_draft_email`. Log every call, and that's your audit trail.

Third, mutating and irreversible. These are writes that are hard to roll back. Things like `charge_card` or `post_to_slack`. These really need explicit confirmation — not just an instruction to the model, but a code-level gate.

And finally, catastrophic. These are destructive, multi-user, loud. Things like `drop_database`, `delete_user`, or `publish_press_release`. Humans in the loop. Do not let the agent call these directly.

The temptation is to treat every tool the same, because the framework kind of treats them the same at first glance. But don't — because each tier really does deserve a different level of guardrail.

---

## Slide 23 — Where to put the guard

If there's one rule to carry forward from this interlude, it's this: **put the guard in the tool code** — not in the instruction.

And here's why that distinction really matters. An instruction is just a polite request that the model can ignore or misread. Code, on the other hand, is a wall. So if your delete-ticket tool checks for a confirmation token in Python, then no instruction in the world can bypass it. But if your check is only something like "please ask the user first" in the system prompt, the model will skip it sometimes — and the first time that costs you data, you'll wish you'd enforced it in code.

---

## Slide 24 — Confirmation gate code

In code, that guard looks like this. The tool takes an extra argument, `confirmation_token`, which is defaulted to empty. If the token matches the expected string for this specific ticket, then the delete proceeds. But if the token is empty or wrong, the function just returns a preview and does nothing.

Now the instruction to the model can say something like "call with an empty token first, show the preview, confirm with the user, and only retry with the real token if they explicitly confirm." But if the model skips any of that — if it tries to short-cut — the tool returns a preview anyway, and the delete does not happen.

Notice the subtle detail here: the expected token is computed from the ticket ID. That way, a model that somehow learned a fixed token string from training data can't just hardcode it and slip through.

---

## Slide 25 — Live: guarded delete

Over in cell twenty-five, the user says "delete ticket T-1001." Watch the event stream.

The agent calls `delete_ticket` without a confirmation token. The tool returns a preview, not a delete. The agent then surfaces the preview to the user and asks for confirmation. Only on a second turn, with the right token, would the delete actually happen. So the data is safe.

---

## Slide 26 — Choosing a flavor

Before we wrap up, let me give you a quick reference on which flavor to pick when. If the thing you want is a Python function running in-process — use FunctionTool. If it's an existing REST API with a spec — OpenAPIToolset. If it's a tool server written in any language with its own state — McpToolset. And if it's a specialist sub-agent the parent should call like a function — AgentTool.

FunctionTool is really the default. Reach for the others only when you have a specific reason — things like a language mismatch, an existing spec, or a shared tool catalog.

---

## Slide 27 — Gotchas

Before we wrap up, there are three real gotchas worth pre-empting.

The first one is that the built-in Google tools — so Search, code execution, and Vertex Search — cannot coexist with other tools in the same agent. There's an exception for Search on ADK 1.16 or later, via `bypass_multi_tools_limit=True`. Otherwise, you have to wrap each built-in tool in its own sub-agent. We'll actually do this in module eleven.

The second gotcha is around MCP stdio in Jupyter or Colab. Jupyter replaces `sys.stderr` with an object that doesn't have a `.fileno()`, which in turn breaks the subprocess spawn. Luckily, the notebook patches this in the setup cell automatically. But if you ever write your own MCP integration in a notebook, remember to patch `sys.stderr` first.

And the third gotcha: LiteLLM plus tool calls plus streaming is known to be flaky on non-Gemini models. That's why ADK defaults tool-calling demos to non-streaming, which is the right choice for our purposes. If you do turn streaming back on for production, test the tool paths hard.

---

## Slide 28 — Takeaway

So what should you carry forward from today? Tools really come in four flavors — same abstraction to the model, different integration targets. So that's FunctionTool, OpenAPIToolset, McpToolset, and AgentTool.

And then there's the design rule to remember from the interlude: blast radius really matters, which is why you want to put the guard in the tool code, not in the instruction.

---

## Slide 29 — Next

Up next in module three, we dig into Sessions, State, Events, and Artifacts — where the conversation's memory actually lives. See you there.
