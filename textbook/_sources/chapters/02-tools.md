# Tools as verbs

If Module 01 gave you the mental model of an agent, this chapter is where the agent starts doing things. An agent without tools is a chatbot — it can only produce text. An agent with tools can look up data, call APIs, run code, talk to other agents. All the interesting properties of agent software come from the tool boundary, and almost all the interesting bugs do too. This chapter covers the four flavors of tools ADK supports, when to reach for each, and one design rule that applies across all of them.

## The tool mental model

Regardless of flavor, here is what happens when your agent calls a tool.

The model sees a **schema** — a JSON description with a tool name, a human-readable description, and a list of typed arguments. The model decides when the schema applies to the current user request, and emits a structured call: the name of the tool it wants to run, and the arguments it wants to pass. ADK catches the call before it leaves the agent. It looks up the Python code behind that schema, runs it with the arguments the model picked, wraps the return value, and feeds it back into the conversation as a tool-response event. The model reads that response and produces a natural-language answer.

That is the whole protocol. Four flavors of tools differ only in two places: where the schema comes from, and where the code lives.

```
┌─────────────┐   "I need to know X"    ┌─────────────┐
│     LLM     │────────────────────────▶│     ADK     │
│   decides   │                         │  dispatch   │
└─────────────┘                         └──────┬──────┘
       ▲                                       │
       │  "X is {...}"                         ▼
       │                                 ┌─────────────┐
       └─────────────────────────────────│  your tool  │
                                         │ (any flavor)│
                                         └─────────────┘
```

## Flavor 1 — FunctionTool

The default flavor. You write a Python function; ADK turns it into a tool. The schema comes from your function's docstring and type hints; the code runs in the same Python process as the agent.

```python
def get_weather(city: str, units: str = "celsius") -> dict:
    """Look up today's weather for a city.

    Args:
        city: The city name in English (e.g. "Prague", "Munich").
        units: Either "celsius" (default) or "fahrenheit".
    """
    ...
    return {"city": city, "temperature": ..., "condition": ..., "units": units}
```

Three things to internalize:

**The docstring is the schema the model sees.** Your job when writing a tool function's docstring is not to help a human code reviewer understand the code — your job is to help the model, which has no Slack channel to ask you what a parameter means. Every argument gets an explicit description. Ambiguity in the docstring becomes unpredictable behavior at inference time.

**Type hints are load-bearing.** ADK reads them to build the JSON schema's types. A missing hint degrades to `"type": "string"`, often silently. Always type your tool functions. If you're returning a dict, consider a TypedDict or at least document the shape in the docstring.

**Return JSON-serializable data.** A dict, a list, a string, a number. Not a Pandas DataFrame, not a NumPy array, not a custom class. The return value is sent verbatim to the model as a tool-response event, and anything unserializable crashes the dispatch.

When to reach for FunctionTool: almost always. It is the right default. The other three flavors exist for specific scenarios the default can't cover.

## Flavor 2 — OpenAPIToolset

When the thing you want to call is a REST API, and that API has an OpenAPI specification, you do not want to hand-write a FunctionTool per endpoint. `OpenAPIToolset` takes a full spec and turns every operation into a tool automatically.

```python
from google.adk.tools.openapi_tool import OpenAPIToolset

fx_toolset = OpenAPIToolset(spec_dict=FRANKFURTER_SPEC)

fx_agent = LlmAgent(
    ...,
    tools=[fx_toolset],   # every path in the spec → one tool
)
```

The spec can be a dict, a JSON string, or a YAML string. Every path in the spec becomes a tool. Parameters become tool arguments. The `summary` and `description` fields become what the model sees. The `servers[0].url` becomes the base URL.

Two things worth flagging:

**ADK snake-cases operationIds.** A spec that declares `operationId: getLatestRate` produces a tool named `get_latest_rate`. If you instruct the model to call a camelCase name, it won't find the tool. If a tool call isn't happening and you're sure the instruction is right, check whether ADK renamed the tool.

**The tool-response event is the raw API payload.** ADK does not transform the API's output before handing it to the model. That is a feature, not a bug — you can debug your API's contract directly in the event stream. But it means the model needs to be able to read the shape the API returns. If the API returns deeply nested JSON, consider a small wrapper tool that flattens it.

The production use case: your company already has an API with a spec. Point the agent at it. Every endpoint becomes an agent-callable tool with no per-endpoint glue.

## Flavor 3 — MCPToolset

Model Context Protocol is Anthropic's standard for exposing tools to agents. It was donated to the Linux Foundation in December 2025 and is now the de facto standard — Anthropic, Google, OpenAI, Microsoft, the open-source agent stack, every serious player ships MCP support. An MCP server is a separate process that exposes a set of tools; your agent connects to it over stdio or HTTP and uses its tools as if they were local.

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

ticket_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["mcp_servers/ticket_mcp_server.py"],
        ),
    )
)
```

What happens when that toolset runs: ADK spawns the server script as a subprocess, speaks the MCP handshake over stdio, and calls the server's `list_tools` method. Whatever tools the server exposes are registered as if they were local. From the agent's perspective there is no difference.

This is the most valuable property of the flavor. **The MCP server can be written in any language**, run on any machine, own any state — database connections, API credentials, caches. The agent doesn't care. It speaks the protocol; the tools show up.

Two practical notes:

**Close the toolset when you're done.** The stdio subprocess lives until you close it. Long-running agents should manage the lifecycle explicitly; short-lived notebook demos should call `await toolset.close()` at the end.

**Jupyter's `sys.stderr` doesn't have a `.fileno()`.** This is the most common gotcha. When you run an MCP stdio integration inside a Jupyter kernel (or Colab, or nbconvert), the subprocess spawn fails with a `fileno` error because ADK's MCP client tries to inherit the parent's stderr, and the parent's stderr is an ipykernel `OutStream` that lacks a file descriptor. The fix is to swap `sys.stderr` to an `os.devnull`-backed file before importing MCPToolset. Every notebook in this course that uses MCP does this in its setup cell.

## Flavor 4 — AgentTool

The fourth flavor is the most conceptually interesting. **`AgentTool` takes any existing agent and makes it callable as a tool from another agent.**

```python
from google.adk.tools.agent_tool import AgentTool

translator = LlmAgent(
    name="translator",
    description="Translates English to Slovak. Input: phrase. Output: translation.",
    instruction="You are a translation tool. Output the Slovak translation only.",
    ...
)

orchestrator = LlmAgent(
    ...,
    tools=[AgentTool(agent=translator)],
)
```

The parent's model sees `translator` as a tool — the tool name is the child's name, the tool description is the child's description. When the parent decides to call, the child runs as its own LLM call with its own instruction, produces a response, and that response comes back to the parent as a tool-response event.

This is the **consultant pattern**. The parent calls the specialist like a function. The parent stays in charge. The child answers one question, and control goes back to the parent automatically.

The alternative pattern is `sub_agents`, where the parent *transfers* the conversation to the child. The child owns the dialog — for one turn or many — until it itself decides to transfer back. That is delegation, not a function call. M06 will make the distinction crisp with a side-by-side demo; for now, the rule of thumb:

- **AgentTool** when the child has a clean input-output contract and you want it to be visible as a tool call in the parent's event stream.
- **sub_agents** when the child should own the conversation for a stretch of turns.

## Interlude — Risk-based tool design

This is the first of the Agentic Design Patterns interludes. The pattern is drawn from the *Agentic Design Patterns* publication (Chapter 4: Tool Design and Constraint Architecture). The content here is a condensed version; the publication is worth reading in full.

Not all tools are equal. A tool that reads the ticket database is not in the same category as a tool that deletes the database. The difference is **blast radius** — the scope of damage a misfiring tool call can do before anyone notices.

A practical taxonomy:

| Risk tier | Characteristic | Example | Guard |
|---|---|---|---|
| **Read-only** | No external change | `get_weather`, `search_tickets` | None |
| **Mutating, reversible** | Writes, easy to undo | `create_ticket`, `send_draft_email` | Log every call |
| **Mutating, irreversible** | Writes that can't be rolled back | `charge_card`, `post_to_slack` | **Explicit confirmation** |
| **Catastrophic** | Destructive, multi-user, loud | `drop_database`, `delete_user` | **Human in the loop** |

The temptation is to treat every tool the same because the framework treats them the same. Don't. Put the guards in the tool's implementation, not in the instruction.

**The design rule: an instruction is a polite request the model can ignore. A code-level check is a wall.**

Concretely: here is what an irreversible-tier tool looks like, with a code-level confirmation gate.

```python
def delete_ticket(ticket_id: str, confirmation_token: str = "") -> dict:
    """Delete a support ticket. IRREVERSIBLE.

    Args:
        ticket_id: The ticket to delete.
        confirmation_token: Must equal "CONFIRM_DELETE_<ticket_id>".
            Empty or wrong → returns a preview, does nothing.
    """
    expected = f"CONFIRM_DELETE_{ticket_id}"
    if confirmation_token != expected:
        return {
            "status": "preview",
            "ticket_id": ticket_id,
            "message": f"Not executed. Pass token={expected} to proceed.",
        }
    ...  # actually delete
```

Now the instruction can say "call with an empty token first to preview, show the user, confirm, and only retry with the real token if they explicitly agree." But if the model skips any of that — if it decides to short-cut — the tool returns a preview anyway. The data is safe.

Notice the subtle detail: the expected token is computed from the ticket ID. A model that somehow learned a fixed token string from training data or system-prompt exfiltration can't just hardcode it.

This pattern — **code-level gates for irreversible tools** — scales. You can apply it to `send_email` (require the user to see a draft first), to `transfer_funds` (require a signed approval token), to `post_to_social` (require a dry-run preview). The specific guard changes; the principle doesn't.

## Choosing a flavor

A quick decision guide.

- **Python function that runs in-process** → FunctionTool. The default.
- **Existing REST API with an OpenAPI spec** → OpenAPIToolset. One line, N endpoints.
- **Tool server in another language or with its own state** → MCPToolset. Language- and process-agnostic.
- **Specialist sub-agent that should be called, not delegated to** → AgentTool. Parent stays in charge.

## Gotchas worth naming now

Three real ones.

**Built-in Google tools don't mix.** Google Search, the built-in code executor, and Vertex AI Search cannot coexist with other tools in the same agent. The exception is Search, on ADK 1.16 or later, via `bypass_multi_tools_limit=True`. The general workaround is to wrap each built-in tool as an `AgentTool` and compose them through sub-agents. Module 11 will hit this directly when we use Search grounding.

**MCP stdio in Jupyter / Colab / nbconvert needs a patched `sys.stderr`.** The ipykernel environment replaces `sys.stderr` with an object that lacks `.fileno()`. The MCP subprocess spawn tries to inherit stderr and calls `.fileno()` on it. That throws. The fix is a three-line stanza in the notebook setup cell that swaps `sys.stderr` to `os.devnull` when the current stderr doesn't have a usable fileno. Every MCP-touching notebook in this course does this automatically.

**LiteLLM plus streaming plus tool calls is known flaky on non-Gemini models.** There are several open adk-python issues documenting this — #187, #2065, #3665, #3697, and more. The practical guidance for OpenRouter-backed demos: default `stream=False`. ADK does this out of the box for non-streaming runners. If you turn streaming on for production on an OpenRouter model, test the tool paths hard before shipping.

## What to carry forward

Tools come in four flavors: **FunctionTool, OpenAPIToolset, MCPToolset, AgentTool**. Same abstraction to the model; different integration targets. FunctionTool is the default; reach for the others when you have a specific reason.

And the design rule from the Agentic Design Patterns interlude: **blast radius matters**. Categorize your tools by how much damage a mis-call can do. Put the guards for irreversible tools in the code, not in the instruction. An instruction is a polite request. Code is a wall.

Module 03 picks up where the event stream leaves off. Every tool call you just saw went into the session's event history; Module 03 makes sessions, state, and events the subject.
