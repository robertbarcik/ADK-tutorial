# M10 — Speaker notes (SK)

---

## Slide 1 — Title

Deployment. Presne to je téma tohto modulu: vezmeme agenta, ktorý beží v notebooku, a spravíme z neho HTTP službu, ktorú viete zavolať odkiaľkoľvek.

Doteraz každý agent, ktorého sme postavili, bežal v notebooku, v `adk web` alebo v testovacom skripte. Tento modul to mení. Agent sa stane FastAPI serverom, server pobeží v kontajneri a kontajner pošlete na platformu, ktorú si sami vyberiete.

---

## Slide 2 — Up to now / This module

Rámovanie na tomto slide dáva celý kurz do perspektívy. Zatiaľ všetci naši agenti bežali lokálne. Práve tu sa to mení a agent sa stáva produktom.

Mechanický rozdiel je menší, než to znie. Kód agenta ostáva rovnaký. Mení sa spôsob, akým ho voláte. Namiesto testovacieho skriptu, ktorý ho volá priamo, ho volá HTTP klient cez FastAPI server, ktorý ADK poskytuje.

---

## Slide 3 — Three paths

Pre deployment máme tri cesty a líšia sa v tom, koľko Googlu chcete mať v hre.

Prvá je `adk deploy cloud_run`, jeden príkaz na Google Cloud Run. Ak už ste na GCP, je to najrýchlejšia možnosť.

Druhá je čistý Docker. Napíšete Dockerfile, zbuildujete image a nasadíte kamkoľvek, kde bežia kontajnery. Google k tomu vôbec nepotrebujete.

Tretia je Vertex AI Agent Engine, spravovaná a názorovo vyhranená cesta. Dostanete toho viac hotového v balení, vrátane vstavaného Memory Bank a Agent Identity. A zároveň je to najhlbší Google lock-in.

Všetky tri cesty produkujú na úrovni agenta to isté. Líšia sa len v tom, kto prevádzkuje kontajner a čo k tomu dostanete.

---

## Slide 4 — Foundation header

Skôr než sa pustíme do jednotlivých ciest, je tu spoločný základ, a tým je štruktúra priečinka, ktorú očakáva každý ADK nástroj.

---

## Slide 5 — The shape every tool expects

Štyri súbory tvoria nasaditeľný layout, ktorý každý ADK nástroj hľadá. Súbor `__init__.py`, ktorý označuje priečinok ako Python balík. Súbor `agent.py`, ktorý exportuje `root_agent`. Súbor `requirements.txt` s pripnutými závislosťami. A voliteľný `.env` na tajné údaje.

Príkazy `adk api_server`, `adk web`, `adk deploy cloud_run` aj `AgentEvaluator.evaluate` hľadajú presne tento tvar. Konvencia nie je tvrdo vynucovaná, ale keď sa od nej odchýlite, znamená to, že si okolo toho dopíšete vlastnú obsluhu. Celú štruktúru vám `adk create` vyskladá jedným príkazom.

---

## Slide 6 — Path 1: adk api_server header

`adk api_server` je spôsob, ako vidieť svojho agenta ako HTTP službu lokálne, ešte predtým, než sa zaviažete akémukoľvek cloudu.

---

## Slide 7 — Start it / Hit it

Naštartovať server je jeden príkaz. Z nadradeného priečinka nad vaším agentským priečinkom spustite `adk api_server .`. Tým sa na localhost:8000 rozbehne FastAPI server, ktorý hosťuje každý agentský priečinok, aký nájde.

Volanie je čistý JSON cez HTTP. Endpoint `/list-apps` vráti hosťovaných agentov, session vytvoríte POSTom na sessions endpoint s ID používateľa a ID session, a správu pošlete POSTom na `/run` so session trojicou a obsahom od používateľa. Žiadna mágia sa tu nekoná. Sú to presne tie isté endpointy, ktoré bude volať váš produkčný klient.

---

### Notebook break — api_server + real HTTP calls

[Prepnite obrazovku na notebook.]

Spustite bunky 7 a 8. Bunka 7 naštartuje `adk api_server` ako proces na pozadí priamo v notebooku a bunka 8 naň potom posiela skutočné HTTP volania: vypíše aplikácie, vytvorí session, pošle správu, pozbiera eventy. Bunka 10 proces po skončení uprace.

Každé volanie, ktoré vidíte, je JSON cez HTTP na FastAPI endpoint. Presne toto by robil produkčný klient, len by mieril na inú URL.

[Prepnite späť na prezentáciu.]

---

## Slide 8 — The production shape

Cloud Run je tá istá FastAPI aplikácia, ktorá beží na infraštruktúre Googlu namiesto vášho notebooku. Vymeníte URL a kód klienta sa nemení.

Ak ste postavili frontend, ktorý sa rozpráva s `http://localhost:8000/run`, a zajtra nasadíte na Cloud Run na `https://my-agent-xyz.run.app`, jediná zmena je jedna URL konštanta. Vytváranie sessions, formát správ aj streamovanie eventov ostávajú identické.

---

## Slide 9 — Vanilla Docker header

Čistý Docker je druhá cesta. Nasadíte na akúkoľvek kontajnerovú platformu, ktorá sa vám páči.

---

## Slide 10 — The Dockerfile — 10 lines

Dockerfile má okolo desať riadkov. Vezmete slim Python base image, nakopírujete requirements, nainštalujete ich, nakopírujete agentský priečinok, nastavíte `PORT` env var a CMD spustí `adk api_server` počúvajúci na všetkých rozhraniach na porte, ktorý dodá cloud.

Žiadny platformový kód špecifický pre ADK tu nie je. Je to len FastAPI aplikácia v kontajneri, a práve to jej umožňuje nasadenie kamkoľvek, kde kontajnery bežia.

---

## Slide 11 — Where you can ship the image

AWS Fargate, Azure Container Apps, fly.io, Kubernetes, alebo váš vlastný server s `docker run`, image beží na všetkých. Hlavné možnosti spolu s príslušnými príkazmi nájdete na slide.

Jednu vlastnosť sa oplatí pomenovať explicitne. Pre ne-Google cloudy neexistuje žiadny deployment postup špecifický pre ADK, je to obyčajné nasadenie kontajnera. FastAPI výstup z ADK beží všade tam, kde beží FastAPI.

---

## Slide 12 — Path 3: adk deploy cloud_run header

Tretia cesta vám dáva deploy na Cloud Run jedným príkazom. Ak už ste na GCP a chcete čo najrýchlejšie dodať, toto je najkratšia cesta.

---

## Slide 13 — The one-liner

Kód ukazuje štyri flagy: projekt, región, meno služby a agentský priečinok. Spustíte ho a pod kapotou ADK vygeneruje Dockerfile, zbuilduje image cez Cloud Build, pushne ho do Artifact Registry a nasadí Cloud Run službu. Výstupom je URL.

Na strane plusov je to rýchle, má rozumné defaulty pre agentské workloady a prirodzene sa integruje s Cloud Trace a Cloud Logging. Na strane mínusov je to len Google Cloud, máte menej kontroly než pri vlastnom kontajneri a platíte prirážku za Cloud Run runtime.

Je to dobrý default, keď ste na GCP a chcete rýchlo dodať, a zlý default, keď vám záleží na detailoch.

---

## Slide 14 — Vertex AI Agent Engine header

Štvrtá a posledná cesta je len na zmienku: Vertex AI Agent Engine. Vy nasadíte, Google prevádzkuje.

---

## Slide 15 — What Agent Engine adds

Agent Engine pridáva oproti Cloud Runu štyri veci, na ktorých naozaj záleží.

Po prvé spravované sessions. Nemusíte prevádzkovať žiadnu samostatnú databázu, o stav sessions sa stará Google.

Po druhé Memory Bank. Ide o LLM-destilovanú dlhodobú pamäť s auto-konsolidáciou a auto-decay, čo je skutočný upgrade oproti ručne poskladanej `InMemoryMemoryService`.

Po tretie Agent Identity. Každý agent dostane vlastný IAM principal s certificate-bound credentials, teda prihlasovacími údajmi viazanými na certifikát. Ukradnuté credentials sa mimo dôveryhodného runtime nedajú znova prehrať. Ide o najsilnejší enterprise-governance primitív, aký Google v agentskom stacku ponúka.

Po štvrté vstavaná evaluácia a observability, ktorá sa integruje s Gen AI Evaluation Service od Googlu.

---

## Slide 16 — Pricing picture

Cenotvorba sa rozpadá na štyri položky a najdôležitejšia je tá prvá: runtime stojí rovnako ako Cloud Run. Na compute vrstve nie je žiadna prirážka.

Náklady podľa použitia sú sessions za 25 centov za tisíc eventov a Memory Bank za 25 centov za tisíc uložených spomienok mesačne, pričom retrieval stojí 50 centov za tisíc a prvá tisícka je zadarmo.

Agent Engine si vyberte vtedy, keď chcete Memory Bank a Agent Identity bez toho, aby ste si ich stavali sami. Cloud Run si vyberte, keď chcete prenositeľnosť. A nevyberte si ani jedno, ak nie ste na Google Cloude.

---

## Slide 17 — Plugins header

Ešte jeden koncept, skôr než uzavrieme, a tým sú pluginy. Dopĺňajú vzor callbackov, ktorý poznáte zo skoršej časti kurzu, a sú tým správnym nástrojom pre produkčné prierezové záležitosti.

---

## Slide 18 — Callbacks vs Plugins

Obidva mechanizmy tu vidíte vedľa seba. Callbacky sú per-agent, pripájajú sa na `LlmAgent` a hodia sa na ochranné funkcie špecifické pre jedného agenta, ako je blocklist alebo PII redakcia na jednom konkrétnom špecialistovi. Pluginy patria celému Runneru, pripájajú sa na `Runner` a platia pre každého agenta, ktorého spravuje.

Práve tento rozdiel v rozsahu robí z pluginov správny nástroj pre organizačné záležitosti. Audit logging, rate limity pre jednotlivých používateľov, presadzovanie tokenového rozpočtu alebo PII redakcia naprieč organizáciou musia platiť konzistentne v celej aplikácii, nie len na jednom agentovi.

Základné pravidlo je rovnaké ako pri callbackoch. Logika viazaná na jedného agenta ostáva v callbackoch, celoaplikačná policy ide do pluginov. V produkcii budete mať zvyčajne obidvoje. Pluginy sú v ADK novšie a Google ich pre nový kód odporúča namiesto celoaplikačných callbackov.

---

## Slide 19 — Production readiness checklist

Sedem oblastí sa oplatí pomenovať explicitne, nad rámec otázky, či agent vôbec funguje.

Persistencia a tajné údaje sú základ: `DatabaseSessionService` nad managed Postgresom a kľúče mimo kontajnera. Potom nasleduje vrstva špecifická pre ADK, teda callbacky pre bezpečnostné mechanizmy, pluginy pre observability a eval v CI na každom pull requeste. Nad tým trace backend, aby ste videli, čo agent v produkcii robí. A napokon autentifikácia, pretože ADK žiadnu auth nedodáva, takže potrebujete API gateway alebo authenticated subnet.

Nič z toho nie je špecifické pre ADK. Je to to, čo potrebuje každá služba v Pythone. Oplatí sa to však pomenovať práve tu, pretože demá tieto veci neobsahujú.

---

## Slide 20 — Part 1 wrap

Týmto uzatvárame prvú časť. Prešli sme cestu od otázky, čo je agent, až po otázku, ako ho dodať do sveta.

---

## Slide 21 — What you can build now

Prvá časť pokryla veľký kus cesty. Postavili ste agentov s nástrojmi štyroch druhov a perzistentný stav so scope prefixami. Videli ste vendor-neutrálnu výmenu modelov, kde ten istý agent beží na Claude, GPT, Qwene alebo Geminim, aj workflow kompozície a LLM-riadený routing. Cez callbacky ste pridali bezpečnostné mechanizmy, cache a PII redakciu, cez MemoryService dlhodobú pamäť. K tomu automatizovaná evaluácia s trajectory testovaním a LLM-as-judge, a napokon deployment ako HTTP služba, ktorá beží kamkoľvek, kam siahnu kontajnery.

To všetko na ktoromkoľvek modeli chcete, pretože LiteLLM spravil z modelu konfiguráciu, nie závislosť.

---

## Slide 22 — Up next / Part 2

Druhá časť štartuje v nasledujúcom module. Posúvame sa od vendor-neutrálneho ku Gemini-špecifickému: Google Search grounding s citáciami priamo v odpovedi, context caching, ktorý znižuje tokenové náklady pri opakovaných promptoch, a neskôr v druhej časti thinking budgety a hlasový agent cez Live API.

Prepnite si `.env` tak, aby obsahoval `GOOGLE_API_KEY`. Free tier na aistudio.google.com na Gemini moduly stačí. Vidíme sa v druhej časti.
