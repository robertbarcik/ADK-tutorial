# M02 — Speaker notes (SK)

---

## Slide 1 — Title

Vitajte späť. Tento modul je o nástrojoch, teda o slovesách agenta, a práve tu sa agenti stávajú užitočnými. Na konci budete mať postavený jeden nástroj z každého zo štyroch rôznych druhov, osvojíte si mentálny model, ktorý všetky štyri spája, naučíte sa jedno dizajnové pravidlo o tom, že s rizikom treba pri každom nástroji zaobchádzať inak, a prejdeme si krátku vsuvku o bezpečnosti. Poďme na to.

---

## Slide 2 — Without / with tools

Bez nástrojov je agent len chatbot. Vie písať text, odpovedať na otázky, viesť konverzáciu, a tým sa jeho možnosti končia. S nástrojmi sa agent stáva softvérom. Vie siahnuť von, vyhľadať dáta, meniť stav, spúšťať kód, rozprávať sa s inými agentmi, skrátka čokoľvek, čo dokážete schovať za funkciu. To je rozdiel medzi niečím, čo rozpráva, a niečím, čo koná. Zvyšok modulu je o tom, ako to „konanie“ zapojiť bezpečne.

---

## Slide 3 — The tool mental model

Poďme si prejsť, čo sa naozaj deje, keď agent volá nástroj. Keď model usúdi, že nástroj treba, vyšle štruktúrované volanie, teda meno nástroja plus argumenty, ktoré mu chce odovzdať. ADK to volanie zachytí, nájde kód, ktorý za ním stojí, spustí ho, zabalí návratovú hodnotu a podá ju späť modelu ako tool-response event. Z toho potom model vyrobí finálnu odpoveď na základe toho, čo nástroj vrátil.

Tento tvar je rovnaký bez ohľadu na to, aký druh nástroja zapájate. Medzi štyrmi druhmi sa menia len dve veci, a to odkiaľ pochádza schéma a kde beží kód. Naozaj nič viac sa nemení.

---

## Slide 4 — Four flavors differ only in two things

Tu je tabuľka, ktorú by ste si mali odniesť v hlave, teda štyri druhy nástrojov.

Prvý je FunctionTool. Schéma pochádza z docstringu a type hintov vašej Python funkcie a kód žije vo vašom vlastnom Python súbore. S týmto druhom sme už pracovali, je to obyčajná funkcia v Pythone.

Druhý je OpenAPIToolset. Schéma pochádza z OpenAPI špecifikácie a kód žije za vzdialeným HTTP API niekde na sieti.

Tretí je McpToolset. Schéma pochádza z list-tools odpovede MCP servera a kód žije v samostatnom procese, často napísanom v inom jazyku.

A napokon AgentTool. Schéma pochádza z mena a popisu iného agenta a kódom je ten druhý agent samotný.

Kľúčové je, že pre model je to stále tá istá abstrakcia. Model na úrovni schémy naozaj nedokáže tieto štyri od seba rozlíšiť. Dnes si postavíme jeden z každého.

---

## Slide 5 — Flavor 1: FunctionTool

Začnime prvým druhom. FunctionTool sú jednoducho obyčajné Python funkcie zapojené do agenta. Nemusíte písať samostatnú schému ani žiadny konfiguračný súbor. ADK sa pozrie na samotnú funkciu, konkrétne na docstring a type hinty, a všetko, čo LLM potrebuje, si odvodí z nich. Ako presne sa to deje, rozoberá ďalší slide.

---

## Slide 6 — The docstring is the schema

Jadrová myšlienka FunctionTool znie takto: docstring je schéma.

Čo to znamená v praxi? Docstring je blok textu hneď pod definíciou funkcie v Pythone, zabalený v trojitých úvodzovkách, ktorý popisuje, čo funkcia robí a na čo slúžia jej argumenty. Normálne je to poznámka pre ľudských čitateľov. V ADK sa ale docstring stáva hlavným zdrojom JSON popisu, ktorý sa posiela LLM. Tento JSON popis voláme schéma a hovorí modelu meno nástroja, aké argumenty berie, čo ktorý argument znamená a aký tvar bude mať návratová hodnota.

Z toho plynú tri praktické dôsledky. Po prvé, docstring píšte pre model, nie pre človeka, ktorý vám robí code review. Model sa vás nemá ako spýtať, čo parameter znamená, takže každý argument potrebuje jednoznačný popis napísaný pre LLM.

Po druhé, type hinty sú nosné. Chýbajúci type hint v schéme potichu degraduje na string, takže funkcie nástrojov vždy typujte.

A po tretie, vracajte JSON-serializovateľný slovník alebo string. Nie vlastnú Python triedu a nie NumPy pole. Návratová hodnota sa posiela modelu doslovne ako tool-response event, čo znamená, že to musí byť niečo, čo JSON vie reprezentovať.

---

## Slide 7 — A FunctionTool with a rich docstring

Na slide máme funkciu `get_weather`. Berie názov mesta a voliteľný argument `units` a vyhľadá dnešné počasie pre dané mesto. Ťažkú prácu odvádza docstring vo vnútri funkcie. Vysvetľuje, čo funkcia robí, pomenúva každý argument a hovorí modelu, kedy ktorý použiť.

Presne takto vyzerá bohatý docstring napísaný pre model. Prejdime si, ako sa každá jeho časť premietne do schémy, ktorú LLM uvidí.

Blok Args v docstringu sa stane popismi parametrov, ktoré model číta. Type hint `city: str` sa stane `"type": "string"` v schéme. A pythonovská východisková hodnota `units = "celsius"` sa pre tento argument premietne do `"required": false`, čiže model ho smie vynechať.

Za zmienku stojí jedna drobná dizajnová vec. Modelu v docstringu explicitne hovorím, kedy použiť fahrenheit, a to vetou „only if the user explicitly asks for it“. Bez tejto konkrétnej vety by model len hádal a jednotky by ste mali naprieč volaniami nekonzistentné.

---

### Notebook break — FunctionTool in action

[Prepnite obrazovku na notebook.]

Tu je tá istá funkcia `get_weather`, ktorú sme práve videli, zapojená do fungujúceho weather agenta. Pošlem otázku, ktorá precvičí voliteľný argument: „What's the weather in Munich? Reply in Fahrenheit.“ [Spustite bunku.] Sledujte argumenty tool callu v prúde eventov. Model zvolil `units='fahrenheit'`, pretože docstring mu povedal, kedy ho zvoliť. Nástroj vráti číslo a model ho sformátuje do anglickej vety pre používateľa. Bez tej jednej vety v docstringu by model tipol celsius a používateľ by bol zmätený.

[Prepnite späť na prezentáciu.]

---

## Slide 8 — Flavor 2: OpenAPIToolset

Prejdime na druhý druh, OpenAPIToolset. Motivácia je tu iná ako pri FunctionTool. Pri FunctionTool píšete Python kód sami. Čo ale ak je vec, ktorú agent potrebuje volať, REST API, ktoré už existuje, aj so špecifikáciou? Nechcete ručne písať wrapper pre každý endpoint. Presne na to slúži OpenAPIToolset.

---

## Slide 9 — When your target is a REST API with a spec

Keď je cieľ, ktorý chcete volať, REST API s hotovou OpenAPI špecifikáciou, nechcete písať FunctionTool pre každý endpoint ručne. Namiesto toho podáte ADK špecifikáciu a dostanete N nástrojov automaticky.

Skúsme to na reálnom príklade. Predstavte si, že pracujete v online obchode. Vaša e-commerce platforma už má REST API s OpenAPI špecifikáciou, používa ju webový frontend, mobilná aplikácia a pár interných dashboardov. Endpointy ako `getOrder`, `cancelOrder`, `listProducts`, `updateInventory`. Teraz chcete postaviť agenta pre zákaznícku podporu, ktorý zvládne otázky ako „where is my order?“. Bez OpenAPIToolset by ste písali Python wrapper pre každý endpoint ručne, jeden pre `getOrder`, jeden pre `cancelOrder`, jeden pre `listProducts`. S OpenAPIToolset nasmerujete ADK na tú istú špecifikáciu, ktorú už používa frontend, a agent má zrazu každý endpoint dostupný ako nástroj, bez ďalšieho kódu.

O jednej zvláštnosti sa oplatí vedieť. ADK prevádza operation ID na snake-case. Takže ak vaša špecifikácia hovorí `operationId: getLatestRate`, nástroj, ktorý model naozaj vidí, sa volá `get_latest_rate`. Ak volanie neprichádza a ste si istí, že inštrukcia je správna, skontrolujte, či ADK nástroj nepremenoval.

---

## Slide 10 — Frankfurter currency API: three lines to integrate

Zapojenie OpenAPIToolset do agenta naozaj zaberie tri riadky a všetky tri vidíte na slide. Vezmeme OpenAPI špecifikáciu, ktorá môže byť Python slovník, JSON string alebo YAML string, a podáme ju do `OpenAPIToolset`. Výsledný toolset potom ide do zoznamu `tools=` agenta. A to je celé. Agent má teraz každý endpoint zo špecifikácie dostupný ako nástroj.

V našom deme používame bezplatné verejné API menom Frankfurter. Vracia menové kurzy, nevyžaduje žiadnu autentifikáciu a vystavuje jediný endpoint na načítanie aktuálneho kurzu. Vďaka tomu je to čistý učebný príklad. OpenAPI špecifikácia, ktorú do ADK podávame, je krátka, jediný endpoint popísaný na približne dvadsiatich riadkoch YAMLu. Náš agent tak skončí s presne jedným nástrojom, `get_latest_rate`.

V reálnom produkčnom nasadení by vaša špecifikácia bola oveľa väčšia, pokojne desiatky či stovky endpointov. Každý z nich by sa automaticky stal nástrojom, ktorý agent vie zavolať, a nemuseli by ste písať žiadny lepiaci kód pre jednotlivé endpointy. To je celá ponuka OpenAPIToolset.

---

### Notebook break — OpenAPIToolset against Frankfurter

[Prepnite obrazovku na notebook.]

Tu máme Frankfurter špecifikáciu zapojenú do `OpenAPIToolset` a výsledný toolset odovzdaný agentovi. Spýtam sa: „What's the exchange rate from Swiss francs to Japanese yen?“ [Spustite bunku.] Pozrite na prúd eventov. Model zavolal automaticky vygenerovaný nástroj `get_latest_rate` s argumentmi `base='CHF'` a `symbols='JPY'`. Tool response je surové JSON telo, ktoré Frankfurter vrátil, úplne nezmenené. Model potom prečíta pole `rates.JPY` a vyrobí finálnu odpoveď. Všimnite si, že ADK výstup API vôbec netransformovalo. Len ho prepustilo ďalej, vďaka čomu je API kontrakt transparentný a ľahko sa debuguje.

[Prepnite späť na prezentáciu.]

---

## Slide 11 — Flavor 3: McpToolset

Nasleduje tretí druh, McpToolset. Toto je druh, ktorý nechá vášho agenta rozprávať sa s úplne samostatným tool serverom, často napísaným v inom jazyku, často bežiacim ako iný proces a často držiacim vlastný stav, napríklad databázové pripojenie alebo API credentials. Rozhranie medzi agentom a tým serverom je štandardizované protokolom menom MCP, ktorý stretneme na ďalšom slide.

---

## Slide 12 — MCP in one paragraph

MCP znamená Model Context Protocol. Je to štandard od Anthropicu na vystavovanie nástrojov agentom, v decembri 2025 darovaný Linux Foundation, a dnes je to de facto štandard komunikácie medzi agentmi a nástrojmi naprieč celým odvetvím. Anthropic, Google, OpenAI, Microsoft aj open-source svet, všetci ho podporujú.

MCP server je v podstate samostatný proces, ku ktorému sa váš agent pripojí cez stdio, HTTP alebo Server-Sent Events, a potom používa nástroje servera, akoby boli lokálne.

A tu je dôvod, prečo na MCP naozaj záleží. Server môže byť napísaný v akomkoľvek jazyku, v TypeScripte, v Go, v Ruste, v čom len chcete. Môže bežať na akomkoľvek stroji. A môže vlastniť akýkoľvek stav, napríklad databázové pripojenia, API credentials alebo cache. Agent o ničom z toho nemusí vedieť. Jednoducho hovorí protokolom a nástroje sa objavia.

---

## Slide 13 — Connect to an existing MCP server

Pripojenie k existujúcemu MCP serveru zaberie len pár riadkov kódu, ktoré vidíte na slide. Vytvoríme `McpToolset`, dáme mu parametre pripojenia, ktoré hovoria, ako sa k serveru dostať, a podáme ho do zoznamu `tools=` agenta. Zvyšok spraví ADK.

Rozbaľme si, čo sa deje pod povrchom. Parametre pripojenia popisujú, ako sa dostať k MCP serveru. V tomto prípade cez stdio, čo znamená, že ADK spustí server ako subprocess a bude s ním komunikovať cez štandardný vstup a výstup. Argumenty hovoria, ktorý Python interpreter spustiť a ktorý súbor so skriptom naštartovať.

Toto repo prináša tri hotové MCP servery v priečinku `mcp_servers/`, jeden pre tickety, jeden pre znalostnú bázu a jeden pre monitoring systému. Tu používame ticketový server. Interne vystavuje päť nástrojov, a výsledkom je, že v agentovi sa objaví päť nástrojov bez akéhokoľvek ďalšieho kódu.

---

### Notebook break — McpToolset against the ticket server

[Prepnite obrazovku na notebook.]

Tu ADK spustí ticketový MCP server ako subprocess a automaticky si vypýta zoznam jeho nástrojov. Agent má teraz k dispozícii päť nástrojov bez toho, aby sme čo i len jeden napísali. Spýtam sa: „Find any open tickets about WiFi.“ [Spustite bunku.] Sledujte prúd eventov. Model zavolal `search_tickets`, ktorý prišiel z MCP servera, nie z Python kódu v tomto súbore. Odpoveďou je payload servera zabalený v MCP content obálke. Model z neho vytiahne detaily ticketu a odpovie po anglicky. A celý čas žije ticketová databáza vo vnútri subprocesu, kam agent priamo nevidí.

[Prepnite späť na prezentáciu.]

---

## Slide 14 — Flavor 4: AgentTool

A posledný druh je AgentTool. Zo všetkých štyroch je najviac reflexívny. Pri AgentTool je vec, ktorú váš agent volá, iný agent zabalený tak, aby vyzeral ako nástroj. Hodí sa, keď máte špecialistického agenta, povedzme prekladateľa alebo code reviewera, ktorého chcete zapojiť do väčšieho workflow bez toho, aby prevzal konverzáciu.

---

## Slide 15 — The consultant pattern

Tento štvrtý druh má konceptuálnu jemnosť, ktorú sa oplatí pochopiť správne. ADK má v skutočnosti dva spôsoby, ako vložiť jedného agenta do druhého, AgentTool a sub_agents. Nie sú zameniteľné.

AgentTool je consultant pattern, teda vzor konzultanta. Rodič volá špecialistu ako funkciu. Rodič zostáva pri kormidle, dieťa odpovie a riadenie sa automaticky vráti rodičovi.

sub_agents je transfer pattern, vzor preposlania. Rodič odovzdá konverzáciu úplne. Dieťa potom konverzáciu vlastní, či už na jeden ťah alebo na dvadsať, kým sa samo nerozhodne preposlať ju späť.

Praktické pravidlo znie takto. AgentTool použite, keď má dieťa čistý vstupno-výstupný kontrakt, a sub_agents, keď má dieťa viesť dialóg. K tomuto porovnaniu sa podrobne vrátime neskôr v kurze. Dnes sa sústreďte na vzor konzultanta.

---

## Slide 16 — A translator, called like a function

Tu na slide máme dvoch agentov. Prvý je `translator`, špecialista, ktorého jedinou úlohou je prekladať z angličtiny do slovenčiny. Druhý je `orchestrator`, rodičovský agent, ktorý sa rozpráva s používateľom. Namiesto toho, aby sme prekladateľa vložili do `sub_agents` a odovzdali mu konverzáciu, zabalíme ho do `AgentTool` a podáme orchestrátorovi, akoby to bol len ďalší nástroj v jeho zozname `tools=`.

Model orchestrátora teraz vidí `translator` vo svojom zozname nástrojov, s popisom prekladateľa ako popisom nástroja. Keď používateľ požiada o preklad, orchestrátor zavolá prekladateľa, dostane preklad späť a zapracuje ho do odpovede. Orchestrátor má celý čas veci pod kontrolou a prácu oboch agentov vidíte v jednom prúde eventov.

---

### Notebook break — AgentTool with the translator

[Prepnite obrazovku na notebook.]

Tu je orchestrátor s prekladateľom zabaleným ako `AgentTool`. Pošlem požiadavku: „Translate 'good morning' to Slovak.“ [Spustite bunku.] Sledujte, čo sa deje v prúde eventov. Orchestrátor zavolá nástroj `translator`, čo je samo o sebe LLM volanie bežiace ako samostatný agent. Prekladateľ vyprodukuje „dobré ráno“ a táto odpoveď sa vráti ako tool-response event. Orchestrátor potom napíše finálnu odpoveď používateľovi. Dve volania modelu v jednej stope eventov, obe viditeľné, obe kontrolovateľné, a rodič nikdy nestratil kontrolu nad konverzáciou.

[Prepnite späť na prezentáciu.]

---

## Slide 17 — Interlude: Risk-based tool design

Je čas na krátku vsuvku o rizikovom dizajne nástrojov. Ide o jeden z desiatich vzorov z publikácie Agentic Design Patterns a tá myšlienka je dosť dôležitá na to, aby som prehliadku druhov na chvíľu prerušil a nechal vás nad ňou porozmýšľať, kým budeme pokračovať.

---

## Slide 18 — Categorize tools by blast radius

Nie všetky nástroje sú si rovné. Nástroj, ktorý číta ticket, jednoducho nie je v rovnakej kategórii ako nástroj, ktorý maže databázu. Rozdiel medzi nimi je blast radius, teda rozsah škody, ktorú stihne napáchať zle vystrelený tool call, kým si to niekto všimne.

Praktická taxonómia vyzerá takto. Štyri úrovne, od najbezpečnejšej po najnebezpečnejšiu.

Prvá je read-only. Tieto nástroje nemenia nič externé, napríklad `get_weather` alebo `search_tickets`. Nepotrebujú žiadny bezpečnostný mechanizmus.

Druhá je meniace, ale vratné. Tieto už zapisujú, ale vrátiť zápis späť je lacné, napríklad `create_ticket` alebo `send_draft_email`. Logujte každé volanie a máte audit trail.

Tretia je meniace a nevratné. To sú zápisy, ktoré sa ťažko vracajú späť, napríklad `charge_card` alebo `post_to_slack`. Tie potrebujú explicitné potvrdenie, a nie len ako inštrukciu modelu, ale ako bránu na úrovni kódu.

A napokon katastrofické. Sem patria nástroje deštruktívne, viacpoužívateľské a hlučné, napríklad `drop_database`, `delete_user` alebo `publish_press_release`. Pri týchto musí byť v slučke človek. Nenechajte agenta volať ich priamo.

Pokušenie je zaobchádzať s každým nástrojom rovnako, pretože framework s nimi na prvý pohľad tak trochu rovnako zaobchádza. Neurobte to, pretože každá úroveň si naozaj zaslúži inú mieru ochrany.

---

## Slide 19 — The rule: put the guard in the tool code

Ak si z tejto vsuvky máte odniesť jedno pravidlo, je to toto: ochranu dajte do kódu nástroja, nie do inštrukcie.

A tu je dôvod, prečo na tom rozdieli naozaj záleží. Inštrukcia je len zdvorilá prosba, ktorú model môže ignorovať alebo zle pochopiť. Kód je naopak múr. Ak váš nástroj na mazanie ticketov kontroluje confirmation token v Pythone, žiadna inštrukcia na svete ho neobíde. Ak je ale vaša kontrola len niečo ako „najprv sa spýtaj používateľa“ v system prompte, model ju občas preskočí. A keď vás to prvýkrát bude stáť dáta, budete ľutovať, že ste to nevynútili v kóde.

---

## Slide 20 — A delete tool with a confirmation gate

Pozrite sa na kód na slide. Funkcia sa volá `delete_ticket` a robí presne to, čo hovorí jej meno, natrvalo by zmazala support ticket. Zaujímavá časť je argument navyše, `confirmation_token`, s východiskovou hodnotou prázdneho stringu. Funkcia porovnáva token s očakávanou hodnotou vypočítanou z ID ticketu. Ak token sedí, mazanie prebehne. Ak je token prázdny alebo nesprávny, funkcia len vráti náhľad a nespraví nič.

Inštrukcia modelu potom môže znieť napríklad tak, že najprv má volať s prázdnym tokenom, ukázať náhľad, potvrdiť si to s používateľom a skutočný token použiť až vtedy, keď používateľ explicitne súhlasí. Ak ale model čokoľvek z toho preskočí a pokúsi sa cestu skrátiť a zavolať mazanie priamo, nástroj aj tak vráti len náhľad a mazanie sa nestane.

Všimnite si tu jemný detail. Očakávaný token sa počíta z ID ticketu. Model, ktorý by sa nejaký fixný token náhodou naučil z trénovacích dát, si ho tak nemôže jednoducho zapamätať a prekĺznuť cez kontrolu.

---

### Notebook break — The guarded delete in action

[Prepnite obrazovku na notebook.]

Tu je agent so zapojeným chráneným nástrojom `delete_ticket`. Používateľ hovorí: „Delete ticket T-1001.“ [Spustite bunku.] Pozrite, čo sa deje v prúde eventov. Agent zavolal `delete_ticket` bez confirmation tokenu, pretože tak vyzerá východiskové prvé volanie. Nástroj vrátil náhľad, nie zmazanie. Agent náhľad ukáže používateľovi a pýta si potvrdenie. Dáta sú v bezpečí. V druhom ťahu so správnym tokenom by mazanie naozaj prebehlo, ale len s týmto explicitným odovzdaním.

[Prepnite späť na prezentáciu.]

---

## Slide 21 — Choosing a flavor

Skôr než uzavrieme, dám vám rýchlu pomôcku, kedy siahnuť po ktorom druhu. Ak chcete Python funkciu bežiacu priamo v procese, použite FunctionTool. Ak ide o existujúce REST API so špecifikáciou, použite OpenAPIToolset. Ak je to tool server napísaný v hocijakom jazyku s vlastným stavom, použite McpToolset. A ak ide o špecialistického sub-agenta, ktorého má rodič volať ako funkciu, použite AgentTool.

FunctionTool je v skutočnosti východisková voľba. Po ostatných siahnite len vtedy, keď máte konkrétny dôvod, napríklad iný jazyk, existujúcu špecifikáciu alebo zdieľaný katalóg nástrojov.

---

## Slide 22 — Gotchas worth knowing now

Ostávajú tri skutočné chytáky, ktoré sa oplatí pomenovať skôr, než odídete.

Prvý je, že vstavané Google nástroje, ako Search, spúšťanie kódu a Vertex Search, nemôžu koexistovať s inými nástrojmi v tom istom agentovi. Výnimka existuje pre Search na ADK 1.16 a novšom, cez `bypass_multi_tools_limit=True`. Inak musíte každý vstavaný nástroj zabaliť do vlastného sub-agenta. Tento vzor uvidíme neskôr v kurze, keď sa dostaneme k funkciám špecifickým pre Gemini.

Druhý chyták sa točí okolo MCP cez stdio v Jupyteri alebo Colabe. Jupyter nahrádza `sys.stderr` objektom, ktorý nemá `.fileno()`, a to rozbije spúšťanie subprocesu. Náš notebook to našťastie automaticky patchuje v setup bunke. Ak ale niekedy budete písať vlastnú MCP integráciu v notebooku, nezabudnite najprv patchnúť `sys.stderr`.

A tretí chyták sa týka streamingu. LiteLLM plus tool cally plus streaming je na modeloch mimo Gemini známy svojou nespoľahlivosťou. Preto majú tool-calling demá v ADK východiskovo vypnutý streaming, čo je pre naše účely správna voľba. Ak streaming v produkcii zapnete späť, cesty s nástrojmi otestujte poriadne.

---

## Slide 23 — What to carry forward

Čo si teda z dneška odniesť? Nástroje naozaj prichádzajú v štyroch druhoch. Pre model rovnaká abstrakcia, len iné integračné ciele, teda FunctionTool, OpenAPIToolset, McpToolset a AgentTool.

A potom je tu dizajnové pravidlo zo vsuvky. Na blast radiuse záleží, a práve preto chcete ochranu v kóde nástroja, nie v inštrukcii.

---

## Slide 24 — Up next

Nabudúce sa ponoríme do Sessions, State, Events a Artifacts, teda do toho, kde naozaj býva pamäť konverzácie. Pozrieme sa, ako agenta naučiť pamätať si používateľa naprieč oddelenými konverzáciami, na štvorúrovňový systém rozsahov, ktorý rozhoduje, či pamäť vydrží jeden ťah alebo navždy, a na tri vzory zapisovania stavu. Vidíme sa tam.
