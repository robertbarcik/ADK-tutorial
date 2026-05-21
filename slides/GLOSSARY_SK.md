# Slovenský terminologický slovník — ADK kurz

Slovník pre slovenský preklad speaker notes kurzu **Agent Development Kit (ADK) — od základov po produkčné agenty**. Slúži ako jednotná referencia: vždy keď v texte narazíš na anglický odborný výraz, použi prislušný slovenský / hybridný ekvivalent z tohto slovníka. Cieľ je konzistencia naprieč všetkými 15 modulmi (M00–M14).

---

## Princípy

1. **Ponechané v angličtine** — keď je termín v slovenskej IT komunite zaužívaný a slovenský preklad by znel umelo (napr. *callback*, *streaming*, *prompt*, *token*, *deployment*, *tool calling*). V audio voľne skloňuj: *"v callbacku"*, *"cez middleware"*, *"po tool calle"*.
2. **Názvy ADK tried, primitív a funkcií ostávajú v angličtine** ako vlastné mená API — *LlmAgent*, *Runner*, *Session*, *Event*, *LoopAgent*, *FunctionTool*, *AgentTool*, *McpToolset*. Pri prvom výskyte v module daj jednovetnú parafrázu.
3. **Mená Python knižníc, frameworkov a SDK** (ADK, LiteLLM, FastAPI, SQLAlchemy, Ollama, Starlette, uvicorn) **neprekladaj**.
4. **Akronymy** (LLM, MCP, A2A, RAG, REST, JSON, HTTP, SDK, IAM, CI/CD) ostávajú v angličtine. Vyslovuj písmenkovo alebo ako slovo, podľa toho ako je v komunite zaužívané.
5. **Mená modelov a poskytovateľov** (Gemini, Claude, GPT, Qwen, Llama, Gemma, OpenRouter, Anthropic, Google) **neprekladaj**. Skloňuj prirodzene: *"v Geminim"*, *"od Anthropicu"*.
6. **Mená v kóde sa nikdy neprekladajú** — argumenty (`use_legacy=False`), prefixy (`user:`, `app:`, `temp:`), parametre (`output_key`, `max_iterations`), názvy súborov (`requirements.txt`, `.env`).
7. **Skloňovanie**: anglické termíny skloňuj prirodzene podľa slovenskej gramatiky — *"v notebooku"*, *"po Runneri"*, *"cez Session Service"*, *"tool-response event sme videli"*.
8. **Optimalizácia pre voiceover**: vyhni sa jazykolamom. Tam, kde slovenský preklad obsahuje veľa spoluhlások (napr. *"observovateľnosť"*), použi anglický termín (*"observability"*).

---

## A) M00 + M01 — ADK foundations a primitives

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| Agent Development Kit (ADK) | **Agent Development Kit** *(ADK)* | Vlastný názov frameworku. Pri prvom výskyte plný názov + akronym; ďalej len *"ADK"*. |
| agent | **agent** | Univerzálne, slovenský ekvivalent funguje prirodzene. |
| AI agent | **AI agent** | *"Umelointeligentný agent"* sa nepoužíva; *"AI agent"* je v SK IT bežný. |
| primitive (Agent, Runner, Event, Session) | **primitív** *(Agent, Runner, Event, Session)* | Slovenský preklad funguje; názvy primitív ponechaj anglicky ako vlastné mená API. |
| framework | **framework** | V SK IT zaužívané. |
| LLM (Large Language Model) | **LLM** | Akronym, ponechaj. |
| model | **model** | Univerzálne. |
| Runner | **Runner** | Názov ADK triedy; ponechaj. V texte parafrázuj *"spúšťač konverzácie"* pri prvom výskyte. |
| Event | **Event** | Názov ADK primitívu; ponechaj. |
| event stream | **event stream** *(prúd eventov)* | Hybrid. *"Prúd eventov"* OK v audio; *"event stream"* v texte. |
| Session | **Session** | Názov ADK primitívu; ponechaj. *"Konverzačná pamäť"* ako parafráza pri prvom výskyte. |
| instruction (system prompt) | **inštrukcia** *(system prompt)* | Slovenské *"inštrukcia"* funguje; *"system prompt"* zaužívaný anglicky. |
| tool | **nástroj** / **tool** | V texte *"nástroj"*; v technickom / kódovom kontexte *"tool"* (napr. *"tool call"*, *"tool response"*). |
| tool call | **tool call** | V SK IT zaužívané anglicky. |
| tool response | **tool response** | Detto. |
| function | **funkcia** | Univerzálne (Python). |
| async generator | **async generátor** | Hybrid; *"async"* sa neprekladá. |
| event loop | **event loop** | V SK IT zaužívané anglicky. |
| tick (game-engine metaphor) | **tick** | Anglický termín z game-dev kontextu, ponechaj. |
| game engine main loop | **hlavná slučka herného enginu** | Slovenský preklad funguje. |
| Express middleware / Node.js middleware | **Express middleware** / **Node.js middleware** | Vlastné mená frameworkov + zaužívaný termín. |
| sub-agent / sub_agents | **sub-agent** / **sub_agents** | Hybrid. V kóde `sub_agents` ostáva; v texte *"sub-agent"* zaužívaný. *"Pod-agent"* znie umelo. |
| session service | **session service** | Anglické v SK IT bežné. |
| InMemorySessionService / DatabaseSessionService / VertexAiSessionService | **InMemorySessionService** / **DatabaseSessionService** / **VertexAiSessionService** | Názvy ADK tried, neprekladaj. |
| async loop | **async slučka** | Hybrid; *"async"* sa neprekladá. |
| typed Python | **typovaný Python** | Slovenský preklad funguje. |
| graph DSL | **graph DSL** | Anglický termín, technický. |
| node-and-edge graph | **node-and-edge graf** / **graf uzlov a hrán** | Oboje funguje; v audio prirodzenejšie slovenský preklad. |
| boilerplate | **boilerplate** | V SK IT zaužívané anglicky. |
| retry loop | **retry slučka** / **retry loop** | Hybrid; *"opakovacia slučka"* tiež OK. |
| context window | **kontextové okno** | Štandardný preklad. |
| JSON parser | **JSON parser** | V SK IT zaužívané. |
| switch statement | **switch statement** / **switch konštrukcia** | V Python kontexte v SK obvykle len *"switch"*. |
| docstring | **docstring** | V SK Python komunite anglické. |
| type hint | **type hint** | Detto. |
| LiteLlm (wrapper) | **LiteLlm wrapper** | Vlastný názov ADK adaptéra; *"wrapper"* v SK IT zaužívané. |
| vendor lock-in | **vendor lock-in** | V SK IT zaužívané anglicky; *"uzamknutie na dodávateľa"* znie technokratky. |
| vendor-neutral / vendor-agnostic | **vendor-neutrálny** / **vendor-agnostický** | Hybrid. |
| adk web (CLI) | **adk web** | Názov CLI príkazu, neprekladaj. |
| clickable timeline | **klikateľná časová os** | Slovenský preklad funguje. |
| chat UI | **chat UI** | Hybrid; *"chatovacie rozhranie"* v audio OK. |
| Ollama | **Ollama** | Vlastný názov produktu. |
| Jupyter notebook | **Jupyter notebook** | Vlastný názov. *"Notebook"* samostatne tiež OK. |
| LangGraph / CrewAI | **LangGraph** / **CrewAI** | Vlastné mená frameworkov. |

---

## B) M02 — Tools (four flavors + risk-based design)

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| flavor (of tool) | **druh** / **typ** *(nástroja)* | Anglické *"flavor"* v audio znie zvláštne (*"štyri flavory nástrojov"*). V SK použi *"druh"* alebo *"typ"*. |
| FunctionTool / OpenAPIToolset / McpToolset / AgentTool | **FunctionTool** / **OpenAPIToolset** / **McpToolset** / **AgentTool** | Názvy ADK tried, neprekladaj. |
| schema | **schéma** | Slovenský termín funguje. |
| JSON schema | **JSON schéma** | Hybrid. |
| OpenAPI specification / OpenAPI spec | **OpenAPI špecifikácia** / **OpenAPI spec** | Hybrid. |
| REST API | **REST API** | Akronym, neprekladaj. |
| endpoint | **endpoint** | V SK IT zaužívané anglicky. |
| operationId | **operationId** | Pole z OpenAPI špec, neprekladaj. |
| snake-case | **snake-case** | V SK IT zaužívané. |
| YAML | **YAML** | Akronym, neprekladaj. |
| MCP (Model Context Protocol) | **MCP** *(Model Context Protocol)* | Akronym + plný názov pri prvom výskyte. |
| MCP server | **MCP server** | V SK IT bežné. |
| stdio (standard input/output) | **stdio** | V SK Python komunite anglické. |
| HTTP / Server-Sent Events / SSE | **HTTP** / **Server-Sent Events** *(SSE)* | Akronymy / vlastné mená protokolov, neprekladaj. |
| subprocess | **subprocess** | V SK Python komunite anglické. |
| AgentTool | **AgentTool** | Názov ADK triedy. |
| consultant pattern | **consultant pattern** *(vzor konzultanta)* | Hybrid; parafráza pri prvom výskyte. |
| transfer pattern | **transfer pattern** *(vzor preposlania)* | Hybrid; parafráza pri prvom výskyte. |
| orchestrator | **orchestrátor** | Slovenský preklad funguje. |
| specialist agent | **špecialistický agent** / **špecialista** | Slovenský preklad funguje. |
| parent agent | **parent agent** / **rodičovský agent** | Hybrid. |
| risk-based tool design | **rizikový dizajn nástrojov** | Slovenský preklad funguje. |
| blast radius | **blast radius** *(rozsah dopadu)* | Anglický termín z bezpečnosti; pri prvom výskyte parafráza. |
| read-only | **read-only** | V SK IT zaužívané. |
| mutating but reversible | **meniace, ale vratné** | Doslovný preklad funguje. |
| mutating and irreversible | **meniace a nevratné** | Detto. |
| catastrophic | **katastrofické** | Slovenský termín funguje. |
| audit trail | **audit trail** | V SK IT zaužívané anglicky. |
| guard / guardrail | **bezpečnostný mechanizmus** / **ochranná funkcia** | V hovorenom slove plynulejšie ako anglické *"guardrail"*. V kóde / komentároch môže anglické ostať. |
| confirmation token | **confirmation token** | Anglický bežný v IT bezpečnosti. |
| code-level gate | **code-level gate** *(brána na úrovni kódu)* | Hybrid + parafráza. |
| safety gate | **safety gate** *(bezpečnostná brána)* | Hybrid. |
| BuiltInCodeExecutor / Vertex AI Search | **BuiltInCodeExecutor** / **Vertex AI Search** | Vlastné mená Google nástrojov. |
| bypass_multi_tools_limit | **bypass_multi_tools_limit** | Názov ADK argumentu, v kóde ostáva. |
| streaming | **streaming** | V SK IT zaužívané. |
| non-streaming | **non-streaming** | Detto. |
| Frankfurter API | **Frankfurter API** | Vlastný názov verejnej API. |

---

## C) M03 — Sessions, State, Events, Artifacts

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| stateless | **bezstavový** | Štandardný preklad. |
| stateful | **stavový** | Detto. |
| state | **state** / **stav** | V technickom kontexte (kód, `state["foo"]`) *"state"*; v texte *"stav"*. |
| state dict / state dictionary | **state dict** / **stavový slovník** | Hybrid. |
| event history | **história eventov** | Hybrid. |
| state mutation | **mutácia stavu** | Slovenský preklad funguje. |
| state delta | **state delta** | Anglický termín z event sourcingu, zaužívaný. |
| key-value storage | **key-value úložisko** | Hybrid; *"key-value"* zaužívané. |
| scope prefix | **scope prefix** *(prefix rozsahu)* | Hybrid + parafráza. |
| user: prefix / app: prefix / temp: prefix | **`user:` prefix** / **`app:` prefix** / **`temp:` prefix** | V kóde ostávajú anglicky. V audio: *"user dvojbodka"*, *"app dvojbodka"*, *"temp dvojbodka"*. |
| unprefixed | **bez prefixu** | Slovenský preklad funguje. |
| four rings of scope | **štyri prstence rozsahu** / **štyri tiers** | Hybrid; metaforu *"prstence"* ponechaj v audio. |
| ToolContext / tool_context | **ToolContext** / **`tool_context`** | Názov triedy / parametra, v kóde anglicky. |
| LlmAgent | **LlmAgent** | Názov ADK triedy. |
| output_key | **`output_key`** | Argument konštruktora, neprekladaj. |
| event sourcing | **event sourcing** | V SK IT zaužívaný anglicky. |
| immutable ledger | **nemenná účtovná kniha** / **immutable ledger** | Slovenský preklad funguje aj anglický. |
| artifacts | **artifakty** | Slovenský preklad funguje. |
| binary blob | **binárny blob** / **binárny blok** | Hybrid; *"blob"* v SK IT zaužívané. |
| Git LFS | **Git LFS** | Akronym, neprekladaj. |
| Google Cloud Storage / S3 / Azure / MinIO | **Google Cloud Storage** / **S3** / **Azure** / **MinIO** | Vlastné mená produktov. |
| Skeptical Memory (pattern) | **Skeptical Memory** *(skeptická pamäť)* | Názov vzoru z Agentic Design Patterns publikácie; pri prvom výskyte parafráza. |
| Agentic Design Patterns | **Agentic Design Patterns** *(publikácia)* | Názov publikácie, neprekladaj. |
| staleness / stale memory | **staleness** *(zastaranosť)* / **zastaraná pamäť** | Hybrid + parafráza. |
| retrieval over recall | **retrieval namiesto recall** / **vyhľadávanie namiesto spomínania** | Hybrid alebo plne slovenský. |
| ground truth | **ground truth** | V SK ML zaužívané anglicky. |

---

## D) M04 — Model swap (LiteLLM, Ollama, Prompt priority tiers)

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| LiteLLM (library) | **LiteLLM** | Vlastný názov knižnice. |
| adapter / shim | **adaptér** / **shim** | Slovenský / anglický funguje. |
| OpenAI-shaped request | **OpenAI-shaped request** *(požiadavka v tvare OpenAI)* | Hybrid + parafráza. |
| translation layer | **translačná vrstva** | Slovenský preklad funguje. |
| round trip | **round trip** | V SK IT zaužívané anglicky. |
| OpenRouter | **OpenRouter** | Vlastný názov služby. |
| model string | **model string** *(reťazec modelu)* | Hybrid + parafráza. |
| provider | **poskytovateľ** / **provider** | V audio *"poskytovateľ"* prirodzenejšie. |
| per-token price | **cena za token** | Slovenský preklad funguje. |
| markup | **markup** / **prirážka** | Hybrid. |
| Gemini-Flash-Lite / GPT-4o-mini / Claude-Haiku / Qwen-3 / Llama-3.1 | **Gemini-Flash-Lite** / **GPT-4o-mini** / **Claude-Haiku** / **Qwen-3** / **Llama-3.1** | Vlastné mená modelov, neprekladaj. |
| wall time | **wall time** *(reálny čas)* | Hybrid + parafráza. |
| latency | **latencia** | Štandardný slovenský termín. |
| open-weight model | **open-weight model** | V SK ML zaužívané anglicky. |
| frontier model | **frontier model** *(špičkový model)* | Hybrid + parafráza. |
| reasoning trace | **reasoning trace** *(stopa uvažovania)* | Hybrid + parafráza. |
| chain-of-thought | **chain-of-thought** | Anglický zaužívaný termín; *"reťaz myšlienok"* znie literárne. |
| reasoning variant | **reasoning varianta** | Hybrid. |
| Ollama | **Ollama** | Vlastný názov. |
| `ollama_chat/` prefix | **`ollama_chat/` prefix** | V kóde ostáva, neprekladaj. |
| chat-completions API / completions API | **chat-completions API** / **completions API** | Vlastné mená API endpointov. |
| function-calling support | **podpora function-callingu** | Hybrid. |
| infinite loop | **nekonečná slučka** | Slovenský preklad funguje. |
| google-genai SDK | **google-genai SDK** | Vlastný názov knižnice. |
| prompt priority tier | **prompt priority tier** *(úroveň priority promptu)* | Hybrid + parafráza. |
| invariant | **invariant** | Slovenský technický termín funguje. |
| core behavior | **core behavior** *(jadrové správanie)* / **jadrové správanie** | Hybrid alebo plne slovenský. |
| preference | **preferencia** | Slovenský preklad funguje. |
| context pressure | **kontextový tlak** | Slovenský preklad funguje. |
| truncation | **truncation** / **orezanie** | Hybrid. |
| safety gate | **safety gate** *(bezpečnostná brána)* | Hybrid. |
| hard refusal | **hard refusal** *(tvrdé odmietnutie)* | Hybrid + parafráza. |
| jailbreak | **jailbreak** | V SK AI security zaužívané anglicky. |
| failover | **failover** | V SK IT zaužívané anglicky. |
| per-task capability | **per-task spôsobilosť** *(schopnosť na úlohu)* | Hybrid + parafráza. |
| cost optimization | **optimalizácia nákladov** | Slovenský preklad funguje. |

---

## E) M05 — Workflow agents (Sequential, Parallel, Loop)

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| workflow agent | **workflow agent** | Anglický termín, v SK IT zaužívaný. |
| SequentialAgent / ParallelAgent / LoopAgent | **SequentialAgent** / **ParallelAgent** / **LoopAgent** | Názvy ADK tried, neprekladaj. |
| pipeline | **pipeline** | V SK IT zaužívané anglicky. |
| shell pipeline | **shell pipeline** | Detto. |
| `asyncio.gather` | **`asyncio.gather`** | Python API, v kóde ostáva. |
| while loop | **while slučka** | Hybrid. |
| escape hatch | **escape hatch** *(núdzový východ)* | Hybrid + parafráza. |
| iteration ceiling | **iteračný strop** | Slovenský preklad funguje. |
| role-playing DSL | **role-playing DSL** | Anglický termín, zaužívaný. |
| pipe (state as pipe) | **rúra** *(state ako rúra)* | Slovenský preklad metaforu zachováva. |
| curly-brace substitution | **vkladanie premenných** *(cez zložené zátvorky `{...}`)* | Slovenský preklad pre voiceover; *"curly-brace substitúcia"* je jazykolam. |
| `{summary?}` optional variant | **`{summary?}` voliteľná varianta** | Hybrid; v kóde ostáva ako je. |
| KeyError | **KeyError** | Python výnimka, neprekladaj. |
| fan-out | **fan-out** | V SK IT zaužívané anglicky. |
| concurrent | **paralelný** / **súbežný** | Slovenský preklad funguje. |
| self-correction | **self-correction** *(sebakorekcia)* | Hybrid + parafráza. |
| critic-driven refinement | **critic-driven refinement** | Anglický pattern name, ponechaj. |
| Reflexion | **Reflexion** | Vlastný názov vzoru z literatúry. |
| draft-and-review | **draft-and-review** | Anglický pattern name. |
| generator (in Loop) | **generátor** | Slovenský preklad funguje. |
| critic (in Loop) | **kritik** | Slovenský preklad funguje. |
| exit_loop (built-in tool) | **`exit_loop`** | Názov ADK built-in toolu, v kóde anglicky. |
| max_iterations | **`max_iterations`** | Argument konštruktora, v kóde anglicky. |
| iteration | **iterácia** | Slovenský preklad funguje. |
| nesting workflow agents | **vnorenie workflow agentov** | Slovenský preklad funguje. |
| LLM-driven flow | **LLM-driven flow** *(LLM-riadený tok)* | Hybrid + parafráza. |
| determinism | **determinizmus** | Štandardný slovenský termín. |
| auditable | **auditovateľný** | Slovenský preklad funguje. |

---

## F) M06 — Multi-agent hierarchies

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| multi-agent hierarchy | **multi-agent hierarchia** | Hybrid. |
| LLM-driven routing | **LLM-driven routing** *(LLM-riadený routing)* | Hybrid + parafráza. |
| coordinator | **koordinátor** | Slovenský preklad funguje. |
| specialist | **špecialista** | Detto. |
| transfer_to_agent | **`transfer_to_agent`** | Názov built-in toolu, v kóde anglicky. |
| org-chart transfer | **org-chart transfer** *(presmerovanie podľa org-chart)* | Hybrid + parafráza. |
| routing schema | **routing schéma** | Hybrid. |
| author of final response | **autor finálnej odpovede** | Slovenský preklad funguje. |
| tell-tale sign | **tell-tale sign** *(rozpoznávací znak)* | Hybrid + parafráza. |
| multi-agent decomposition | **multi-agent dekompozícia** | Hybrid. |
| coordination tax | **coordination tax** *(daň za koordináciu)* | Hybrid + parafráza. |
| LLM invocation | **LLM invokácia** / **LLM volanie** | Slovenský preklad funguje. |
| routing error | **routing chyba** | Hybrid. |
| context fragmentation | **kontextová fragmentácia** | Slovenský preklad funguje. |
| monolithic single agent | **monolitický agent** | *"Jeden"* je redundantné — *"monolitický"* už implikuje celistvosť. |
| model heterogeneity | **heterogenita modelov** | Slovenský preklad funguje. |
| reuse test | **test opätovného použitia** | Slovenský preklad funguje. |
| instruction-scale test | **test rozsahu inštrukcie** | Slovenský preklad funguje. |
| coordinator-plus-specialists | **coordinator-plus-specialists** *(koordinátor a špecialisti)* | Hybrid + parafráza. |

---

## G) M07 — Callbacks ako middleware

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| callback | **callback** | V SK IT zaužívané anglicky. |
| middleware | **middleware** | V SK IT zaužívané anglicky. |
| lifecycle hook | **lifecycle hook** *(hook životného cyklu)* | Hybrid + parafráza. |
| pre-hook / post-hook | **pre-hook** / **post-hook** | V SK IT zaužívané anglicky. |
| request lifecycle | **request lifecycle** *(životný cyklus požiadavky)* | Hybrid + parafráza. |
| before_model_callback / after_model_callback (atď.) | názvy callbackov ponechaj v kóde anglicky | Identifikátory v kóde. |
| return-to-override | **return-to-override** *(vrátiť hodnotu = prepísať)* | Hybrid + parafráza. |
| short-circuit | **short-circuit** *(skrátiť cestu)* | Hybrid + parafráza. |
| LlmResponse | **LlmResponse** | Názov ADK triedy, neprekladaj. |
| model-role content | **model-role content** *(obsah s rolou model)* | Hybrid + parafráza. |
| blocklist | **blocklist** | V SK IT zaužívané anglicky. |
| PII (Personally Identifiable Information) | **PII** | V SK security zaužívané anglicky. |
| PII redaction | **PII redakcia** | Hybrid. |
| sensitive field | **citlivé pole** | Slovenský preklad funguje. |
| SSN (Social Security Number) | **SSN** | Akronym, neprekladaj. |
| ticker (stock) | **ticker** | V SK fintech zaužívané anglicky. |
| mocking | **mocking** | V SK testovaní zaužívané anglicky. |
| mock | **mock** | Detto. |
| test seam | **testovacie rozhranie** | *"Švík"* (Michael Feathers) znie krajčírsky; *"testovacie rozhranie"* je v SK dev komunite prirodzenejšie. |
| unit-testable | **unit-testovateľný** | Hybrid. |
| cached fallback | **cached fallback** | V SK IT zaužívané anglicky. |
| prompt injection | **prompt injection** | V SK AI security zaužívané anglicky. |
| argument validation | **validácia argumentov** | Slovenský preklad funguje. |
| plugin | **plugin** | V SK IT zaužívané anglicky. |
| org-wide policy | **org-wide policy** *(org-wide pravidlo)* | Hybrid + parafráza. |
| audit logging | **audit logging** | V SK IT zaužívané anglicky. |
| OpenTelemetry / span | **OpenTelemetry** / **span** | Vlastné mená nástrojov / zaužívané anglicky. |
| Cloud Trace / Langfuse / Arize | **Cloud Trace** / **Langfuse** / **Arize** | Vlastné mená produktov. |

---

## H) M08 — Memory (Persistence + Long-term recall)

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| persistence | **persistencia** | V SK IT zaužívané. |
| long-term recall / long-term memory | **dlhodobá pamäť** | Slovenský preklad funguje. |
| process restart | **reštart procesu** | Slovenský preklad funguje. |
| async engine | **async engine** | Hybrid; *"async"* sa neprekladá. |
| async driver / sync driver | **async driver** / **sync driver** | Anglické, v SK Python zaužívané. |
| async-URL gotcha | **async-URL gotcha** | Anglický termín *"gotcha"* v SK IT zaužívaný. |
| transitive requirement | **tranzitívna závislosť** | Slovenský preklad funguje. |
| MemoryService | **MemoryService** | Názov ADK triedy. |
| load_memory (tool) | **`load_memory`** | Názov ADK built-in toolu. |
| add_session_to_memory | **`add_session_to_memory`** | Názov metódy, v kóde anglicky. |
| search query | **vyhľadávací dopyt** | Slovenský preklad funguje. |
| archive | **archivovať** | Slovenský preklad funguje. |
| InMemoryMemoryService / VertexAiMemoryBankService | **InMemoryMemoryService** / **VertexAiMemoryBankService** | Názvy ADK tried. |
| LLM-distilled facts | **LLM-distilled facts** *(LLM-destilované fakty)* | Hybrid + parafráza. |
| deduplicate | **deduplikovať** | Slovenský preklad funguje. |
| consolidate | **konsolidovať** | Slovenský preklad funguje. |
| BaseMemoryService | **BaseMemoryService** | Názov ADK triedy. |
| vector extension | **vector extension** *(vektorová prípona)* | Hybrid; *"vector"* v SK ML zaužívané anglicky. |
| MemoryEntry | **MemoryEntry** | Názov ADK triedy. |
| grounded answer | **grounded answer** *(odpoveď s groundingom)* | Hybrid; *"grounded"* sa v SK AI ťažko prekladá kompaktne. |
| retrieve-and-verify | **retrieve-and-verify** *(vyhľadaj a over)* | Hybrid + parafráza. |
| recency metadata | **recency metadata** *(metadáta čerstvosti)* | Hybrid + parafráza. |
| decay (memory) | **decay** *(úpadok, prirodzené zastarávanie)* | Hybrid + parafráza. |
| Raspberry Pi / ESP32 | **Raspberry Pi** / **ESP32** | Vlastné mená hardvéru. |

---

## I) M09 — Evaluation

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| evaluation / eval | **evaluácia** / **eval** | Plné *"evaluácia"* v audio profesionálnejšie; *"eval"* v technickom kontexte. |
| regression | **regresia** | Slovenský preklad funguje. |
| tool_trajectory_avg_score / response_match_score | názvy metrík v kóde ponechaj anglicky | Identifikátory v kóde. |
| trajectory metric / trajectory score | **trajectory metrika** / **trajectory skóre** | Hybrid; *"trajectory"* sa v SK AI ťažko prekladá. |
| trajectory testing | **trajectory testovanie** | Hybrid. |
| ROUGE-1 / unigram overlap | **ROUGE-1** / **unigram overlap** | Akronym + technický termín, ponechaj. |
| threshold | **threshold** / **prah** | V audio *"prah"* prirodzenejšie. |
| evalset | **evalset** | Anglický termín, zaužívaný v SK AI komunite. |
| .test.json file | **`.test.json` súbor** | V kóde ostáva. |
| test_config.json | **`test_config.json`** | Detto. |
| AgentEvaluator / EvalSet | **AgentEvaluator** / **EvalSet** | Názvy ADK tried. |
| pull request / PR | **pull request** / **PR** | V SK dev komunite zaužívané anglicky. |
| CI / CI/CD | **CI** / **CI/CD** | Akronymy, zaužívané. |
| LLM-as-judge | **LLM-as-judge** *(LLM ako sudca)* | Hybrid + parafráza. |
| Gen AI Evaluation Service | **Gen AI Evaluation Service** | Vlastný názov Google služby. |
| public preview | **public preview** | V SK IT zaužívané anglicky. |
| grading rubric | **grading rubric** *(hodnotiaca rubrika)* | Hybrid + parafráza. |
| semantic correctness | **sémantická správnosť** | Slovenský preklad funguje. |
| nightly run | **nightly run** | V SK CI/CD zaužívané anglicky. |
| borderline case | **borderline prípad** | Hybrid. |
| Kubernetes | **Kubernetes** | Vlastný názov. |
| PermissionError | **PermissionError** | Python výnimka, neprekladaj. |
| writable | **writable** *(s právom zápisu)* | Hybrid + parafráza. |

---

## J) M10 — Deployment

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| deployment | **nasadenie** / **deployment** | Obidva fungujú; v audio *"nasadenie"* prirodzenejšie. |
| FastAPI | **FastAPI** | Vlastný názov frameworku. |
| container | **kontajner** | Slovenský preklad funguje. |
| Docker / Dockerfile | **Docker** / **Dockerfile** | Vlastné mená. |
| Cloud Run / GCP / Google Cloud | **Cloud Run** / **GCP** / **Google Cloud** | Vlastné mená produktov. |
| Vertex AI / Vertex AI Agent Engine | **Vertex AI** / **Vertex AI Agent Engine** | Vlastné mená produktov. |
| Memory Bank | **Memory Bank** | Vlastný názov Google produktu. |
| Agent Identity | **Agent Identity** | Vlastný názov Google produktu. |
| IAM principal | **IAM principal** | V SK cloud bezpečnosti zaužívané anglicky. |
| certificate-bound credentials | **certificate-bound credentials** *(prihlasovacie údaje viazané na certifikát)* | Hybrid + parafráza. |
| folder layout | **folder layout** *(štruktúra priečinka)* | Hybrid + parafráza. |
| `__init__.py` / `agent.py` / `requirements.txt` / `.env` | názvy súborov ostávajú | Identifikátory v kóde. |
| adk api_server / adk deploy cloud_run / adk create | **`adk api_server`** / **`adk deploy cloud_run`** / **`adk create`** | Názvy CLI príkazov. |
| HTTP service | **HTTP služba** | Hybrid. |
| localhost | **localhost** | V SK IT zaužívané. |
| endpoint | **endpoint** | V SK IT zaužívané. |
| frontend | **frontend** | V SK IT zaužívané. |
| Cloud Build / Artifact Registry | **Cloud Build** / **Artifact Registry** | Vlastné mená Google produktov. |
| AWS Fargate / Azure Container Apps / fly.io / Kubernetes | **AWS Fargate** / **Azure Container Apps** / **fly.io** / **Kubernetes** | Vlastné mená cloud platforiem. |
| slim Python base image | **slim Python base image** | Hybrid. |
| PORT env var | **`PORT` env var** | Hybrid. |
| CMD | **CMD** | Docker direktíva. |
| auto-consolidation / auto-decay | **auto-konsolidácia** / **auto-decay** | Hybrid. |
| runtime margin | **časová rezerva pre runtime** | *"Marža"* sa v slovenčine spája s financiami; v IT prirodzenejšie *"časová rezerva"*. |
| compute layer | **compute vrstva** | Hybrid. |
| storage | **storage** / **úložisko** | Oboje funguje. |
| token-budget enforcement | **token-budget enforcement** *(presadzovanie tokenového rozpočtu)* | Hybrid + parafráza. |
| rate limit | **rate limit** | V SK IT zaužívané anglicky. |
| production readiness checklist | **production readiness checklist** *(kontrolný zoznam produkčnej pripravenosti)* | Hybrid + parafráza. |
| managed Postgres | **managed Postgres** | V SK cloud zaužívané anglicky. |
| API gateway | **API gateway** | V SK IT zaužívané anglicky. |
| authenticated subnet | **authenticated subnet** | Anglický bežnejší. |
| trace backend | **trace backend** | V SK observability zaužívané anglicky. |

---

## K) M11 — Gemini grounding + Context caching

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| grounding (Gemini) | **grounding** | V SK AI zaužívané anglicky; *"ukotvenie"* znie psychologicky. |
| context caching | **context caching** | V SK AI zaužívané anglicky. |
| google_search (built-in tool) | **`google_search`** | Názov ADK built-in toolu. |
| built-in tool | **built-in tool** *(vstavaný nástroj)* | Hybrid + parafráza. |
| citation | **citácia** | Slovenský preklad funguje. |
| grounding metadata | **grounding metadáta** | Hybrid. |
| per-request / per-token billing | **per-request** / **per-token billing** | Anglické zaužívané v SK SaaS pricing. |
| context window | **kontextové okno** | Štandardný preklad. |
| 1M tokens / 2M tokens | **1M tokenov** / **2M tokenov** | Slovenský preklad funguje. |
| 500-page PDF | **500-stranové PDF** | Slovenský preklad funguje. |
| implicit caching / explicit caching | **implicit caching** / **explicit caching** | Anglické zaužívané; *"implicitné cachovanie"* v audio OK. |
| TTL (time-to-live) | **TTL** | V SK IT akronym. |
| `client.caches.create` | **`client.caches.create`** | API call, v kóde anglicky. |
| cached_content / cache.name | **`cached_content`** / **`cache.name`** | Argumenty / property, v kóde anglicky. |
| storage fee | **poplatok za úložisko** | Slovenský preklad funguje. |
| 429 error | **429 error** | HTTP error code, ponechaj. |
| free tier / paid tier | **free tier** / **paid tier** | V SK SaaS zaužívané anglicky. |
| worked example | **prepočítaný príklad** | Slovenský preklad funguje. |
| break-even | **bod zvratu** | Etablovaný slovenský biznis termín; plynulejší v audio ako *"brejk íven"*. |
| feature matrix | **feature matrix** *(matica funkcií)* | Hybrid + parafráza. |
| OpenAI-shaped interface | **OpenAI-shaped interface** | Anglický termín, viz M04. |
| multi-model failover | **multi-model failover** | V SK IT zaužívané anglicky. |

---

## L) M12 — Thinking budgets

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| thinking budget | **thinking budget** *(tokenový rozpočet na uvažovanie)* | Hybrid + parafráza; *"thinking budget"* je centrálny termín modulu. |
| internal reasoning / reasoning pass | **interné uvažovanie** / **reasoning pass** | Hybrid. |
| thoughts_token_count | **`thoughts_token_count`** | Pole v usage metadata, v kóde anglicky. |
| usage metadata | **usage metadata** | V SK API kontexte zaužívané anglicky. |
| wall-clock time | **wall-clock time** *(reálny čas)* | Hybrid + parafráza. |
| reasoning token | **reasoning token** | Hybrid. |
| ThinkingConfig | **ThinkingConfig** | Názov ADK / Google triedy. |
| thinking_level (MINIMAL/LOW/MEDIUM/HIGH) | **`thinking_level`** *(MINIMAL/LOW/MEDIUM/HIGH)* | Argument + jeho hodnoty, v kóde anglicky. |
| include_thoughts | **`include_thoughts`** | Argument, v kóde anglicky. |
| BuiltInPlanner | **BuiltInPlanner** | Názov ADK triedy. |
| planner (argument) | **`planner`** *(argument)* | V kóde anglicky. |
| step-by-step working | **krok-za-krokom postup** | Slovenský preklad funguje. |
| multi-step calculation | **viacstupňový výpočet** | Slovenský preklad funguje. |
| logic puzzle | **logická hádanka** | Slovenský preklad funguje. |
| dependency analysis | **analýza závislostí** | Slovenský preklad funguje. |
| factual lookup | **faktové vyhľadanie** | Slovenský preklad funguje. |
| text transformation | **textová transformácia** | Slovenský preklad funguje. |
| classification task | **klasifikačná úloha** | Slovenský preklad funguje. |
| thought signature | **thought signature** *(podpis myšlienky)* | Hybrid + parafráza. |
| multi-turn tool call | **multi-turn tool call** *(viackolový tool call)* | Hybrid + parafráza. |
| reasoning_effort (OpenAI) | **`reasoning_effort`** | OpenAI parameter, v kóde anglicky. |
| extended thinking (Claude) | **extended thinking** | Anthropic feature name, anglicky. |
| budget_tokens | **`budget_tokens`** | Anthropic argument, v kóde anglicky. |
| LiteLLM parity | **LiteLLM parita** | Hybrid. |

---

## M) M13 — Live API (Voice)

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| Live API | **Live API** | Vlastný názov Google produktu. |
| bidirectional audio streaming | **obojsmerný audio streaming** | Slovenský preklad funguje. |
| voice activity detection / VAD | **voice activity detection** *(VAD)* | Hybrid; *"detekcia hlasovej aktivity"* dlhé pre audio. |
| interruption handling | **interruption handling** *(spracovanie prerušení)* | Hybrid + parafráza. |
| WebSocket | **WebSocket** | V SK IT zaužívané anglicky. |
| preview-tier | **preview-tier** | V SK SaaS zaužívané anglicky. |
| 1011 error | **1011 error** | WebSocket error code, ponechaj. |
| connection drop | **connection drop** *(výpadok spojenia)* | Hybrid + parafráza. |
| timeout | **timeout** | V SK IT zaužívané. |
| `run_async` / `run_live` | **`run_async`** / **`run_live`** | Názvy ADK metód, v kóde anglicky. |
| request/response (pattern) | **request/response** *(vzor)* | Anglické zaužívané v SK IT. |
| LiveRequestQueue | **LiveRequestQueue** | Názov ADK triedy. |
| `send_content` / `send_realtime` | **`send_content`** / **`send_realtime`** | Názvy metód, v kóde anglicky. |
| raw audio bytes | **raw audio bytes** *(surové audio bajty)* | Hybrid + parafráza. |
| turn-complete event | **turn-complete event** | Anglický technický termín. |
| RunConfig / response_modalities | **RunConfig** / **`response_modalities`** | Názvy ADK tried / argumentov. |
| TEXT / AUDIO (modalities) | **TEXT** / **AUDIO** | Hodnoty enum, ponechaj. |
| raw PCM bytes | **raw PCM bytes** | PCM je akronym, anglický termín. |
| `inline_data` field | **`inline_data` pole** | Hybrid; názov poľa v kóde. |
| Live-capable model | **Live-capable model** *(model so support Live API)* | Hybrid + parafráza. |
| RealtimeInputConfig | **RealtimeInputConfig** | Názov ADK triedy. |
| silence_duration_ms / prefix_padding_ms | **`silence_duration_ms`** / **`prefix_padding_ms`** | Argumenty, v kóde anglicky. |
| end-of-turn | **end-of-turn** *(koniec ťahu)* | Hybrid + parafráza. |
| false trigger | **false trigger** *(falošné spustenie)* | Hybrid + parafráza. |
| microphone | **mikrofón** | Slovenský preklad funguje. |
| Web Audio API | **Web Audio API** | Vlastný názov browser API. |
| speech-to-text / STT | **speech-to-text** *(STT)* | V SK AI zaužívané anglicky. |
| text-to-speech / TTS | **text-to-speech** *(TTS)* | Detto. |
| transcription | **transkripcia** | Slovenský preklad funguje. |
| narration script | **scenár narácie** | Slovenský preklad funguje. |
| per-minute pricing | **per-minute cenotvorba** | Hybrid. |

---

## N) M14 — A2A protocol

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| A2A protocol | **A2A protokol** | Hybrid. *"A2A"* je akronym (agent-to-agent). |
| agent-to-agent communication | **agent-to-agent komunikácia** | Hybrid; *"medzi agentmi"* tiež OK. |
| MCP (agents-calling-tools) | **MCP** *(protokol pre agentov volajúcich nástroje)* | Akronym + parafráza pri prvom výskyte. |
| Linux Foundation | **Linux Foundation** | Vlastný názov organizácie. |
| official SDK | **oficiálny SDK** | Hybrid; *"SDK"* akronym. |
| ACP protocol (IBM) | **ACP protokol** | Hybrid. |
| Agentic AI Foundation | **Agentic AI Foundation** | Vlastný názov organizácie. |
| @a2a_experimental | **`@a2a_experimental`** | Python dekorátor, v kóde ostáva. |
| Cloud Next (Google event) | **Cloud Next** | Vlastný názov konferencie. |
| Agent Card | **Agent Card** | Centrálny názov v A2A protokole; ponechaj originál. Parafráza pri prvom výskyte *"JSON descriptor agenta"*. |
| JSON descriptor | **JSON descriptor** | Anglický bežný v SK API kontexte. |
| well-known URL | **well-known URL** | Anglický bežný v SK web štandardoch. |
| OpenAPI spec | **OpenAPI spec** | viz M02. |
| Task (A2A) | **Task** | Názov A2A primitívu; ponechaj. Parafráza *"jednotka práce"* pri prvom výskyte. |
| stateful (Task) | **stavový** | Štandardný preklad. |
| server-owned | **server-owned** *(vlastnený serverom)* | Hybrid + parafráza. |
| status: working, input-required, completed | **status: working, input-required, completed** | Hodnoty enum, ponechaj anglicky. |
| artifact (A2A) | **artifakt** | Slovenský preklad funguje. |
| GitHub Issue (analogy) | **GitHub Issue** | Vlastný názov GitHub featúry. |
| Message (A2A primitive) | **Message** | Názov A2A primitívu; ponechaj. |
| typed parts: text, file, data | **typed parts** *(text, file, data)* | Hybrid; hodnoty enum anglicky. |
| Artifact (A2A primitive) | **Artifact** | Názov A2A primitívu; ponechaj. *"Trvalý výstup"* parafráza pri prvom výskyte. |
| durable output | **durable output** *(trvalý výstup)* | Hybrid + parafráza. |
| Skills (vs Capabilities) | **Skills** *(zručnosti agenta — menu)* | Anglický termín z A2A spec; pri prvom výskyte parafráza. |
| Capabilities | **Capabilities** *(protokolové feature-flagy)* | Detto. |
| feature flag | **feature flag** | V SK IT zaužívané anglicky. |
| push notification | **push notification** | V SK IT zaužívané anglicky. |
| history replay | **history replay** *(prehratie histórie)* | Hybrid + parafráza. |
| orchestrator agent | **orchestrátor agent** | Slovenský preklad funguje. |
| `to_a2a` (function) | **`to_a2a`** | Názov ADK funkcie, v kóde anglicky. |
| Starlette app | **Starlette aplikácia** | Hybrid; *"Starlette"* je vlastný názov frameworku. |
| uvicorn | **uvicorn** | Vlastný názov servera. |
| agent-as-HTTP-service | **agent-as-HTTP-service** *(agent ako HTTP služba)* | Hybrid + parafráza. |
| JSON-RPC endpoint | **JSON-RPC endpoint** | Anglické zaužívané v SK IT. |
| task lifecycle | **task lifecycle** *(životný cyklus tasku)* | Hybrid + parafráza. |
| RemoteA2aAgent | **RemoteA2aAgent** | Názov ADK triedy. |
| `agent_card` URL (argument) | **`agent_card` URL** | V kóde anglicky. |
| `use_legacy=False` | **`use_legacy=False`** | Argument, v kóde anglicky. |
| legacy executor | **legacy executor** | Anglické zaužívané v SK IT. |
| user-message duplication | **duplikácia user správ** | Slovenský preklad funguje. |
| sub-agent output loss | **strata sub-agent výstupu** | Hybrid. |
| nested remote agent | **nested remote agent** *(vnorený vzdialený agent)* | Hybrid + parafráza. |
| event stream | **event stream** | viz M01. |
| Protocol version (0.3.0) | **verzia protokolu** *(0.3.0)* | Slovenský preklad. |
| Transport preference | **Transport preference** *(preferovaný transport)* | Hybrid + parafráza. |
| Default input/output modes | **východiskové vstupné/výstupné módy** | Slovenský preklad funguje. |
| AgentCardSignature | **AgentCardSignature** | Názov A2A triedy. |
| cryptographic identity | **kryptografická identita** | Slovenský preklad funguje. |
| root-of-trust CA | **root-of-trust CA** | V SK security zaužívané anglicky. |
| `/.well-known/agent-card.json` | **`/.well-known/agent-card.json`** | URL cesta, ponechaj. |
| a2a-sdk (0.3.24 / 1.0 alpha) | **a2a-sdk** | Vlastný názov knižnice. |
| discovery (A2A) | **discovery** *(objavovanie)* | Hybrid + parafráza. |
| registry / registries | **registry** / **registre** | Hybrid. |
| federated identity | **federovaná identita** | Slovenský preklad funguje. |
| Agent Engine (Google) | **Agent Engine** | Vlastný názov Google produktu. |
| `/v1/card` | **`/v1/card`** | URL cesta, ponechaj. |
| lethal trifecta (Simon Willison) | **lethal trifecta** *(smrtiace trio)* | viz HCAI glossary, identický termín. |
| private data + untrusted content + external communication | **súkromné dáta + nedôveryhodný obsah + externá komunikácia** | Slovenský preklad funguje. |

---

## O) Cross-cutting general terms

| Anglický originál | Slovenský preklad | Zdôvodnenie |
|---|---|---|
| API key | **API key** / **API kľúč** | Hybrid; *"API kľúč"* v audio prirodzenejšie. |
| `.env` file | **`.env` súbor** | V kóde anglicky. |
| Python | **Python** | Vlastný názov jazyka. |
| Python module / package | **Python modul** / **balík** | Slovenský preklad funguje. |
| SDK | **SDK** | Akronym, ponechaj. |
| open-source | **open-source** | V SK IT zaužívané anglicky. |
| repository / repo | **repository** / **repo** | V SK dev zaužívané anglicky. |
| GitHub | **GitHub** | Vlastný názov. |
| commit / push | **commit** / **push** | V SK dev zaužívané anglicky. |
| Git | **Git** | Vlastný názov. |
| feature | **feature** / **funkcia** | Hybrid; *"feature"* v technickom kontexte. |
| pipeline | **pipeline** | V SK IT zaužívané anglicky. |
| middleware | **middleware** | V SK IT zaužívané anglicky. |
| async / asynchronous | **async** / **asynchrónny** | Hybrid; *"async"* v kóde, *"asynchrónny"* v texte. |
| sync / synchronous | **sync** / **synchrónny** | Detto. |
| fixture (test) | **fixture** | V SK Python testovaní zaužívané. |
| demo | **demo** | Univerzálne. |
| notebook | **notebook** | Skrátené pre Jupyter notebook, v SK Python zaužívané. |
| key (API / encryption) | **kľúč** | Slovenský preklad funguje. |
| docs / documentation | **dokumentácia** | Slovenský preklad funguje. |
| concurrent / parallel | **paralelný** / **súbežný** | Slovenský preklad funguje. |
| sequential | **sekvenčný** | Detto. |
| loop | **slučka** | Slovenský preklad funguje. |
| iterate | **iterovať** | Slovenský preklad funguje. |
| async generator | **async generátor** | Hybrid. |
| dictionary / dict (Python) | **slovník** / **dict** | V texte *"slovník"*; v kóde *"dict"*. |
| list (Python) | **list** / **zoznam** | V kóde *"list"*; v texte *"zoznam"*. |
| `True` / `False` / `None` | **`True`** / **`False`** / **`None`** | Python keywords, ponechaj. |
| docstring | **docstring** | V SK Python zaužívané. |
| type hint | **type hint** | Detto. |
| package install / `pip install` | **`pip install`** | V kóde anglicky. |
| environment variable / env var | **environment variable** / **env var** | V SK dev zaužívané anglicky. |
| port (network) | **port** | Univerzálne. |
| Docker image | **Docker image** | V SK DevOps zaužívané anglicky. |
| service | **služba** | Slovenský preklad funguje. |
| client (API) | **klient** | Slovenský preklad funguje. |
| server | **server** | Univerzálne. |
| backend | **backend** | V SK IT zaužívané anglicky. |
| production | **produkcia** | Slovenský preklad funguje. |
| production-ready | **production-ready** | V SK IT zaužívané anglicky. |

---

## P) Acronyms — ostávajú v angličtine

| Akronym | Plné znenie | Vyslov v audio ako |
|---|---|---|
| **ADK** | Agent Development Kit | *"A-D-K"* po písmenkách |
| **LLM** | Large Language Model | *"L-L-M"* |
| **API** | Application Programming Interface | *"A-P-I"* |
| **MCP** | Model Context Protocol | *"M-C-P"* |
| **A2A** | Agent-to-Agent | *"A-2-A"* alebo *"agent-to-agent"* |
| **SDK** | Software Development Kit | *"S-D-K"* |
| **HTTP / HTTPS** | HyperText Transfer Protocol | *"H-T-T-P"* / *"H-T-T-P-S"* |
| **JSON** | JavaScript Object Notation | *"džejson"* (slovo) |
| **YAML** | YAML Ain't Markup Language | *"jamel"* (slovo) |
| **REST** | Representational State Transfer | *"rest"* (slovo) |
| **JSON-RPC** | JSON Remote Procedure Call | *"džejson R-P-C"* |
| **SSE** | Server-Sent Events | *"S-S-E"* |
| **VAD** | Voice Activity Detection | *"V-A-D"* |
| **TTS / STT** | Text-to-Speech / Speech-to-Text | *"T-T-S"* / *"S-T-T"* |
| **PCM** | Pulse Code Modulation | *"P-C-M"* |
| **PII** | Personally Identifiable Information | *"P-I-I"* |
| **SSN** | Social Security Number | *"S-S-N"* |
| **CI / CI/CD** | Continuous Integration / Continuous Delivery | *"C-I"* / *"C-I-C-D"* |
| **PR** | Pull Request | *"pé-er"* alebo *"P-R"* |
| **IAM** | Identity and Access Management | *"I-A-M"* |
| **CA** | Certificate Authority | *"C-A"* |
| **TTL** | Time-To-Live | *"T-T-L"* |
| **CLI** | Command Line Interface | *"C-L-I"* |
| **DSL** | Domain-Specific Language | *"D-S-L"* |
| **UI** | User Interface | *"U-I"* alebo *"juáj"* |
| **DAG** | Directed Acyclic Graph | *"dag"* (slovo) |
| **GCP** | Google Cloud Platform | *"G-C-P"* |
| **AWS** | Amazon Web Services | *"A-W-S"* |
| **GPU / CPU / RAM** | — | po písmenkách |
| **ROUGE-1** | Recall-Oriented Understudy for Gisting Evaluation (1-gram) | *"rúdž jedna"* |
| **PR / FastAPI / SQL / SQLite / Postgres / MySQL** | mená produktov | viz O |

---

## Q) Vlastné mená — NEPREKLADAJ

Spoločnosti, produkty, modely, frameworky, prípady — vždy ponechaj v originálnom anglickom znení. Skloňuj podľa slovenskej gramatiky (*"v Geminim"*, *"od Anthropicu"*, *"cez LiteLLM"*, *"s Cloud Runom"*).

**Spoločnosti / poskytovatelia:** Google, Anthropic, OpenAI, IBM, Microsoft, AWS, Cisco, Salesforce, SAP, ServiceNow, Linux Foundation, Agentic AI Foundation, Meta, Alibaba, DeepSeek.

**Modely:** Gemini (2.5 Flash / 2.5 Pro / Flash-Lite / 3.0 / 3.1 / Live), Claude (Haiku / Opus 4 / Sonnet / 4.5), GPT (-4o / -4o-mini / -5 / o3), Qwen (3 / 3-8B), Llama (3.1), Gemma, DeepSeek-R1.

**ADK / Google produkty:** ADK, Google AI Studio, Vertex AI, Vertex AI Agent Engine, Memory Bank, Agent Identity, Cloud Run, Cloud Build, Cloud Trace, Cloud Logging, Artifact Registry, Gen AI Evaluation Service, BuiltInCodeExecutor, Vertex AI Search.

**Frameworky / knižnice:** ADK, LiteLLM, FastAPI, SQLAlchemy, Starlette, uvicorn, asyncio, aiosqlite, greenlet, Playwright, Ollama, Jupyter, Colab, LangGraph, CrewAI, AutoGen, LangChain, OpenTelemetry, Langfuse, Arize, Pydantic, Docker, Kubernetes.

**Cloud platformy:** Google Cloud / GCP, AWS, Azure, AWS Fargate, Azure Container Apps, fly.io.

**Databázy:** PostgreSQL / Postgres, MySQL, SQLite, Redis, MinIO.

**Hardware / IoT:** Raspberry Pi, ESP32, Pi 5.

**Protokoly / štandardy:** MCP, A2A, OpenAPI, JSON-RPC, WebSocket, REST, HTTP, gRPC, OAuth.

**Publikácie / vzory / autori:** Agentic Design Patterns (publikácia), Skeptical Memory (vzor), Simon Willison (autor), lethal trifecta (Willisonov termín), Reflexion (vzor).

**Verejné API:** Frankfurter API.

---

## Použitie

Keď budeš prekladať konkrétne speaker notes, pre každý odborný výraz nájdi riadok v tomto slovníku a použi zvolený slovenský / hybridný / anglický variant. Cieľová konzistencia: žiadny termín nesmie byť v rôznych moduloch preložený inak.

Ak narazíš na termín, ktorý tu nie je → najprv overí či nevyplýva z analógie (napr. *"tool-response event"* → kombinácia *"tool response"* + *"event"*), a ak je nový, doplň ho sem skôr, než pôjdeš prekladať.

Hybridné riešenia (anglický termín + slovenská parafráza v zátvorke pri prvom výskyte) sú často najlepší kompromis — pri prvom výskyte v module daj plnú parafrázu, ďalej len anglický termín.
