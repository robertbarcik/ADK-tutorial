# Google ADK — plán natáčania (MVP, voľné rozprávanie nad notebookmi)

Vytvorené 2026-08-19, prepracované 2026-08-24 (nadväznosť) a 2026-08-25 (notebooky 01–02
v classroom štýle; videá kapitol 1–2 = pomenované sekcie notebooku, nie čísla buniek). Zrkadlí tab
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

### 0_2 Materiály, prostredie a prečo OpenRouter · ~6 min · README + nb01 sekcia „Setup“
- Drive priečinok (link do popisu) + GitHub `robertbarcik/ADK-tutorial`; materiály po anglicky,
  videá po slovensky (rovnaká logika ako v Testingu a GenAI v Pythone).
- Notebooky 01–10 = časť 1 (OpenRouter), 11–14 = Gemini natívne + A2A (samoštúdium, ukážeme 11).
- **Otázka dňa jedna: „mám OPENAI_API_KEY, prečo nový kľúč?"** – sekcia „One New Key — OpenRouter"
  v nb01 na to odpovedá: OpenAI kľúč otvára jedného vendora; OpenRouter = jeden kľúč + jedna
  faktúra pre všetkých (v 3_4 pobeží ten istý agent na piatich). Celý kurz pár dolárov.
- Setup rituál ako v minulom kurze: Colab Secrets (🔑) → `.env` (novinka, vysvetlená) → prompt.
- Ukáž sekciu „Setup" v nb01: pip (pinované verzie – ADK sa hýbe rýchlo) + kľúč. Nič viac.

## Kapitola 1 · Váš prvý agent v ADK (notebook 01)

Notebook 01 má po prerábke (2026-08-25) krátke bunky v štýle GenAI v Pythone: každá sekcia =
motivácia → kód → „🔍 What just happened?" → „🎯 Mini-task". Video = sekcia (H1 nadpis), nie
čísla buniek — pri natáčaní scrolluj po nadpisoch.

### 1_1 Agent, ktorého ste už postavili · ~8 min · nb01 sekcie „The Agent You Already Built" → „The Ceiling" → „The Map"
- Otvor sekciou „The Agent You Already Built": rekap notebooku 5 ich menami (`get_current_weather`,
  ručná `tools` schéma, `available_functions`, `chat_with_function_execution`).
- **Spusti obe bunky mosta**: ich kód, jediná zmena = `base_url` na OpenRouter + prefix
  `openai/gpt-5.6-luna` (bez `openrouter/` – ten príde až s LiteLLM, povedz to nahlas).
- „🔍 What just happened?": rozhodni – vykonaj – odpovedz = agent. Postavili ho pred mesiacmi.
- Sekcia „The Ceiling": päť limitov (1 kolo, falošná user správa, loop per projekt, žiadna pamäť,
  žiadna pozorovateľnosť). Sekcia „The Map": **mapovacia tabuľka kus→kus** – tá je celé video.

### 1_2 Čo je LiteLLM a štyri stavebné kocky ADK · ~6 min · nb01 sekcie „What Is LiteLLM?" → „The Four Building Blocks"
- LiteLLM = `base_url` trik zovšeobecnený na 100+ providerov (knižnica, nie Google); `LiteLlm`
  (trieda ADK) = malý adaptér do `model=`. Nemeníme nastavenia ADK, nepíšeme kód modelu.
- Trojdielny model string `openrouter / openai / gpt-5.6-luna` – ASCII diagram v notebooku.
- Spusti importy. Sekcia „The Four Building Blocks": tabuľka + reprise (Runner = tvojich 5 krokov
  napísaných raz; Session = messages list s domovom; printy = Eventy).

### 1_3 Prvý agent: Runner, Session a dve pravidlá async · ~6 min · nb01 sekcia „Your First Agent"
- `LlmAgent(...)` = len popis, žiadne API volanie – preto hneď potrebujeme Runner.
- Bunka „na natívnom Gemini": jeden obyčajný string vs `LiteLlm(...)` obal – celý rozdiel;
  presne preto sme na LiteLlm (dôkaz vendor-neutrality).
- Tri krátke bunky odpovedajú na otázky v hlave študenta: načo Runner (agent je loop), čo je
  Session, čo je async (**dve pravidlá**: `async def` + `await` – ich prvý async v živote),
  čo je stream (`async for`, event za každý krok).
- Bunka „The helper, line by line": chat() v piatich obyčajných vetách (otvor priečinok,
  najmi operátora, odovzdaj obálku Content/Part, sleduj eventy, zvyšok je printovanie).
- Spusti `chat()` helper + greeter; „🔍": jeden event = minimum konverzácie.

### 1_4 Pridáme nástroj: docstring je schéma · ~6 min · nb01 sekcie „Add a Tool" → „A Word on adk web" → „Key Takeaways"
- Najlepší riadok mapy: v moste 34-riadková schéma ručne; tu `tools=[funkcia]`.
- **Spusti bunku so schémou**: funkcia z mosta zopakovaná + vygenerovaná JSON schéma
  (`_get_declaration()`); porovnaj s ručnou. Úprimne: ADK 2.7 posiela docstring vcelku
  (`Args:` sekciu nerozdeľuje per parameter).
- **Spusti weather agenta**: prúd narastie na tri eventy (tool_call → tool_resp → FINAL).
- `adk web` = bezplatný vizuálny debugger (folder layout, event timeline); v kurze ostávame
  v notebookoch. „🎯 Mini-tasks" ako domáca úloha; Key Takeaways prečítaj voľne.

## Kapitola 2 · Nástroje: štyri príchute, jeden príbeh (notebook 02)

Notebook 02 je po prerábke (2026-08-25) prerozprávaný cez jeden príbeh: **IT helpdesk**. Každá
príchuť = jedna požiadavka zamestnanca; tabuľka príchutí sa opakuje na začiatku každej sekcie
(vždy vieš, kde si). Video = sekcia, nie čísla buniek.

### 2_1 Príbeh IT helpdesku a 1. príchuť: vlastná funkcia · ~8 min · nb02 sekcie „One Story, Four Flavors" → „How Every Tool Works" → „Flavor 1"
- Otvor príbehom: staviame agenta pre IT helpdesk; štyri požiadavky dňa = štyri príchute nástrojov.
- Setup len preleť (rovnaký rituál ako M01; plumbing vysvetlený v komentároch).
- „How Every Tool Works": diagram (LLM rozhodne → ADK dispatch → nástroj → výsledok) + tabuľka
  štyroch príchutí (odkiaľ je schéma, kde žije kód).
- **Spusti Flavor 1**: `check_system_status` („nejde mi VPN – je down?") + checklist dobrého
  nástroja; default hodnota = voliteľný argument. **Spusti aj vytlačenie schémy** – `required`
  obsahuje len `system`.

### 2_2 2. príchuť: cudzie webové API (OpenAPI) · ~6 min · nb02 sekcia „Flavor 2"
- Požiadavka z finance: faktúra vo frankoch. Dáta žijú v cudzej službe – nepíšeme FunctionTool
  per endpoint, dáme ADK **„menu" celého API** = OpenAPI špecifikáciu (tá istá idea menu ako
  schéma nástroja z minulého kurzu).
- Prejdi spec zhora nadol (servers → paths → get → parameters → responses); `description` polia
  hrajú rolu docstringu.
- Bunka „The key line": `OpenAPIToolset(spec_dict=...)` dekódovaná upokojujúco – tá istá
  dvojica schéma + kód ako pri Flavor 1, len schéma je zo spec-u a „kód" je HTTP request,
  ktorý ADK napíše za teba; `tools=[fx_toolset]` = balík nástrojov do toho istého slotu.
- **Spusti** – Frankfurter, CHF→JPY.
- „🔍": ⚠️ `getLatestRate` → `get_latest_rate` (snake_case!); surový HTTP JSON sa vracia nezmenený.

### 2_3 3. príchuť: MCP server (s rekapituláciou MCP) · ~8 min · nb02 sekcia „Flavor 3"
- Požiadavka: „aký je stav môjho tiketu?" – tikety žijú v databáze, nástroje už existujú ako
  MCP server v repe.
- **Najprv „First, Look Inside"**: importuj `ticket_mcp_server.py` ako obyčajný modul,
  **spusti priame volanie** `call_tool("search_tickets", {"query": "wifi"})` – databáza je
  dict, nástroje sú obyčajné funkcie; v súbore spoznajú SVOJ vzor z notebooku 5 (ručné
  schémy v list_tools + if/elif dispatch v call_tool). MCP = len vrstva, ktorá to servíruje
  cez stdin/stdout iným programom. Až potom teória.
- „MCP in 60 Seconds": stretli ho 2× (hosted tool v minulom kurze – klienta bežal OpenAI;
  MCP kurz – písali obe strany). Tabuľka „What's Different This Time": tu je klientom ADK
  a server beží ako **subprocess** (vysvetlený: druhý program, stdin/stdout, žiadna sieť).
- Vnorený `McpToolset(StdioConnectionParams(StdioServerParameters(...)))` čítaj zvnútra von:
  ktorý program spustiť → ako s ním hovoriť (stdio) → odovzdaj ADK. **Spusti** – handshake,
  5 nástrojov, ten istý WiFi tiket ako pri priamom volaní. „🔍": reasoning summary GPT-5.6 (Pod kapotou)
  + dva tool cally v jednom evente (paralelné volania = schopnosť modelu).
- Cleanup (koniec notebooku): `await ticket_toolset.close()` – nezabudni spustiť pri 2_5.

### 2_4 4. príchuť: agent ako nástroj (AgentTool) · ~5 min · nb02 sekcia „Flavor 4"
- Požiadavka: preklad odpovede do slovenčiny – nie lookup, treba jazykový model → helpdesk
  **konzultuje špecialistu**: druhý agent zabalený cez `AgentTool`, volaný ako funkcia.
- **Spusti prekladateľa.** Rodič zostáva pri kormidle; kontrast so `sub_agents` (transfer celej
  konverzácie) jednou vetou – naostro v 4_5.

### 2_5 Nebezpečné nástroje: potvrdenie patrí do kódu · ~6 min · nb02 sekcie „Interlude" → „Cleanup" → „Key Takeaways"
- Helpdesk vie tikety čítať – má ich vedieť aj mazať? **Blast radius** ako os návrhu (tabuľka
  4 úrovní rizika).
- **Spusti `delete_ticket`**: bez tokenu vráti náhľad, nie zmazanie. Stráž = porovnanie reťazcov
  v Pythone – „instruction je prosba, kód je múr". Most ku kurzu Testovanie GenAI.
- Spusti Cleanup (`close()`), Key Takeaways voľne, avízo na M03.

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

### 3_3 Každý krok je Event; súbory ako artefakty · ~5 min · nb03 bunky 20–24 (spusti 21)
- Prejdi históriu session 1: 4 eventy, `state_delta` pri každom zápise; state = projekcia eventov
  (event sourcing – log súbor so štruktúrou).
- Artefakty = Git LFS pre agentov (binárne dáta mimo eventov), tri služby ako pri sessions.
- Minúta z interlude: pamäť zastaráva – čo si agent „pamätá" o projekte spred mesiacov, over.

### 3_4 Jeden agent, päť modelov: výmena jedným riadkom · ~7 min · nb04 bunky 8–13 (spusti 11, 12)
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

### 4_1 Skladanie agentov a prvý workflow: SequentialAgent · ~7 min · nb05 bunky 8–11 (spusti 10)
- ASCII obrázok: Sequential / Parallel / Loop.
- Pipeline sumarizátor → prekladateľ: `output_key="summary"` zapíše do state, `{summary}` v
  inštrukcii ďalšieho agenta číta. **State je rúra**; `{key?}` = voliteľné.

### 4_2 Paralelné vetvy: ParallelAgent · ~5 min · nb05 bunky 12–14 (spusti 13)
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

### 5_1 Callbacky: váš kód pred a po každom kroku agenta · ~5 min · nb07 bunky 8–10, 20 (teória)
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
