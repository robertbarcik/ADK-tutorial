# M14 — Speaker notes (SK)

---

## Slide 1 — Title

Tento modul patrí A2A protokolu. Nie je to striktne vzaté súčasť ADK, ale je to vec, ktorá ADK prežije. MCP a A2A spolu prežijú akýkoľvek konkrétny model, akýkoľvek konkrétny framework aj akéhokoľvek konkrétneho poskytovateľa. Celý kurz ste stavali agentov, ktorí volajú nástroje. Teraz pôjde o to, ako títo agenti volajú iných agentov, naprieč procesmi, naprieč organizáciami, a pokojne napísaných v úplne odlišných frameworkoch.

---

## Slide 2 — MCP vs A2A framing

Rozdelenie medzi MCP a A2A je správny rámec pre celú túto časť. MCP je protokol pre agentov volajúcich nástroje. A2A je protokol pre agentov volajúcich iných agentov. Oba dnes spadajú pod správu Linux Foundation. Oba majú viac-menej stabilné špecifikácie s oficiálnymi SDK. Toto rozdelenie je najtrvácnejšia vec, ktorú si odtiaľto odnesiete.

---

## Slide 3 — The journey

Prejdime si vývoj v rýchlosti. Google spustil A2A na konferencii Cloud Next v apríli 2025 a v júni ho daroval Linux Foundation. V auguste sa doň zlúčil konkurenčný ACP protokol od IBM. V decembri bol do novej Agentic AI Foundation darovaný aj MCP, takže A2A a MCP sú teraz spolu pod cross-vendor správou. Začiatkom roka 2026 vyšla verzia A2A 1.0 s piatimi oficiálnymi jazykovými SDK. K dnešnému dňu sa prihlásilo zhruba stopäťdesiat zakladajúcich členských organizácií, hoci integrácia v ADK je stále označená ako experimentálna.

Protokol je skutočný. Ekosystém ho ešte len dobieha.

---

## Slide 4 — Four nouns header

Celý A2A protokol sa dá zredukovať na štyri podstatné mená. Zapamätajte si ich, pretože všetko ostatné okolo A2A je už len komentár navrch.

---

## Slide 5 — The four nouns

Poďme si tie štyri podstatné mená prejsť jedno po druhom.

Prvý je Agent Card, čiže JSON descriptor agenta servírovaný na well-known URL. Nesie identitu agenta, jeho capabilities, skills a autentifikačné schémy. Predstavte si ho ako OpenAPI spec, ale pre agenta.

Druhý je Task, stavová jednotka práce vlastnená serverom. Má svoje ID, status, ktorý sa posúva cez hodnoty working, input-required a completed, históriu správ a artifakty. Podobá sa na GitHub Issue, pretože je trvalý, sledovateľný a dlho bežiaci.

Tretí je Message, teda jeden ťah v rámci tasku. Prichádza od používateľa alebo od agenta a skladá sa z typed parts, teda častí typu text, file alebo data. V podstate je to chatová správa.

Štvrtý je Artifact, trvalý výstup tasku. Môžu to byť reporty, obrázky alebo štruktúrovaný JSON. Od správ sa líši tým, že je to deliverable, nie konverzácia.

Jedno rozlíšenie sa oplatí ustrážiť. Skills sú sémantický zoznam vecí, ktoré agent vie robiť, čiže menu. Capabilities sú protokolové feature-flagy pre streaming, push notifications a history replay, čiže či kuchyňa robí aj rozvoz. Sú to rôzne koncepty a rôzne polia v Agent Carde.

---

## Slide 6 — Where A2A fits

Architektonický obraz je vrstvený vzor. Orchestrátor agent postavený v ADK používa A2A na to, aby sa dostal k špecialistom, ktorí môžu byť postavení v LangGraphu, v CrewAI, alebo to môže byť jednoducho ďalší ADK agent v inom procese či v inej organizácii. Každý špecialista zase používa MCP na volanie nástrojov napísaných v Go, v Ruste, v TypeScripte alebo v čomkoľvek inom.

A2A slúži na komunikáciu medzi agentmi naprieč frameworkmi a MCP na volanie nástrojov naprieč jazykmi. Presne takto vyzerá moderné multi-agent nasadenie.

---

### Notebook break — Expose and consume

[Prepnite obrazovku na notebook.]

Bunky osem až štrnásť. Prvá polovica vystaví ADK agenta ako A2A službu, teda `to_a2a(agent)`, uvicorn server a živý endpoint. Potom si z toho endpointu stiahneme Agent Card a pozrieme sa, čo ADK automaticky vygenerovalo. Druhá polovica službu konzumuje cez `RemoteA2aAgent` namierený na URL Agent Cardu, vložený do Runnera a volaný presne ako lokálny agent.

Spustite obe polovice. Kľúčová vec na sledovanie je event stream z konzumujúcej strany, pretože ukazuje tool cally bežiace na vzdialenom serveri, nie lokálne.

[Prepnite späť na prezentáciu.]

---

## Slide 7 — Expose — to_a2a()

Serverová strana sú tri riadky. Funkcia `to_a2a(agent)` zabalí ľubovoľného ADK agenta do Starlette aplikácie, ktorá hovorí protokolom A2A. Aplikáciu podáte uvicornu spolu s hostom a portom a máte agenta ako HTTP službu. Agent Card, JSON-RPC endpoint aj task lifecycle, teda životný cyklus tasku, sú zapojené automaticky.

V samotnom agentovi pritom nie je žiadny A2A-špecifický kód. Funguje akýkoľvek `LlmAgent`, ktorého ste už postavili.

---

## Slide 8 — Consume — RemoteA2aAgent

Konzumujúca strana zrkadlí tú serverovú. `RemoteA2aAgent` vezme URL Agent Cardu, stiahne si ho a vystaví vzdialeného agenta ako lokálneho ADK agenta. Môžete ho vložiť do Runnera alebo do zoznamu `sub_agents` iného agenta. Z pohľadu konzumujúcej strany je tvar identický s lokálnym agentom.

Dôležité sú dva argumenty. Prvý je `name`, čiže ako ho volá lokálna strana, a druhý je `agent_card`, čiže URL, na ktorej karta žije. K tomu ešte `use_legacy=False`, ktorému sa venuje ďalší slide.

---

## Slide 9 — The event stream

Event stream z volania vzdialeného agenta má štyri kroky: správu používateľa, tool call vykonaný na vzdialenom serveri, tool response a finálny text.

Z pohľadu vášho kódu je to rovnaký tvar eventov, ako keby tú istú prácu robil lokálny agent. Z pohľadu siete prebehlo HTTP volanie. A2A tieto dva svety premosťuje bez toho, aby volajúcemu ten rozdiel ukazoval.

---

## Slide 10 — use_legacy=False

`RemoteA2aAgent(use_legacy=False)` je ten jeden argument, ktorý sa oplatí zapamätať.

Východisková hodnota je `True` a legacy executor má tri známe chyby: duplikáciu user správ, vzdialené výstupy nesprávne klasifikované ako myšlienky a stratu sub-agent výstupu pri vnorených vzdialených agentoch. Nastavenie `use_legacy=False` vymení executor za taký, ktorý všetky tri opravuje.

Nový kód by mal `False` posielať vždy explicitne. Východisková hodnota sa v niektorom budúcom vydaní ADK pravdepodobne preklopí, ale kým sa tak nestane, píšte ten argument zakaždým.

---

## Slide 11 — Agent Card structure

Výstup Agent Cardu z notebooku ukazuje, čo ADK generuje automaticky. Je tam meno a popis. Verzia protokolu je 0.3.0, čo je línia a2a-sdk, na ktorej ADK závisí. Preferovaný transport je vo východiskovom stave JSON-RPC. Capabilities hovoria, ktoré protokolové featury agent podporuje. Nasledujú východiskové vstupné a výstupné módy. A napokon sú tam Skills, čiže zoznam vecí, ktoré agent vie robiť, aj s popismi a príkladmi.

ADK to celé odvodí z mena, popisu a nástrojov vášho agenta. Pre produkčných agentov by ste kartu písali ručne, doplnili do každého skillu realistické príklady, deklarovali capabilities explicitne a kartu podpísali cez `AgentCardSignature`, čím získa kryptografickú identitu. Pre kurzové demo automaticky vygenerovaná verzia stačí.

---

## Slide 12 — Maturity: honest read

Nasleduje úprimné zhodnotenie zrelosti A2A v dvoch poloviciach.

Čo je skutočné: A2A 1.0 je stabilná špecifikácia, správa pod Linux Foundation funguje, existuje päť oficiálnych jazykových SDK a v cross-vendor protokolovom orgáne sedia zástupcovia AWS, Cisca, Googlu, IBM, Microsoftu, Salesforce, SAP a ServiceNow.

Čo je tenké: ekosystém. Väčšina zo zhruba stopäťdesiatich zakladajúcich organizácií sú signatári, nie firmy s bežiacimi produkčnými integráciami. Integrácia A2A v ADK je stále označená ako `@a2a_experimental`. A medziorganizačná vrstva dôvery, teda podpísané karty, registre a federovaná identita, je v špecifikácii explicitne označená ako budúce skúmanie.

Praktický záver znie takto. A2A je architektúra, ktorú sa oplatí pochopiť už teraz, ale nie je to infraštruktúra, na ktorú by ste tento rok stavili produkciu. Pri novej práci proti nej pokojne stavajte, existujúce produkčné workloady zatiaľ nemigrujte. Koncom roka 2026 by sa to malo otočiť, keď ekosystém dozreje.

---

## Slide 13 — Six gotchas

Ostáva šesť ostrých hrán, ktoré stojí za to pomenovať.

Prvá je premenovanie cesty. Vo verzii 0.2 bol Agent Card na `/.well-known/agent.json`. Vo verzii 0.3, ktorou hovorí ADK, sa presunul na `/.well-known/agent-card.json`. Kód zo starších blogových článkov má nesprávnu cestu.

Druhá je legacy executor, o ktorom sme už hovorili. Vždy nastavte `use_legacy=False`.

Tretia je version pin. ADK až po aktuálne vydanie 2.4 vyžaduje a2a-sdk vo verzii 0.3. A2A 1.0 vyžaduje a2a-sdk 1.0, ktorým ADK zatiaľ nehovorí. Verzie nemiešajte.

Štvrtá je nedošpecifikovaná discovery, teda objavovanie agentov. Cesta `.well-known` je stabilná, ale registre sú budúca práca. Nespoliehajte sa na registry featury.

Piata je Agent Engine, ktorý sa odchyľuje od východiskového správania špecifikácie. Googlov vlastný Agent Engine servíruje Agent Card na `/v1/card` za autentifikáciou, nie na `.well-known`. A2A klienti tretích strán, ktorí očakávajú štandardnú cestu, proti Agent Enginu zlyhajú. Ak tam nasadzujete, počítajte s tým.

Šiesta je nevyriešená dôvera medzi organizáciami. Podpísané karty sú vo verzii 1.0 ako SHOULD, nie MUST, a neexistuje žiadna centrálna root-of-trust CA pre agentov. Každá A2A odpoveď spoza hraníc vašej organizácie je pre váš planner nedôveryhodný vstup. Naplno tu platí lethal trifecta Simona Willisona, čiže smrtiace trio: súkromné dáta plus nedôveryhodný obsah plus externá komunikácia. S výstupom každého vzdialeného agenta zaobchádzajte, ako keby ho napísal zlomyseľný používateľ.

---

## Slide 14 — Carry forward

Odneste si štyri podstatné mená, dve protokolové roly, teda A2A pre komunikáciu medzi agentmi a MCP pre volanie nástrojov, a šesť ostrých hrán. Protokoly prežijú frameworky, a práve preto je ich pochopenie trvácna investícia.

---

## Slide 15 — Course finale header

A tým sa dostávame k finále kurzu. Prešli sme cestu od otázky, čo je to vlastne agent, až po agentov, ktorí sa rozprávajú s inými agentmi naprieč organizáciami.

---

## Slide 16 — What you can build

Zrekapitulujme si, čo kurz pokryl. Prvá časť bola vendor-agnostické ADK: štyri primitívy, štyri druhy nástrojov, state so scope prefixmi, výmena modelu na jeden riadok naprieč piatimi poskytovateľmi, workflow agenti Sequential, Parallel a Loop, multi-agent kompozícia cez sub_agents a AgentTool, callbacky ako middleware, perzistentná pamäť, automatizovaná evaluácia s trajectory testovaním a nasadená HTTP služba.

Druhá časť ukázala, čo odomyká Gemini: grounding cez Google Search so skutočnými citáciami, dlhý kontext s cachovaním a deväťdesiatpercentnou úsporou nákladov, thinking budgety, ktoré vymieňajú latenciu za kvalitu uvažovania, a Live API pre hlasových agentov.

Odbočkou bol A2A protokol, teda agent-to-agent komunikácia naprieč frameworkmi postavená na otvorenom cross-vendor štandarde.

Keď to celé poskladáte, viete stavať skutočný agentový softvér. Bude stavový, bude si pamätať, poskladáte ho naprieč frameworkmi, nasadíte ho, zmeriate ho evaluáciou, zvládne viac modalít a bude mať produkčný tvar.

---

## Slide 17 — Thanks

Ďakujem, že ste kurz absolvovali. Teraz choďte a niečo postavte, pretože to je jediný spôsob, ako sa to naozaj naučiť. Môže to byť hlasový bot zákazníckej podpory, výskumný orchestrátor alebo osobný asistent, ktorý prežije reštarty a pamätá si vás celé týždne. Kurz vás naučil mechaniku a stavanie vás naučí zvyšok. Bolo mi potešením vás kurzom sprevádzať a držím vám palce.
