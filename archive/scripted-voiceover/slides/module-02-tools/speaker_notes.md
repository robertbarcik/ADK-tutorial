# M02 — Speaker notes

---

## Slide 1 — Title

Welcome to module two: tools as verbs. This is the module where agents become useful. By the end you'll have built one of each of four different flavors of tool, picked up the mental model that ties all four together, learned one design rule about treating risk differently per tool, and walked through a short interlude on safety. Let's go.

---

## Slide 2 — Without / with tools

Without tools, an agent is just a chatbot. It can write text, answer questions, hold a conversation, and that's the whole scope. With tools, the agent becomes software. It can reach out, look up data, change state, run code, talk to other agents, anything you can put behind a function. That's the difference between something that talks and something that does. The rest of this module is about how to wire that "doing" part in safely.

---

## Slide 3 — The tool mental model

Let me walk through what actually happens when an agent calls a tool. When the model decides a tool is needed, it emits a structured call: the tool name plus the arguments it wants to pass. ADK catches that call, finds the code behind it, runs the code, wraps the return value, and feeds it back to the model as a tool-response event. From there, the model produces a final answer based on what the tool returned.

This is the same shape, regardless of what kind of tool you're wiring up. The only things that change between the four flavors are where the schema comes from, and where the code runs. That's really it. Just those two dimensions vary.

---

## Slide 4 — Four flavors differ only in two things

Here's the table you should carry in your head: four flavors of tool.

First, FunctionTool. The schema comes from your Python function's docstring and type hints, and the code lives in your own Python file. This is the kind of tool we already worked with: just a plain Python function.

Second, OpenAPIToolset. The schema comes from an OpenAPI specification, and the code lives behind a remote HTTP API somewhere on the network.

Third, McpToolset. The schema comes from an MCP server's list-tools response, and the code lives in a separate process, often written in a different language.

And finally, AgentTool. The schema comes from another agent's name and description, and the code is that other agent itself.

The key thing is that it's the same abstraction to the model. The model really cannot tell the difference between these four at the schema level. Today, we'll build one of each.

---

## Slide 5 — Flavor 1: FunctionTool

Let's start with flavor one. FunctionTool is just plain Python functions wired into an agent. You don't have to write a separate schema or any configuration file. ADK looks at the function itself, specifically at the docstring and the type hints, and figures out everything the LLM needs from there. The next slide unpacks how that actually happens.

---

## Slide 6 — The docstring is the schema

The core idea behind FunctionTool is this: the docstring is the schema.

So what does that mean in practice? A docstring is the block of text you put right under a function definition in Python, wrapped in triple quotes, that describes what the function does and what its arguments are for. It's normally there as a note for human readers. But in ADK, the docstring becomes the main source of the JSON description that's sent to the LLM. That JSON description is what we call the schema, and it tells the model the tool's name, what arguments it takes, what each argument means, and what shape the return value will have.

This has three practical consequences. First, you want to write the docstring for the model to read, not for a human code reviewer. The model has no way to ask you what a parameter means. So every argument needs an unambiguous description, written for an LLM.

Second, the type hints are load-bearing. A missing type hint silently degrades to a string in the schema. So always type your tool functions.

And third, you want to return a JSON-serializable dictionary or string. Not a custom Python class, and not a NumPy array. The return value is sent verbatim to the model as a tool-response event, which means it has to be something JSON knows how to represent.

---

## Slide 7 — A FunctionTool with a rich docstring

Here on the slide we have a function called `get_weather`. It takes a city name and an optional `units` argument, and it looks up today's weather for that city. The docstring inside the function does the heavy lifting. It explains what the function does, names each argument, and tells the model when to use each one.

This is what a rich, model-friendly docstring looks like. Let's walk through how each part of it ends up in the schema the LLM sees.

The Args block in the docstring becomes the parameter descriptions the model reads. The type hint `city: str` becomes `"type": "string"` in the schema. And the Python default value `units = "celsius"` becomes `"required": false` for that argument, meaning the model is allowed to leave it out.

One small design note worth calling out. I tell the model explicitly when to use fahrenheit: "only if the user explicitly asks for it." Without that specific sentence, the model would just guess, and you'd get inconsistent units across calls.

---

### Notebook break — FunctionTool in action

[Switch the screen to the notebook.]

Here's the same `get_weather` function we just saw, wired into a working weather agent. I'll send a question that exercises the optional argument: "What's the weather in Munich? Reply in Fahrenheit." [Run the cell.] Watch the tool call arguments in the event stream. The model picked `units='fahrenheit'` because the docstring told it when to. The tool returns a number, and the model formats it into an English sentence for the user. Without that one sentence in the docstring, the model would have guessed celsius and the user would have been confused.

[Switch back to the slide deck.]

---

## Slide 8 — Flavor 2: OpenAPIToolset

Now to flavor two: OpenAPIToolset. The motivation here is different from FunctionTool. With FunctionTool you write the Python code yourself. But what if the thing the agent needs to call is a REST API that already exists, complete with a specification? You don't want to hand-write a wrapper for every endpoint. That's what OpenAPIToolset is for.

---

## Slide 9 — When your target is a REST API with a spec

When the thing you want to call is a REST API that already has an OpenAPI spec, you don't want to hand-write a FunctionTool per endpoint. Instead, you hand ADK the spec, and you get N tools automatically.

Let me make this concrete with a real example. Imagine you work at an online store. Your e-commerce platform already has a REST API with an OpenAPI spec, used by the web frontend, the mobile app, and a couple of internal dashboards. Endpoints like `getOrder`, `cancelOrder`, `listProducts`, `updateInventory`. Now you want to build a customer-support agent that can answer questions like "where is my order?". Without OpenAPIToolset, you'd write a Python wrapper for each endpoint by hand: one for `getOrder`, one for `cancelOrder`, one for `listProducts`. With OpenAPIToolset, you point ADK at the same spec the frontend already uses, and the agent suddenly has every endpoint available as a tool, with no extra code.

There's one quirk worth knowing about. ADK snake-cases operation IDs. So if your spec says `operationId: getLatestRate`, the tool the model actually sees is named `get_latest_rate`. If a call isn't happening and you're sure the instruction is right, check whether ADK has renamed the tool.

---

## Slide 10 — Frankfurter currency API: three lines to integrate

Wiring OpenAPIToolset into an agent really takes three lines, and you can see all three on the slide. We take an OpenAPI specification, which can be a Python dictionary, a JSON string, or a YAML string, and pass it into `OpenAPIToolset`. The resulting toolset then goes into the agent's `tools=` list. That's it. The agent now has every endpoint in the spec available as a tool.

For our demo, we're using a free public API called Frankfurter. It returns currency exchange rates, requires no authentication, and exposes a single endpoint for fetching the latest rate. That makes it a clean teaching example. The OpenAPI spec we're passing to ADK is short, just one endpoint described in around twenty lines of YAML. So our agent ends up with exactly one tool: `get_latest_rate`.

In a real production setting, your spec would be much bigger, maybe tens or hundreds of endpoints. Every one of those endpoints would automatically become a tool the agent can call, and you wouldn't have to write any per-endpoint glue code. That's the whole pitch of OpenAPIToolset.

---

### Notebook break — OpenAPIToolset against Frankfurter

[Switch the screen to the notebook.]

Here we have the Frankfurter spec wired into an `OpenAPIToolset`, and the resulting toolset handed to the agent. I'll ask: "What's the exchange rate from Swiss francs to Japanese yen?" [Run the cell.] Look at the event stream. The model called the auto-generated `get_latest_rate` tool with `base='CHF'` and `symbols='JPY'`. The tool response is the raw JSON body Frankfurter returned, completely unchanged. The model then reads the `rates.JPY` field and produces the final answer. Notice ADK didn't transform the API output at all. It just passed it through, which makes the API contract transparent and easy to debug.

[Switch back to the slide deck.]

---

## Slide 11 — Flavor 3: McpToolset

On to flavor three: McpToolset. This is the flavor that lets your agent talk to a completely separate tool server, often written in a different language, often running as a different process, often holding its own state like a database connection or API credentials. The interface between the agent and that server is standardised through a protocol called MCP, which we'll meet on the next slide.

---

## Slide 12 — MCP in one paragraph

MCP stands for Model Context Protocol. It's Anthropic's standard for exposing tools to agents, donated to the Linux Foundation in December 2025, and it's now the de facto standard for agent-to-tool communication across the industry. Anthropic, Google, OpenAI, Microsoft, the open-source stack, all of them support it.

An MCP server is essentially a separate process that your agent connects to over stdio, HTTP, or Server-Sent Events, and then uses the server's tools as if they were local.

Here's why MCP really matters. The server can be written in any language: TypeScript, Go, Rust, whatever you want. It can run on any machine. And it can own any state, like database connections, API credentials, or caches. The agent doesn't need to know any of that. It just speaks the protocol, and the tools show up.

---

## Slide 13 — Connect to an existing MCP server

Connecting to an existing MCP server takes only a few lines of code, which you can see on the slide. We create an `McpToolset`, give it connection parameters that say how to reach the server, and pass it to the agent's `tools=` list. ADK does the rest.

Let me unpack what's happening underneath. The connection parameters describe how to reach the MCP server. In this case, over stdio, meaning ADK will spawn the server as a subprocess and talk to it over standard input and output. The arguments say which Python interpreter to run and which script file to launch.

This repo ships three ready-made MCP servers in the `mcp_servers/` folder: one for tickets, one for a knowledge base, and one for system monitoring. We're using the ticket server here. It exposes five tools internally, and as a result, five tools appear in the agent with no extra code.

---

### Notebook break — McpToolset against the ticket server

[Switch the screen to the notebook.]

Here ADK spawns the ticket MCP server as a subprocess and lists its tools automatically. The agent now has five tools available without us writing any of them. I'll ask: "Find any open tickets about WiFi." [Run the cell.] Watch the event stream. The model called `search_tickets`, which came from the MCP server, not from any Python code in this file. The response is the server's payload wrapped in an MCP content envelope. The model extracts the ticket details and answers in English. And the whole time, the ticket database lives inside the subprocess, where the agent never sees it directly.

[Switch back to the slide deck.]

---

## Slide 14 — Flavor 4: AgentTool

And the final flavor is AgentTool. This is the most reflexive of the four. With AgentTool, the thing your agent is calling is another agent, wrapped to look like a tool. Useful when you have a specialist agent, say a translator or a code reviewer, that you want to plug into a bigger workflow without it taking over the conversation.

---

## Slide 15 — The consultant pattern

This fourth flavor has a conceptual subtlety worth getting right. ADK actually has two ways to put one agent inside another: AgentTool and sub_agents. They are not interchangeable.

AgentTool is the consultant pattern. The parent calls the specialist like a function. The parent stays in charge, the child answers, and then control goes back to the parent automatically.

sub_agents is the transfer pattern. The parent hands the conversation over entirely. The child then owns the conversation, whether that's for one turn or twenty turns, until the child itself decides to transfer back.

So the rule of thumb is this. Use AgentTool when the child has a clean input-output contract, and use sub_agents when the child should drive the dialog. We'll come back to this comparison in detail later in the course. For today, just focus on the consultant pattern.

---

## Slide 16 — A translator, called like a function

Here on the slide we have two agents. The first one is `translator`: a specialist whose only job is to translate English to Slovak. The second one is `orchestrator`, the parent agent that talks to the user. Instead of putting the translator into `sub_agents` and handing the conversation over, we wrap it in `AgentTool` and hand that to the orchestrator as if it were just another tool in its `tools=` list.

Now the orchestrator's model sees `translator` in its tools list, with the translator's description as the tool description. When a user asks for a translation, the orchestrator calls the translator, gets its translation back, and incorporates it into the reply. The orchestrator stays in charge the whole time, and you see both agents' work in the same event stream.

---

### Notebook break — AgentTool with the translator

[Switch the screen to the notebook.]

Here's the orchestrator agent with the translator wrapped as an `AgentTool`. I'll send a request: "Translate 'good morning' to Slovak." [Run the cell.] Watch what happens in the event stream. The orchestrator calls the `translator` tool, which is itself an LLM call running a separate agent. The translator produces "dobré ráno" and that response comes back as a tool-response event. The orchestrator then writes the final reply to the user. Two model calls in one event trace, both visible, both inspectable, the parent never lost control of the conversation.

[Switch back to the slide deck.]

---

## Slide 17 — Interlude: Risk-based tool design

Time for a quick interlude on risk-based tool design. This is one of the ten patterns from the Agentic Design Patterns publication, and the idea matters enough that I want to pause the flavor tour and make you think about it before we continue.

---

## Slide 18 — Categorize tools by blast radius

Not all tools are equal. A tool that reads a ticket is just not in the same category as a tool that deletes the database. The difference between them is blast radius: the scope of damage a misfiring tool call can do before anyone notices.

A practical taxonomy looks like this. Four tiers, going from safest to most dangerous.

First, read-only. These don't change anything external. Things like `get_weather` or `search_tickets`. No guard needed.

Second, mutating but reversible. These do write, but undoing the write is cheap. Things like `create_ticket` or `send_draft_email`. Log every call, and that's your audit trail.

Third, mutating and irreversible. These are writes that are hard to roll back. Things like `charge_card` or `post_to_slack`. These need explicit confirmation, not just an instruction to the model, but a code-level gate.

And finally, catastrophic. These are destructive, multi-user, loud. Things like `drop_database`, `delete_user`, or `publish_press_release`. Humans in the loop. Do not let the agent call these directly.

The temptation is to treat every tool the same, because the framework kind of treats them the same at first glance. But don't, because each tier really does deserve a different level of guardrail.

---

## Slide 19 — The rule: put the guard in the tool code

If there's one rule to carry forward from this interlude, it's this: put the guard in the tool code, not in the instruction.

Here's why that distinction really matters. An instruction is just a polite request that the model can ignore or misread. Code, on the other hand, is a wall. If your delete-ticket tool checks for a confirmation token in Python, then no instruction in the world can bypass it. But if your check is only something like "please ask the user first" in the system prompt, the model will skip it sometimes. And the first time that costs you data, you'll wish you'd enforced it in code.

---

## Slide 20 — A delete tool with a confirmation gate

Take a look at the code on the slide. The function is called `delete_ticket`, and it's exactly what it sounds like: a tool that would permanently delete a support ticket. The interesting part is the extra argument, `confirmation_token`, which is defaulted to an empty string. The function checks the token against an expected value computed from the ticket ID. If the token matches, the delete proceeds. If the token is empty or wrong, the function just returns a preview and does nothing.

Now the instruction to the model can say something like: "call with an empty token first, show the preview, confirm with the user, and only retry with the real token if they explicitly confirm." But if the model skips any of that, if it tries to short-cut and just calls the delete directly, the tool returns a preview anyway, and the delete does not happen.

Notice the subtle detail here. The expected token is computed from the ticket ID. That way, a model that somehow learned a fixed token string from training data can't just hardcode it and slip through.

---

### Notebook break — The guarded delete in action

[Switch the screen to the notebook.]

Here's the agent with the guarded `delete_ticket` tool wired in. The user says: "Delete ticket T-1001." [Run the cell.] Look at what happens in the event stream. The agent called `delete_ticket` without a confirmation token, because that's the default first call. The tool returned a preview, not a deletion. The agent surfaces the preview to the user and asks them to confirm. The data is safe. On a second turn with the correct token, the delete would actually run, but only with that explicit hand-off.

[Switch back to the slide deck.]

---

## Slide 21 — Choosing a flavor

Before we wrap up, let me give you a quick reference on which flavor to pick when. If the thing you want is a Python function running in-process, use FunctionTool. If it's an existing REST API with a spec, use OpenAPIToolset. If it's a tool server written in any language with its own state, use McpToolset. And if it's a specialist sub-agent that the parent should call like a function, use AgentTool.

FunctionTool is really the default. Reach for the others only when you have a specific reason: a language mismatch, an existing spec, or a shared tool catalog.

---

## Slide 22 — Gotchas worth knowing now

There are three real gotchas worth pre-empting before you leave.

The first one is that the built-in Google tools, like Search, code execution, and Vertex Search, cannot coexist with other tools in the same agent. There's an exception for Search on ADK 1.16 or later, via `bypass_multi_tools_limit=True`. Otherwise, you have to wrap each built-in tool in its own sub-agent. We'll see this pattern later in the course when we cover Gemini-specific features.

The second gotcha is around MCP stdio in Jupyter or Colab. Jupyter replaces `sys.stderr` with an object that doesn't have a `.fileno()`, which breaks the subprocess spawn. Luckily, the notebook patches this in the setup cell automatically. But if you ever write your own MCP integration in a notebook, remember to patch `sys.stderr` first.

And the third gotcha. LiteLLM plus tool calls plus streaming is known to be flaky on non-Gemini models. That's why ADK defaults tool-calling demos to non-streaming, which is the right choice for our purposes. If you do turn streaming back on for production, test the tool paths hard.

---

## Slide 23 — What to carry forward

So what should you carry forward from today? Tools really come in four flavors. Same abstraction to the model, different integration targets. So that's FunctionTool, OpenAPIToolset, McpToolset, and AgentTool.

And then there's the design rule to remember from the interlude. Blast radius matters, which is why you want to put the guard in the tool code, not in the instruction.

---

## Slide 24 — Up next

Up next, we dig into Sessions, State, Events, and Artifacts: where the conversation's memory actually lives. We'll cover how to make an agent remember a user across separate conversations, the four-tier scope system that decides whether memory lasts a turn or forever, and the three patterns for writing state. See you there.
