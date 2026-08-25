# Google ADK — plán natáčania (MVP, voľné rozprávanie nad notebookmi)

Vytvorené 2026-08-19, prepracované 2026-08-24 (nadväznosť na predchádzajúci kurz). Zrkadlí tab
**„ADK"** v `Skillmea overview.xlsx` (Management drive) – 31 lekcií, 9 sekcií, odhad ~3:25 h.

**Kurz je priame pokračovanie „Úvod do GenAI v Pythone".** Študent prichádza s function callingom
(notebook 5 tamtoho kurzu: `get_current_weather`, ručná JSON schéma, `available_functions`,
`chat_with_function_execution`, `weather_assistant`), s OpenAI Responses API a Colab Secrets.
NEPOZNÁ: async/await, triedy, dekorátory. nb01 začína mostom — jeho kód, jedna zmenená
linka (`base_url` na OpenRouter) — a mapuje jeho loop na 4 primitívy ADK. Každý notebook má hore
blok „Where you are". MCP pozná len ako hosted tool z 9_tools (rekap v nb02). Štýl = Testing GenAI: kamera + obrazovka, **rozprávaš voľne nad
notebookom**, jedno video = jeden úsek notebooku (3–10 min). Žiadny skript; body nižšie sú len
opora, čo nevynechať. Pôvodný formát (slajdy + speaker notes, 77 lekcií) je odložený v
`archive/scripted-voiceover/` – keby si chcel ukázať obrázok, decky tam stále fungujú
(`archive/scripted-voiceover/slides/module-NN-*/index.html`).

Prioritizácia ako pri Testingu: hraničné koncepty (priority tiers, interlude o dekompozícii,
„Your turn", Key takeaways) **ostávajú len v notebooku** – nie sú lekciou. Ak ti pri natáčaní
niečo vyjde prirodzenejšie zlúčiť alebo vyhodiť, urob to a ja potom zosúladím tab (ako pri Testingu).

## Pred natáčaním (5 min)

- Notebooky bežia na **ADK 2.7.1** (re-run 2026-08-19, všetkých 14 zelených, outputy uložené).
  Lokálne: venv `.venv27`; v Colabe stačí Open in Colab (pip bunka má správne piny).
- Kľúče: `OPENROUTER_API_KEY` (všetko), `GOOGLE_API_KEY` len pre 7_1 (nb11). Lokálne v `.env`,
  v Colabe ako Secrets – ako v Testingu.
- Kapitola 6_2 (nb10) štartuje server na porte **8765** – skontroluj `lsof -i :8765` (včera tam
  visel starý http.server z knihy).
- Model je `openrouter/openai/gpt-5.6-luna` (lacný, rýchly, od 2026-08-23 nahrádza gemini-2.5-flash-lite;
  zámerne **nie** Google model – ukazuje, že ADK je vendor-neutral). Ak sa demo správa čudne, **spusti bunku ešte
  raz** – je to nedeterministický model, nie chyba kódu. Outputy v notebooku sú dobré – keď sa
  ti nechce čakať, kľudne rozprávaj nad uloženým outputom a „naživo" spusti len wow bunky
  (2_3 MCP, 3_4 päť modelov, 4_3 Loop, 5_4 reštart, 6_2 HTTP).
- Odporúčané rozdelenie na 3 dni: **deň 1** = 0_1–3_3 (úvod + most, nb01–03; kapitola 1 má teraz
  4 videá), **deň 2** = 3_4–5_3 (nb04–07), **deň 3** = 5_4–8_1 (nb08–11, záver).

---

## Úvod do kurzu

### 0_1 Vitajte: od function callingu k agentom (pokračovanie kurzu GenAI v Pythone) · ~6 min · deck `slides_intro/`
- **Slajdy `slides_intro/index.html`** (7 slajdov, pravý dolný roh voľný na talking head).
- Sľub z konca minulého kurzu splnený: rebrík function calling → vlna open-source agentov (popularizácia)
  → MCP (štandardizácia) → **ADK = orchestračná vrstva** („aj sub-agent je len function call").
- Kľúčová veta kurzu: **agenta ste už postavili** — `weather_assistant()` z notebooku 5; tu ten
  loop dostane mená: LlmAgent / Runner / Event / Session (slajdy 3–4, ten istý diagram dvakrát).
- Mapa kurzu (slajd 5), vstupné požiadavky (slajd 6: absolvovaný GenAI v Pythone, OpenRouter kľúč,
  Colab), ako študovať + čo potom: Testing GenAI (slajd 7).

### 0_2 Materiály, prostredie a prečo OpenRouter · ~6 min · README + nb01 bunky 2–5
- Drive priečinok (link do popisu) + GitHub `robertbarcik/ADK-tutorial`; materiály po anglicky,
  videá po slovensky (rovnaká logika ako v Testingu a GenAI v Pythone).
- Notebooky 01–10 = časť 1 (OpenRouter), 11–14 = Gemini natívne + A2A (samoštúdium, ukážeme 11).
- **Otázka dňa jedna: „mám OPENAI_API_KEY, prečo nový kľúč?"** – bunka 4 v nb01 na to odpovedá:
  OpenAI kľúč otvára jedného vendora; OpenRouter = jeden kľúč + jedna faktúra pre všetkých
  (v 3_4 pobeží ten istý agent na piatich). Celý kurz pár dolárov; model `openai/gpt-5.6-luna`.
- Setup rituál ako v minulom kurze: Colab Secrets (🔑) → `.env` (novinka, vysvetlená) → prompt.
- Ukáž bunky 2–5 v nb01: pip (pinované verzie – ADK sa hýbe rýchlo), kľúč.

## Kapitola 1 · Mentálny model agenta (notebook 01)

### 1_1 Od function callingu k agentom: váš kód, jedna zmena · ~8 min · nb01 bunky 1, 6–9 (spusti 7, 8)
- Bunka 1: „Where you are" + splnený sľub. Bunka 6: rekap notebooku 5 minulého kurzu menami
  (`get_current_weather`, ručná `tools` schéma, `available_functions`, `chat_with_function_execution`).
- **Spusti 7**: ich kód, jediná zmena = `base_url="https://openrouter.ai/api/v1"` + model
  `openai/gpt-5.6-luna` (bez `openrouter/` prefixu – to príde až s LiteLLM, povedz to nahlas).
- **Spusti 8**: kondenzovaný loop (kroky 1–5, vrátane ich fake-user-message skratky – pomenuj ju).
- Bunka 9: strop tohto prístupu (1 kolo, fake user message, loop per projekt, žiadna pamäť,
  žiadna observabilita) + **mapovacia tabuľka** kus→kus na ADK. Tá tabuľka je celé video.

### 1_2 Štyri primitívy ADK a mapovanie na váš loop · ~6 min · nb01 bunky 10–12 (spusti 11)
- Bunka 10: LiteLLM = `base_url` trik zovšeobecnený na 100+ providerov; `LiteLlm` (trieda ADK) vs
  `litellm` (knižnica); prefix `openrouter/openai/gpt-5.6-luna` vysvetlený.
- Spusti 11 (importy). Bunka 12: štyri primitívy — tabuľka + reprise: `Runner` = tvojich 5 krokov
  napísaných raz; `Session` = tvoj messages list s domovom; tvoje printy = `Event`.
- Voliteľne obrázok: archívny deck M01 slajdy 6–9.

### 1_3 Prvý agent a prúd eventov · ~6 min · nb01 bunky 13–18 (spusti 14, 17)
- `LlmAgent(name, model=LiteLlm(...), description, instruction)` – štyri povinné argumenty, zatiaľ
  bez nástrojov = LLM so system promptom v ADK obale.
- Pred spustením: bunka 15 odpovedá na otázky v hlave študenta („načo Runner, doteraz mi stačili
  funkcie?", „čo je async a prečo?", „čo je stream?", „prečo je chat() taký dlhý?") – prejdi ich
  nahlas, je to prvý async v ich živote (2 pravidlá: `async def` + `await`).
- Bunka 15: porovnanie s natívnym Gemini – `model="gemini-2.5-flash"` ako obyčajný string vs
  `LiteLlm(...)` obal; jediný rozdiel, všetko ostatné (Runner, Session, eventy) identické.
  Presne preto sme na LiteLlm forme – dôkaz, že ADK nie je viazané na Google modely.
- `chat()` helper: session per volanie, `Runner`, `run_async()` → **prúd eventov**; budeme ho
  používať celý kurz. Jedna otázka → jeden event s finálnym textom.
- Eventy = jednotka pozorovateľnosti; v ďalších videách sa prúd rozrastie.

### 1_4 Pridáme nástroj: docstring namiesto schémy · ~6 min · nb01 bunky 19–24 (spusti 20, 22)
- Najlepší riadok mapovacej tabuľky: v moste písali 34-riadkovú schému ručne; tu `tools=[funkcia]`
  a schému vyrobí ADK z docstringu + typových anotácií (ktoré už písať vedia).
- **Spusti 20**: funkcia z mosta zopakovaná priamo pod výkladom (type hints + docstring pred očami)
  a hneď vypísaná vygenerovaná JSON schéma (`_get_declaration()`) – porovnaj s ručnou schémou;
  úprimná poznámka: ADK 2.7 posiela docstring vcelku, `Args:` sekciu nerozdeľuje per parameter.
- Tok: model sa rozhodne → `[tool_call] get_current_weather({'location': 'Prague', ...})` → ADK
  vykoná → `[tool_resp]` → `[FINAL]`. Tri eventy; keby model zavolal nástroj zle, vidíš to.
- `adk web` = bezplatný vizuálny debugger (event timeline); v kurze ostaneme pri textových výpisoch.
- Domáca úloha = „Your turn" (bunka 25): úloha 0 = ich starý loop na Claude (1 riadok!), vymeniť
  model v ADK, rozbiť nástroj (Reykjavik), vrátiť `get_n_day_weather_forecast` z notebooku 5.

## Kapitola 2 · Nástroje: štyri príchute (notebook 02)

### 2_1 Ako fungujú nástroje a FunctionTool · ~8 min · nb02 bunky 10–16 (spusti 14, 16)
- Obrázok v bunke 10: LLM „potrebujem X" → ADK dispatch → tvoj nástroj → „X je …" → LLM.
- FunctionTool = default. **Docstring je schéma**: píš ju pre model (nemá Slack, aby sa ťa
  spýtal), typové anotácie sú nosné (`city: str` → `"type": "string"`), návratový dict stačí –
  model si z neho vyberie.
- Demo: `get_current_weather(location, format="celsius")` – tá istá funkcia ako v moste, default
  hodnota = voliteľný parameter. Model si zvolil `fahrenheit` podľa otázky, nič nevymyslel.
- **Spusti 16**: `FunctionTool(...)._get_declaration()` – vygenerovaná schéma vedľa ich ručnej
  z minulého kurzu. Rovnaká informácia, jeden artefakt namiesto dvoch.

### 2_2 OpenAPIToolset: celé REST API jedným riadkom · ~6 min · nb02 bunky 17–19 (spusti 18)
- Keď máš REST API so špecifikáciou, nepíš N FunctionToolov – `OpenAPIToolset(spec)` spraví
  z každej operácie nástroj. Demo: Frankfurter (kurzy mien, bez auth), CHF → JPY.
- Pozor: operationId → snake_case (`get_latest_rate`); ADK vracia surový HTTP JSON – kontrakt API
  ladíš priamo v prúde eventov. V praxi: firemné API so swaggerom.

### 2_3 McpToolset: MCP server ako nástroj (+ rekap MCP) · ~8 min · nb02 bunky 20–24 (+31–32) (spusti 23, 32)
- **Rekap (bunky 20–21)**: MCP stretli 2×: remote MCP ako hosted tool v minulom kurze (klienta
  bežal OpenAI) a MCP kurz (stavali server). Tu prvý raz: **ADK je klient na tvojom stroji a server
  spúšťa ako subprocess** – tabuľka „čo je tentokrát inak". Subprocess = druhý program, stdio.
- Repo má `mcp_servers/ticket_mcp_server.py` (5 nástrojov nad ticketmi). `McpToolset` spustí
  server, handshake, stiahne zoznam nástrojov → agent ich vidí ako lokálne (`search_tickets`).
- Hodnota: server v akomkoľvek jazyku, na inom stroji, s vlastným stavom/credentials.
- Nezabudnúť `await ticket_toolset.close()` – inak unikne subprocess.
- Most: celý kurz MCP príde neskôr (path).

### 2_4 AgentTool: agent ako nástroj · ~5 min · nb02 bunky 25–27 (spusti 26)
- Špecialista (prekladateľ do SK) zabalený ako nástroj; rodič ho volá ako funkciu a ostáva pri
  kormidle; v prúde eventov vidíš `translator({...})` → `{'result': ...}`.
- Kedy AgentTool: čistý vstup/výstup, rodič vedie konverzáciu. Kedy `sub_agents`: potomok má
  vlastniť konverzáciu – to je kapitola 4.

### 2_5 Rizikové nástroje: potvrdenie do kódu, nie do promptu · ~6 min · nb02 bunky 28–30 (spusti 29)
- Blast radius: read-only / vratné / nevratné – a podľa toho stráž.
- Demo `delete_ticket`: bez `confirmation_token` vráti **preview**, nie zmazanie; stráž je
  porovnanie reťazcov v Pythone – model ju neukecá, prompt injection ju neobíde.
- Most na Testing kurz (nepriama injekcia do agenta, ktorý koná).

## Kapitola 3 · Pamäť v rámci session a výmena modelu (notebooky 03 a 04)

### 3_1 Session a state: prefixy rozhodujú, čo prežije · ~6 min · nb03 bunky 8–9 (teória)
- Session = `(app_name, user_id, session_id)`; drží eventy (append-only) + state (dict).
  Tri služby: InMemory / Database / Vertex.
- **Prefixy kľúčov** (málo zdokumentované, denne používané): bez prefixu = táto session,
  `user:` = používateľ naprieč sessionmi, `app:` = globálne, `temp:` = jedno volanie.

### 3_2 Pamäť naprieč sessionmi v 80 riadkoch · ~8 min · nb03 bunky 10–19 (spusti 11, 13, 16, 19)
- Nástroj s `tool_context: ToolContext` zapíše `user:favorite_color`; `output_key` uloží poslednú
  odpoveď bez prefixu.
- Session 2 toho istého používateľa **štartuje** s `user:favorite_color`, `last_response` tam nie je.
  Agent zavolá `recall_favorite_color` → „Teal." Žiadna DB, žiadny vector store – prefix.
- Pasca (bunka 19): `sess.state["..."] = ...` na vrátenej session sa **neuloží** – trvalé sú len
  `output_key` a `tool_context.state`.

### 3_3 Eventy ako ledger a artefakty · ~5 min · nb03 bunky 20–24 (spusti 21)
- Prejdi históriu session 1: 4 eventy, `state_delta` pri každom zápise; state = projekcia eventov
  (event sourcing – log súbor so štruktúrou).
- Artefakty = Git LFS pre agentov (binárne dáta mimo eventov), tri služby ako pri sessions.
- Minúta z interlude: pamäť zastaráva – čo si agent „pamätá" o projekte spred mesiacov, over.

### 3_4 LiteLLM: jeden agent, päť poskytovateľov · ~7 min · nb04 bunky 8–13 (spusti 11, 12)
- `LiteLlm` = prekladová vrstva k ~100 poskytovateľom (OpenAI tvar → čokoľvek); Google ju
  zabalil do ADK, aby nepísal shim per vendor.
- OpenRouter konvencia `openrouter/<provider>/<model>`; jeden kľúč, jedna faktúra.
- Demo: rovnaký agent, rovnaký prompt, 5 modelov (Gemini 3.7 Flash, GPT-5.6 Luna, Claude Haiku 4.5,
  Qwen 3.7 Flash, Llama 4 Scout) – rozdiely v štýle a latencii, obsah konverguje. Qwen „myslí
  nahlas" (reasoning z Pod kapotou presakuje ako text) – ukázať sa dá cez chat() z M01. (Tu môžeš pridať svoj pohľad
  vendor vs open-weight z Testing 4_4.)

### 3_5 Ollama, natívny Gemini a kedy model naozaj meniť · ~5 min · nb04 bunky 14–15, 19 (nič nespúšťaš)
- Lokálne modely cez Ollamu (v minulom kurze bežali Qwen cez HF – toto je ekvivalent pre vlastný
  stroj): **`ollama_chat/`**, nie `ollama/` (inak nekonečné tool-call slučky).
- `model="gemini-2.5-flash"` (natívne) vs `LiteLlm("openrouter/google/...")` – oboje funguje,
  natívny string otvára Gemini-only funkcie (kapitola 7).
- Kedy meniť: výpadok providera, úloha pre konkrétny model, cena. Nezávislosť od vendora je
  schopnosť, nie zvyk. (Priority tiers 16–18 ostávajú v notebooku – max. jednou vetou.)

## Kapitola 4 · Skladanie agentov (notebooky 05 a 06)

### 4_1 Tri spôsoby skladania a SequentialAgent · ~7 min · nb05 bunky 8–11 (spusti 10)
- ASCII obrázok: Sequential / Parallel / Loop.
- Pipeline sumarizátor → prekladateľ: `output_key="summary"` zapíše do state, `{summary}` v
  inštrukcii ďalšieho agenta číta. **State je rúra**; `{key?}` = voliteľné.

### 4_2 ParallelAgent: fan-out a čas · ~5 min · nb05 bunky 12–14 (spusti 13)
- Traja výskumníci súbežne, každý do vlastného kľúča; autori sa prepletajú podľa dokončenia;
  čas ≈ najpomalší, nie súčet (pozri `⏱ Total wall time`).

### 4_3 LoopAgent: generátor a kritik · ~8 min · nb05 bunky 15–17 (spusti 16)
- Kanonický vzor ADK: generátor → kritik zapíše kritiku do state → generátor číta `{critique?}`
  a opraví → kým kritik nezavolá `exit_loop`. **Vždy `max_iterations`.**
- Prečítaj slučku v prúde eventov (niekedy prejde na prvý pokus – povedz, že to je tiež výsledok;
  prípadne sprísni kritika a spusti znova).

### 4_4 Vnorené workflow a kedy nechať rozhodovať LLM · ~5 min · nb05 bunky 18–21 (spusti 19)
- Workflow sú agenti → vnárajú sa: paralelný prieskum + sekvenčná syntéza (5 volaní za čas ~2).
- Deterministické workflow (predvídateľné, testovateľné) vs orchestrátor s `sub_agents`, kde
  LLM vyberá ďalší krok (flexibilné, drahšie, ťažšie testovať).

### 4_5 Dva vzory multi-agent: transfer a konzultant · ~9 min · nb06 bunky 8–23 (spusti 13, 14, 19, 20)
- Splnený sľub z videa o function callingu v minulom kurze: „sub-agent ako function call" –
  presne toto video. Rovnakí špecialisti (greeter, weather), iné zapojenie.
- `sub_agents`: koordinátor → `transfer_to_agent` → **špecialista vlastní konverzáciu**
  (org chart). `AgentTool`: koordinátor položí otázku, dostane výsledok, **ostáva pri kormidle**.
- Vedľa seba v prúde eventov (bunka 22); pravidlo výberu (bunka 23); kedy sa multi-agent
  vôbec neoplatí (jeden agent s nástrojmi je často dosť). Interlude 24 len spomenúť.

## Kapitola 5 · Produkčné zručnosti (notebooky 07 a 08)

### 5_1 Callbacky ako middleware: šesť hookov, jedno pravidlo · ~5 min · nb07 bunky 8–10, 20 (teória)
- before/after × agent/model/tool = šesť hookov. **Jedno pravidlo**: vráť `None` = pokračuj,
  vráť hodnotu = prepíš výsledok (return-to-override). Analógia HTTP middleware.
- Tabuľka šiestich hookov (bunka 20) – kedy ktorý.

### 5_2 Guardrail pred modelom: blocklist · ~6 min · nb07 bunky 11–13 (spusti 12)
- `before_model_callback` vidí požiadavku skôr než LLM: `password` → pripravená odpoveď, **nula
  tokenov**. Normálna otázka prejde.
- Zaraď vedľa LLM guardrailov z Testing kurzu (tam druhý model, tu deterministický kód).

### 5_3 Redakcia PII po nástroji a mockovanie nástrojov v testoch · ~8 min · nb07 bunky 14–22 (spusti 15, 18)
- `after_tool_callback`: HR nástroj vráti plat/SSN/adresu → callback ich zamaskuje skôr, než
  ich model uvidí; odpoveď agenta to potvrdí.
- `before_tool_callback`: pre AAPL vráti mock (short-circuit), MSFT ide na „skutočné" API –
  šev pre testy bez volania drahých API (most na Testing nb02).
- Kedy callbacky vs inštrukcie vs kód nástroja vs pluginy (bunka 21: callbacky = logika jedného
  agenta, pluginy = politika celej aplikácie) + gotcha pozorovateľnosti (bunka 22: callbacky sa
  neobjavujú v OpenTelemetry trace – vidíš LLM a tool spany, nie „before_model_callback bežal“;
  ak to potrebuješ, loguj v callbacku sám).

### 5_4 Perzistentné sessions: SQLite a reštart procesu · ~7 min · nb08 bunky 8–14 (spusti 10, 12, 14)
- Dve časové škály: session (minúty–hodiny) vs dlhodobá pamäť (mesiace).
- `DatabaseSessionService(db_url="sqlite+aiosqlite:///...")` – jeden riadok namiesto InMemory
  (pozor: async driver povinný). Ulož preferenciu → súbor existuje → **nová služba nad tým istým
  súborom** = simulovaný reštart → nová session štartuje s `user:preference` → agent cez
  `recall_preference` odpovie.
- Produkcia: vymeníš URL za Postgres/MySQL.

### 5_5 Dlhodobá pamäť: MemoryService a load_memory · ~7 min · nb08 bunky 16–25 (spusti 19, 21, 23)
- Minulá konverzácia (RaspiKitchen, Pi 5, ESP32) → `add_session_to_memory` → nová session:
  agent zavolá `load_memory` a vybaví si projekt aj hardvér.
- InMemoryMemoryService = keyword search; produkcia = Vertex / vlastný vector store.
- Interlude (bunka 25): skeptická pamäť – na dlhých horizontoch over, čo si vybavíš.

## Kapitola 6 · Evaluácia a nasadenie – prehliadky (notebooky 09 a 10)

### 6_1 Evaluácia agentov: prehliadka notebooku 09 · ~10 min · nb09 bunky 8–21 (scrollovať, outputy sú uložené)
- Dve metriky: **trajektória nástrojov** (zavolal správne nástroje v správnom poradí?) a zhoda
  odpovede (ROUGE-1) – trajektória je tá dôležitá.
- Modul agenta na disku + `.test.json` (prompt, očakávané tool calls, očakávaná odpoveď) →
  `AgentEvaluator.evaluate` → FAILED pri prahu 0.95 (0.84 – „cloudy and 14°C" vs „cloudy and
  14 degrees Celsius") → `test_config.json` s rozumným prahom → PASS.
- Pointa: ROUGE nie je kvalita → skutočný upgrade je LLM sudca (**Testing kurz, kapitola 3**);
  `adk eval` CLI slučka: konverzácia v `adk web` → Save as eval → spúšťaj v CI.

### 6_2 Agent ako HTTP služba: adk api_server · ~7 min · nb10 bunky 5–11 (spusti 6, 8, 9, 11)
- Nasaditeľný priečinok: `__init__.py`, `agent.py` s `root_agent`, `requirements.txt`, `.env`.
- `adk api_server <dir>` → FastAPI; `/list-apps`, vytvor session, `POST /run` s JSON správou →
  3 eventy späť, finálna odpoveď. **Toto je produkčný tvar** – ten istý JSON voči Cloud Run.
- Stopni server (bunka 11). (Ak 404 na `/list-apps`: port 8765 obsadený.)

### 6_3 Docker, Cloud Run, Agent Engine a checklist · ~6 min · nb10 bunky 12–22 (prehliadka)
- Dockerfile (python slim, pip, `adk api_server --host 0.0.0.0 --port $PORT`) – nasadíš kamkoľvek.
- `adk deploy cloud_run` (jeden príkaz, GCP účet), Vertex AI Agent Engine (spravovaná cesta,
  sessions/memory za teba), pluginy = prierezové veci (logging, rate limit, auth).
- Production readiness checklist (bunka 18) – prečítaj body, ktoré považuješ za najdôležitejšie.
- „Part 1 wrap" – čo už vieš postaviť.

## Kapitola 7 · Bonus: natívne Gemini (notebook 11; 12–14 samoštúdium)

### 7_1 Čo získate s natívnym Gemini: grounding cez Google Search · ~8 min · nb11 bunky 9–13 (spusti 11; potrebuje GOOGLE_API_KEY)
- Prepnutie: Google AI Studio kľúč + **obyčajný string modelu** (nie LiteLlm) → Gemini-only funkcie.
- `google_search` ako vstavaný nástroj: odpoveď s aktuálnymi dátami + grounding metadata
  (zdroje) v evente – skutočné citácie.
- Pasca miešania: vstavané nástroje sa nekombinujú s vlastnými funkciami v jednom agentovi
  (sub-agent alebo `bypass_multi_tools_limit`).
- Čo ešte je v notebookoch 11–14 (len spomenúť): context caching (na platenom tieri), thinking
  budgety (nb12), hlasové Live API (nb13), A2A protokol (nb14) – materiály sú v Drive/GitHube.

## Záver

### 8_1 Čo ste sa naučili a čo ďalej · ~5 min · bez notebooku (voliteľne slajdy 2 a 7 z `slides_intro/`)
- Rebrík z úvodu, teraz dokončený: function calling (minulý kurz) → MCP → **ADK** – sľub splnený;
  z `weather_assistant()` je LlmAgent s Runnerom, Session a eventmi.
- Štyri primitívy ešte raz; kurzový rebrík: nástroje → state → workflow → multi-agent → callbacky →
  pamäť → eval → deploy.
- Čo ďalej: Testovanie a bezpečnosť generatívnej AI (evaluácia + red-teaming agentov, ktorých ste
  tu postavili), MCP, vektorové databázy a RAG; Quick path pre kolegov (M01 → M02 → M05 → M11).
- Otázky do diskusie, ďakujem.

---

## Po natáčaní (pre Clauda)
Videá do `TEMP/` s názvami `<kapitola>_<video>_<nazov>.mp4` (ako pri Testingu) → `video-intake`:
kompresia, Videos drive (nový priečinok `8_Google ADK (SVK)` – registry `videos_drive` ešte nie je
nastavené), transkripty, popisy z transkriptov do tabu ADK, upload-ready kópie späť do TEMP.
