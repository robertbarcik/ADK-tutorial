# Stavajte produkčných AI agentov v Pythone s Google ADK: od prvého agenta po hlas, multi-agentov a A2A

*Slovenský popis kurzu pre Skillmea. Výklad vo videách je v slovenčine; slidy, notebooky a učebnica sú v angličtine, tak ako ich stretnete v praxi.*

## Krátky popis

O AI agentoch dnes hovorí každý, ale postaviť a nasadiť skutočného agenta vie málokto. Medzi jedným zavolaním LLM API a agentom, ktorý číta databázu, volá ďalšie služby, pamätá si konverzácie a beží za HTTPS endpointom, je priepasť. Tento kurz vás cez ňu prevedie.

V štrnástich praktických moduloch prejdete od prvého agenta v Pythone k multi-agentovým orchestráciám, hlasovým agentom v reálnom čase a agentom, ktorí sa rozprávajú s cudzími agentmi cez nový protokol A2A. Ku každému konceptu patrí Jupyter notebook, ktorý si spúšťate s vlastným API kľúčom, takže každú myšlienku vyskúšate hneď, ako ju počujete.

Na konci kurzu budete mať za sebou reálnych fungujúcich agentov a budete presne vedieť, ako ich dostať do produkcie.

## Čím je tento kurz iný

**Praktický od prvej minúty.** Každý modul má notebook, ktorý beží odhora nadol. Nepozeráte sa, ako niekto programuje na slide. Kód si spúšťate sami, rozbijete ho, zmeníte a spravíte si ho vlastným.

**Nezávislý od vendora.** Prvá časť beží celá cez OpenRouter, takže desať plných modulov zvládnete s Claude, GPT alebo aj s bezplatným lokálnym modelom, bez toho, aby ste sa dotkli Google Cloudu. Váš kód zostáva prenosný a rozpočet minimálny.

**Stavaný pre produkciu, nie pre demá.** Iné kurzy končia pri chatbote, ktorý odpovie na jednu otázku. Tu ideme celú cestu: pamäť, evaluácia, nasadenie, ochranné mechanizmy, observability a chytáky, ktoré sa ukážu až po nasadení.

**Rýchla cesta pre netrpezlivých.** Štyri starostlivo vybrané moduly vám za zhruba hodinu dajú mentálny model aj najpôsobivejšie demo kurzu. Najrýchlejší spôsob, ako zistiť, či je celý kurz pre vás.

## Čo sa v kurze naučíte

- Stavať produkčných agentov v Pythone s Agent Development Kitom od Googlu.
- Zapojiť štyri druhy nástrojov: obyčajné funkcie v Pythone, REST API cez OpenAPI špecifikácie, MCP servery a špecializovaných sub-agentov.
- Skladať multi-agentové systémy zo Sequential, Parallel a Loop workflow agentov, a rozlišovať medzi odovzdaním práce cez `sub_agents` a konzultáciou cez `AgentTool`.
- Vymeniť poskytovateľa LLM na jednom riadku: ten istý kód beží na Claude, GPT, Gemini, Qwene aj lokálnej Llame cez Ollamu.
- Pridať agentovi pamäť, ktorá prežije reštart servera, aj dlhodobé vybavovanie faktov naprieč konverzáciami.
- Nasadiť agentov ako skutočné HTTP služby: Docker, Cloud Run alebo Vertex AI Agent Engine.
- Testovať agentov poriadne, nie od oka: trajektórie volaní nástrojov, skórovanie odpovedí a prahy, ktoré viete dať do CI.
- Chrániť nebezpečné operácie správne, teda potvrdením v kóde, nie zdvorilou prosbou v prompte, ktorú model môže ignorovať.
- Využiť superschopnosti Gemini: vyhľadávanie s citáciami, cachovanie dlhého kontextu s úsporou až deväťdesiat percent, thinking budgety a hlasové Live API.
- Rozumieť nastupujúcim protokolom MCP a A2A, cez ktoré sa agenti prepájajú naprieč vendormi.

## Obsah kurzu

**Úvod do kurzu** — čo vás čaká a ako z kurzu vyťažiť maximum.

**Časť 1 — Agenti na akomkoľvek LLM**
1. Mentálny model agenta: štyri primitívy Agent, Runner, Event a Session
2. Nástroje: štyri druhy, od funkcií v Pythone po MCP servery
3. Sessions, state, eventy a artefakty
4. Výmena modelu na jednom riadku (LiteLLM)
5. Workflow agenti: Sequential, Parallel, Loop
6. Multi-agent hierarchie
7. Callbacky ako middleware
8. Pamäť: perzistentné sessions a dlhodobé vybavovanie
9. Evaluácia
10. Nasadenie: Docker, Cloud Run, Vertex AI Agent Engine

**Časť 2 — Schopnosti len pre Gemini**
11. Gemini grounding a caching
12. Thinking budgety
13. Live API hlasový agent

**Časť 3 — Agenti sa rozprávajú s agentmi**
14. Protokol A2A

## Čo by ste mali vedieť vopred

Toto je technický kurz. Zíde sa vám:

- Slušná znalosť Pythonu.
- Základná skúsenosť s REST API a príkazovým riadkom. V neskorších moduloch použijeme curl a Docker.
- Aspoň jedno predchádzajúce zavolanie LLM API. Nemusíte byť expert na machine learning, ale kurz predpokladá, že ste si už niekedy skúsili „hello world" proti OpenAI, Anthropicu alebo Gemini.
- Jeden API kľúč: buď OpenRouter (odporúčané, celá prvá časť vás vyjde na pár centov), alebo bezplatný kľúč z Google AI Studio pre druhú časť.

Nepotrebujete GPU ani platený účet na Google Cloude.

## Pre koho je kurz určený

Pre ľudí, ktorí to s agentmi myslia vážne. Nie demo agenti, ale agenti, ktorí sa dostanú pred skutočných používateľov, čítajú skutočné dáta a musia fungovať, aj keď sa nikto nepozerá.

- **Softvéroví inžinieri**, ktorí idú za hranicu jednotlivých LLM volaní a potrebujú framework pre agentov s viackrokovým uvažovaním, nástrojmi a stavom.
- **ML a AI praktici**, ktorí modelom rozumejú, ale potrebujú produkčný spôsob, ako ich prepojiť s nástrojmi, pamäťou, evaluáciou a nasadením.
- **Technickí lídri a architekti**, ktorí sa rozhodujú medzi LangGraph, CrewAI a ADK a chcú porovnávať na základe vlastnej skúsenosti, nie marketingových stránok.
- **Nezávislí vývojári**, ktorí prototypujú agentové produkty s malým rozpočtom. Vendor-neutrálny dizajn drží experimenty lacné a kód prenosný.
- **Každý, kto dnes stavia s LLM** a chce pochopiť, ako do celkového obrazu zapadajú hlasoví agenti, multi-agentová orchestrácia, MCP a A2A.

Ak sa vo vašej blízkej budúcnosti nachádza veta „môj ďalší projekt sú agenti", tento kurz je stavaný pre vás.
