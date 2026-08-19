# Google ADK — plán natáčania (MVP, voľné rozprávanie nad notebookmi)

Vytvorené 2026-08-19. Zrkadlí tab **„ADK"** v `Skillmea overview.xlsx` (Management drive) –
30 lekcií, 9 sekcií, odhad 3:14 h. Štýl = Testing GenAI: kamera + obrazovka, **rozprávaš voľne nad
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
- Model je `gemini-2.5-flash-lite` (lacný, rýchly). Ak sa demo správa čudne, **spusti bunku ešte
  raz** – je to nedeterministický model, nie chyba kódu. Outputy v notebooku sú dobré – keď sa
  ti nechce čakať, kľudne rozprávaj nad uloženým outputom a „naživo" spusti len wow bunky
  (2_3 MCP, 3_4 päť modelov, 4_3 Loop, 5_4 reštart, 6_2 HTTP).
- Odporúčané rozdelenie na 3 dni: **deň 1** = 0_1–3_3 (úvod, nb01–03), **deň 2** = 3_4–5_3
  (nb04–07), **deň 3** = 5_4–8_1 (nb08–11, záver).

---

## Úvod do kurzu

### 0_1 Vitajte v kurze: prečo agenti a prečo ADK · ~5 min · bez notebooku
- Kto si, pre koho kurz je (Python vývojári, ktorí už volali LLM API; chcú stavať agentov).
- Čo je agent jednou vetou: LLM + inštrukcie + nástroje v slučke, ktorá sa rozhoduje, čo zavolať.
- Čo je ADK: open-source framework od Googlu (Python), ale my ho používame **nezávisle od
  vendora** – cez LiteLLM a OpenRouter beží ten istý kód na Claude / GPT / Gemini / Qwen / Llama.
- Mapa kurzu: 10 notebookov = rebrík (mentálny model → nástroje → pamäť/state → výmena modelu →
  skladanie agentov → produkčné veci: callbacky, pamäť → evaluácia, nasadenie) + bonus Gemini.
- Odporúčanie: ísť lineárne, každý notebook si otvoriť a klikať spolu.
- Most: Testing kurz sa hodí po tomto (tam testujeme/útočíme na agentov, ktorých tu staviame).

### 0_2 Materiály a prostredie kurzu · ~5 min · README + nb01 bunky 2–7
- Drive priečinok (link do popisu) + GitHub `robertbarcik/ADK-tutorial`; materiály po anglicky,
  videá po slovensky (rovnaká logika ako v Testingu).
- Notebooky 01–10 = časť 1 (OpenRouter), 11–14 = Gemini natívne + A2A (samoštúdium, ukážeme 11).
- Open in Colab → Secrets: `OPENROUTER_API_KEY`; bezplatný Google AI Studio kľúč len pre nb11.
- Ukáž bunky 2–7 v nb01: pip (pinované verzie – ADK sa hýbe rýchlo), kľúč (Colab secret →
  .env → prompt), importy; `LiteLlm` = ten jeden riadok, ktorý robí ADK vendor-neutral.
- Cena: celý kurz pár dolárov; model `gemini-2.5-flash-lite`.

## Kapitola 1 · Mentálny model agenta (notebook 01)

### 1_1 Čo je agent a štyri primitívy ADK · ~7 min · nb01 bunky 1, 8 (teória)
- Väčšina tutoriálov hodí na teba 12 pojmov; ADK má v prvý deň **štyri**: `LlmAgent` (LLM +
  inštrukcie + model + nástroje), `Runner` (event loop, ktorý vedie konverzáciu), `Event` (každá
  správa, volanie nástroja, odpoveď nástroja, zmena stavu), `Session` (história eventov + slovník state).
- Tabuľka v bunke 8: „čo to je / čo s tým robíš". Všetko ostatné (workflow, multi-agent,
  callbacky, pamäť) sú kombinácie týchto štyroch.
- Voliteľne obrázok: archívny deck M01 slajdy 6–9.

### 1_2 Prvý agent a prúd eventov · ~6 min · nb01 bunky 9–13 (spusti 10, 12)
- `LlmAgent(name, model=LiteLlm(...), description, instruction)` – štyri povinné argumenty, zatiaľ
  bez nástrojov = LLM so system promptom v ADK obale.
- `chat()` helper: session per volanie, `Runner`, `run_async()` → **prúd eventov**; budeme ho
  používať celý kurz. Jedna otázka → jeden event s finálnym textom.
- Eventy = jednotka pozorovateľnosti; v ďalších videách sa prúd rozrastie.

### 1_3 Pridáme nástroj: tri eventy namiesto jedného · ~6 min · nb01 bunky 14–17 (spusti 15)
- Nástroj = funkcia s **docstringom a typovými anotáciami**; ADK z nich spraví JSON schému pre model.
- Tok: model sa rozhodne → `[tool_call] get_weather({'city': 'Prague'})` → ADK vykoná →
  `[tool_resp]` → `[FINAL]`. Tri eventy, všetko viditeľné; keby model zavolal nástroj zle, vidíš to.
- `adk web` = bezplatný vizuálny debugger (event timeline); v kurze ostaneme pri textových výpisoch.
- Domáca úloha = „Your turn" (bunka 18): vymeniť model, rozbiť nástroj (Reykjavik), pridať druhý nástroj.

## Kapitola 2 · Nástroje: štyri príchute (notebook 02)

### 2_1 Ako fungujú nástroje a FunctionTool · ~8 min · nb02 bunky 10–15 (spusti 14)
- Obrázok v bunke 10: LLM „potrebujem X" → ADK dispatch → tvoj nástroj → „X je …" → LLM.
- FunctionTool = default. **Docstring je schéma**: píš ju pre model (nemá Slack, aby sa ťa
  spýtal), typové anotácie sú nosné (`city: str` → `"type": "string"`), návratový dict stačí –
  model si z neho vyberie.
- Demo: `get_weather(city, units)` – model si zvolil `fahrenheit` podľa otázky, nič nevymyslel.

### 2_2 OpenAPIToolset: celé REST API jedným riadkom · ~6 min · nb02 bunky 16–18 (spusti 17)
- Keď máš REST API so špecifikáciou, nepíš N FunctionToolov – `OpenAPIToolset(spec)` spraví
  z každej operácie nástroj. Demo: Frankfurter (kurzy mien, bez auth), CHF → JPY.
- Pozor: operationId → snake_case (`get_latest_rate`); ADK vracia surový HTTP JSON – kontrakt API
  ladíš priamo v prúde eventov. V praxi: firemné API so swaggerom.

### 2_3 McpToolset: MCP server ako nástroj · ~7 min · nb02 bunky 19–21 (+28–29) (spusti 20, 29)
- MCP = štandard agent↔nástroj (od Anthropicu; dec. 2025 darovaný Agentic AI Foundation pod Linux
  Foundation); server = samostatný
  proces, nástroje cez stdio/HTTP.
- Repo má `mcp_servers/ticket_mcp_server.py` (5 nástrojov nad ticketmi). `McpToolset` spustí
  server, handshake, stiahne zoznam nástrojov → agent ich vidí ako lokálne (`search_tickets`).
- Hodnota: server v akomkoľvek jazyku, na inom stroji, s vlastným stavom/credentials.
- Nezabudnúť `await ticket_toolset.close()` – inak unikne subprocess.
- Most: celý kurz MCP príde neskôr (path).

### 2_4 AgentTool: agent ako nástroj · ~5 min · nb02 bunky 22–24 (spusti 23)
- Špecialista (prekladateľ do SK) zabalený ako nástroj; rodič ho volá ako funkciu a ostáva pri
  kormidle; v prúde eventov vidíš `translator({...})` → `{'result': ...}`.
- Kedy AgentTool: čistý vstup/výstup, rodič vedie konverzáciu. Kedy `sub_agents`: potomok má
  vlastniť konverzáciu – to je kapitola 4.

### 2_5 Rizikové nástroje: potvrdenie do kódu, nie do promptu · ~6 min · nb02 bunky 25–27 (spusti 26)
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
- Demo: rovnaký agent, rovnaký prompt, 5 modelov (Gemini, GPT-4o-mini, Claude Haiku 4.5, Qwen 3,
  Llama 3.1) – rozdiely v štýle a latencii, obsah konverguje. (Tu môžeš pridať svoj pohľad
  vendor vs open-weight z Testing 4_4.)

### 3_5 Ollama, natívny Gemini a kedy model naozaj meniť · ~5 min · nb04 bunky 14–15, 19 (nič nespúšťaš)
- Lokálne modely cez Ollamu: **`ollama_chat/`**, nie `ollama/` (inak nekonečné tool-call slučky).
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
- Rovnakí špecialisti (greeter, weather), iné zapojenie.
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

### 8_1 Čo ste sa naučili a čo ďalej · ~4 min · bez notebooku
- Štyri primitívy ešte raz; rebrík: nástroje → state → workflow → multi-agent → callbacky →
  pamäť → eval → deploy.
- Čo ďalej: Testovanie a bezpečnosť generatívnej AI (evaluácia + red-teaming tvojich agentov),
  MCP, vektorové databázy a RAG; Quick path pre kolegov (M01 → M02 → M05 → M11).
- Otázky do diskusie, ďakujem.

---

## Po natáčaní (pre Clauda)
Videá do `TEMP/` s názvami `<kapitola>_<video>_<nazov>.mp4` (ako pri Testingu) → `video-intake`:
kompresia, Videos drive (nový priečinok `8_Google ADK (SVK)` – registry `videos_drive` ešte nie je
nastavené), transkripty, popisy z transkriptov do tabu ADK, upload-ready kópie späť do TEMP.
