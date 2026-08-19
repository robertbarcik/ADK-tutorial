# M01 — Speaker notes (SK)

---

## Slide 1 — Title

Vitajte v prvom module. Toto je základ celého kurzu, kde si postavíme mentálny model, na ktorom stojí všetko ostatné. Naším širším cieľom v kurze je naučiť sa stavať produkčne pripravených AI agentov v Pythone pomocou Agent Development Kitu od Googlu. Skôr než sa ale pustíme do hlbšieho kódu, venujeme chvíľu štyrom primitívom, ktoré sa objavia v každom ďalšom module: Agent, Runner, Event a Session.

Tieto štyri primitívy sú celý mentálny model ADK. Keď ich budete mať jasne v hlave, zvyšok frameworku a vlastne aj zvyšok kurzu sa už len prirodzene rozvíja na nich. Poďme na to.

---

## Slide 2 — What ADK is

ADK je Agent Development Kit od Googlu, framework v Pythone na stavbu agentov. Google ho uvoľnil ako open source, verzia 1.0 vyšla v máji 2025, verzia 2.0 na jar 2026, a v čase nahrávania sme na línii 2.x. Veľkou novinkou vo verzii 2.0 bol grafový workflow runtime pre pokročilé zostavy, a dobrá správa je, že klasické agentové API, ktoré sa v kurze naučíte, prešlo do 2.x bez zmeny. Existujú aj SDK pre Javu, Go a TypeScript, ale novinky pristávajú najprv v Pythone, a tam žije aj tento kurz.

A teraz štyri veci, ktorými ADK NIE JE, pretože sa na ne ľudia pýtajú často a oplatí sa ich pomenovať hneď na začiatku. Nie je to model. Model si prinášate vlastný, a v tomto kurze budeme používať Claude, GPT a Gemmu dávno predtým, než sa dotkneme Gemini. Nie je to ani cloud. Dnes beží na vašom notebooku a zajtra napríklad na Cloud Rune, bez akejkoľvek závislosti na Google Cloude. Nie je to UI. Existuje vývojárske rozhranie menom `adk web`, ktoré o chvíľu uvidíme, ale výstupom vašej práce je kód, nie obrazovky. A napokon, nie je to graph DSL. Píšete typovaný Python, nie JSON s uzlami a hranami.

---

## Slide 3 — Why a framework at all

Úprimný test, či sa nejaký framework oplatí naučiť, znie takto: čo prestanete písať, keď ho prijmete? Pri ADK je odpoveď zhruba šesťdesiat riadkov kódu, ktoré by ste inak písali zakaždým, keď staviate agenta ručne.

Prestanete písať retry slučku, ktorá obaľuje volanie LLM pre prípad, že sieť zaškrtá. Prestanete písať JSON parser, ktorý prvé tri tool response zvládne a na štvrtej spadne, pretože model sa rozhodol dať do JSONu komentár. Prestanete si ručne viesť históriu konverzácie a orezávať ju skôr, než pretečie kontextové okno. A prestanete písať obe polovice obsluhy nástrojov: switch, ktorý mapuje mená nástrojov na funkcie, aj chybovú vetvu pre prípad, že si model vymyslí nástroj, ktorý vôbec neexistuje.

Framework si svoje miesto zaslúži vtedy, keď vás odbremení od takéhoto boilerplatu a nechá vás písať veci, ktoré sú naozaj vaše: inštrukciu, nástroje, biznis logiku. Presne túto dohodu vám ADK ponúka.

---

## Slide 4 — The agent equation

Skôr než si ich predstavíme jeden po druhom, tu je celý obraz v jednom riadku. Agent je v skutočnosti len LLM a pár vecí okolo neho: inštrukcia, ktorá mu hovorí, ako sa má správať, nástroje, ktoré môže volať, kúsok pamäte o tom, čo sa stalo predtým, a slučka, ktorá to celé spája. To je celá rovnica.

O slučku a všetko okolo nej sa stará ADK. Štyri kusy, ktoré prinášate vy, sú LLM, inštrukcia, nástroje a pamäť, a vidíte ich priamo na slide. Držte si tento obraz poruke, kým budeme prechádzať primitívmi, pretože štyri primitívy, ktoré o chvíľu stretnete, sú len spôsob, akým ADK túto rovnicu balí.

---

## Slide 5 — The four primitives

Tu sú štyri primitívy, ktoré som spomínal. Budem ich opakovať často, pretože tvoria celý mentálny model.

Agent je vec, v ktorej býva LLM: meno, model, inštrukcia a voliteľne nástroje. Runner poháňa konverzáciu dopredu, je to event loop, ktorý si môžete predstaviť ako herný engine idúci tick po ticku. Event je každá jedna vec, ktorá sa počas behu stane: správa používateľa, odpoveď modelu, tool call, zmena stavu. A Session je pamäť konverzácie, teda história eventov plus stavový slovník, kľúčovaná názvom aplikácie, ID používateľa a ID session.

Všetko ostatné v ADK sa skladá na týchto štyroch primitívoch: workflow agenti, hierarchie viacerých agentov, callbacky, pamäťové služby, evaluácia, úplne všetko. Zvládnite tieto štyri a zvyšok kurzu sa rozvinie sám.

---

## Slide 6 — Agent

Na slide máme agenta menom `greeter`, ktorého jedinou úlohou je odpovedať používateľom priateľskou jednovetovou správou. Na definovanie akéhokoľvek agenta v ADK potrebujete štyri povinné argumenty a všetky štyri tu vidíte. Name je to, ako ADK agenta volá interne a v eventoch. Model je zabalený v pomocníkovi LiteLlm, a práve tento wrapper robí ADK vendor-neutrálnym, čo uvidíme o pár slidov ďalej. Description je jednovetový popis, ktorý vidia ostatní agenti, keď sa tento stane sub-agentom v hierarchii. A instruction je system prompt, teda text, podľa ktorého sa model rozhoduje, ako sa správať.

Keby ste tomuto agentovi chceli dať nástroje, pridáte argument `tools=[...]` so zoznamom funkcií. Tu žiadne nie sú, pretože tento agent iba zdraví.

---

## Slide 7 — Runner

Pozrite sa na chvíľu na slide. Aby náš greeter naozaj bežal, potrebujeme Runner. Vytvoríme ho, podáme mu agenta a session service, a potom v async slučke iterujeme cez eventy, ktoré beh produkuje. Toto je skutočná mašinéria ADK konverzácie.

Prečo vlastne Runner potrebujeme? Agent je sám o sebe nehybný. Nerobí nič, kým ho niečo nezdvihne a nepotiahne konverzáciu dopredu. A to niečo je Runner. Prepojí agenta so session service a vráti vám asynchrónny prúd eventov.

Mentálny model Runnera je hlavná slučka herného enginu. Váš agent je entita, ktorá dostáva tiky. Pri každom ticku Runner zatlačí aktuálny stav konverzácie do modelu, vytiahne z neho, čo model vyprodukoval, a za každý pozorovateľný krok vydá event. Vy cez tie eventy iterujete a rozhodujete sa, čo s ktorým spraviť.

Ak ste niekedy robili s Node.js middleware alebo s request pipeline v Exprese, tento tvar poznáte. Rovnaká myšlienka: eventy tečú, vy ich spracúvate, konáte.

---

## Slide 8 — Event

Event je primitív, ktorým sa ADK odlišuje od väčšiny agentových frameworkov. Každá jedna komunikácia počas behu agenta vyprodukuje event, a slovom každá myslím naozaj každá. Keď používateľ pošle správu, je to event. Keď model napíše odpoveď, ďalší event. Keď sa model rozhodne zavolať nástroj, samotné volanie je event a hodnota, ktorú nástroj vráti, tiež. Keď jeden agent odovzdá prácu sub-agentovi v hierarchii, vidíte to ako event. Dokonca aj zmena v stavovom slovníku vystrelí vlastný event.

Prečítajte si eventy a viete presne zrekonštruovať, čo agent urobil a prečo. Toto je debugger agentovej práce. Keď sa ma študenti pýtajú, ako debugovať ADK agenta, odpoveď je vždy rovnaká: čítajte eventy.

---

## Slide 9 — Session

Session je štvrtý primitív. Drží históriu eventov plus stavový slovník jednej konverzácie a je kľúčovaná trojicou: názov aplikácie, ID používateľa a ID session. Jedna konverzácia, jedna session.

ADK prináša tri session services. Prvá je `InMemorySessionService`, slovník v Pythone, ktorý žije len tak dlho ako váš proces. Skvelá na demá a testy, a presne ju budeme používať väčšinu kurzu. Druhá je `DatabaseSessionService`, ktorá beží na SQLAlchemy, takže zvládne čokoľvek od SQLite na notebooku po spravovaný Postgres v produkcii. Po tej by ste siahli v self-hosted ADK službe. A napokon `VertexAiSessionService`, tá je pre vás, ak už bežíte na Google Cloude a Vertexe.

Väčšinu kurzu zostaneme pri in-memory službe. Neskôr, keď sa perzistentná pamäť stane témou celého modulu, prepneme na databázovú službu a budete si môcť popri notebooku pustiť Postgres kontajner a skúšať to so mnou.

---

### Notebook break — Run the greeter agent

[Prepnite obrazovku na notebook.]

Teraz toho greetera, ktorého sme si práve definovali, naozaj spustím. Agent je tu, Runner je prepojený so session service a posielam jednu správu používateľa, „hi“. Prejdem cez každý event, ktorý sa vráti, a vypíšem ho. [Spustite bunku.] Jeden event. Označený `FINAL`. Vo vnútri odpoveď greetera. Toto je najmenší prúd eventov, aký ADK konverzácia vie vyprodukovať.

[Prepnite späť na prezentáciu.]

---

## Slide 10 — The simplest event stream

Práve ste to videli bežať. Na slide je ten istý event stream ako statický diagram, ku ktorému sa môžete vracať. Jeden event, označený `FINAL`, s odpoveďou greetera.

Menej už konverzácia vyprodukovať nevie. Samo o sebe to nie je nič zaujímavé, ale je to základná čiara, s ktorou porovnáme, čo sa stane, keď tomu istému agentovi pridáme nástroj.

---

## Slide 11 — Add a tool

Tu máme funkciu `get_weather`, ktorá vezme názov mesta a vráti malý slovník so správou o počasí. Pod ňou je agent nastavený tak, aby túto funkciu zavolal vždy, keď sa používateľ pýta na počasie. To je náš príklad nástroja.

Pointa tohto slidu je, čo sa v ADK počíta za nástroj. Nástroje sú jednoducho funkcie v Pythone. Na tejto úrovni abstrakcie je to naozaj celý model nástrojov.

Napíšete funkciu s docstringom a type hintmi a ADK si z nich zostaví JSON schému, ktorú uvidí model. Žiadne dekorátory, žiadne konfiguračné súbory, žiadna registrácia nástrojov.

Jednu vec treba zdôrazniť hneď: na docstringu naozaj záleží. Model ho číta, aby sa rozhodol, kedy nástroj zavolať, takže vágny docstring vedie k zlému použitiu a konkrétny k správnemu. Pravidlo je jednoduché: docstringy nástrojov píšte pre model, nie pre človeka.

---

### Notebook break — Add a tool and watch the events multiply

[Prepnite obrazovku na notebook.]

Rovnaká zostava ako predtým, len agent má teraz zapojený nástroj `get_weather`. Posielam otázku: „What's the weather in Prague?“ [Spustite bunku.] Sledujte, ako prúd eventov narastie. Najprv event s tool callom: model usúdil, že treba `get_weather` s argumentom `city='Prague'`. Potom event s tool response: ADK funkciu spustilo a návratová hodnota, `{'city': 'Prague', 'report': 'Cloudy, 14C'}`, je tu. A nakoniec finálna textová odpoveď modelu, prirodzená veta o počasí v Prahe. Tri eventy namiesto jedného, a všetky viditeľné.

[Prepnite späť na prezentáciu.]

---

## Slide 12 — The event stream with a tool

Tu je ten istý prúd eventov ako statický diagram, ku ktorému sa môžete vracať. Tri eventy: tool call, tool response a finálna textová odpoveď.

Zapamätajte si tento tvar. Keby model zavolal nesprávny nástroj, videli by ste to v prvom evente. Keby volal dva nástroje za sebou, videli by ste obe volania, obe odpovede a potom finálnu odpoveď. Toto je tvar správania agenta a presne preto je event stream debuggerom vývoja agentov.

---

## Slide 13 — adk web

Všetko, čo sme si práve vypísali, sa dá prehliadať aj vizuálne. Spustite `adk web` z priečinka, v ktorom máte agenta, a v prehliadači sa otvorí chatovacie rozhranie s tým istým prúdom eventov vykresleným ako klikateľná časová os. Rovnaké dáta, len sa v nich príjemnejšie hľadá.

Počas vývoja majte `adk web` otvorené. Keď agent spraví niečo nečakané, či už vráti zlú odpoveď, zavolá nástroj so zlým argumentom, alebo odmietne niečo, čo urobiť mal, dôvod je z časovej osi takmer vždy zjavný. Možno nástroj vrátil zlý tvar. Možno bola inštrukcia nejednoznačná. Možno bol nejaký kľúč v state zastaraný.

Vo zvyšku kurzu sa budeme spoliehať na textové výpisy, pretože sa čisto vkladajú do videa. Ale vo vlastnej práci je `adk web` najlepší debugger agentov, aký dostanete zadarmo.

---

## Slide 14 — ADK vs. the alternatives

Tu je férové porovnanie s alternatívami. LangGraph je líder trhu, má tridsaťštyri miliónov stiahnutí mesačne a chce, aby ste svoj riadiaci tok nakreslili ako explicitný graf uzlov a hrán. Na komplexnú orchestráciu je to správny nástroj, na čokoľvek jednoduché je ťažkopádny. CrewAI ide opačnou cestou. Je to DSL na hranie rolí, kde deklarujete povedzme Výskumníka a Pisateľa a framework ich poskladá dokopy. Na demách rýchly, v metafore vyhranený, a drží zhruba štyridsaťštyritisíc hviezd.

ADK sedí niekde medzi nimi. Komunita je menšia, okolo osemnásťtisíc hviezd, ale dostanete typovaný Python namiesto DSL, explicitné primitívy namiesto metafor a najčistejšiu observability na úrovni eventov, akú som v týchto frameworkoch videl. Ak si chcete uvažovanie vlastného agenta naozaj prečítať krok po kroku, ADK je k tomu najkratšia cesta.

---

## Slide 15 — Vendor lock-in, addressed

Na slide sú štyri rôzne deklarácie modelu a každá mieri na iný LLM. Gemini priamo od Googlu. Claude cez OpenRouter. GPT cez OpenRouter. A model Qwen bežiaci lokálne na vašom notebooku cez Ollamu. Rovnaký agent, rovnaké nástroje, rovnaká inštrukcia, len iný riadok `model=`.

Prečo tento slide vôbec existuje? Najčastejšia námietka proti ADK znie: „veď je to framework od Googlu.“ Áno. Google ho napísal a predáva ním Gemini a Vertex. To ale neznamená, že Gemini musíte používať. Abstrakcia modelu je naozaj výmena jedného riadku a tie štyri deklarácie na slide sú všetko, čo treba zmeniť.

Prvá časť kurzu používa LiteLLM cez OpenRouter od začiatku do konca. Môžete vziať ktorýkoľvek notebook, zmeniť reťazec modelu a spustiť ho na Claude, GPT alebo Gemme, ako je vám milé. Keď prídeme k druhej časti, prepneme na Gemini priamo, pretože funkcie, ktoré odtiaľ učíme, ako vyhľadávanie s citáciami, cachovanie dlhého kontextu, thinking budgety a hlasové Live API, existujú len na Gemini. Dovtedy je ADK presne tak vendor-neutrálne, ako chcete.

---

## Slide 16 — The arc of the course

Toto je mapa kurzu. Prvá časť je vendor-agnostická chrbtica: agenti, nástroje, sessions, workflow agenti, zostavy viacerých agentov, callbacky, pamäť, evaluácia a nasadenie. Celá beží na čomkoľvek, kam dosiahne LiteLLM.

Druhá časť je o tom, o čo prichádzate, keď Gemini nepoužívate. Odpovede podložené vyhľadávaním s citáciami, kde model siahne na Google a uvedie URL, z ktorej čerpal. Otázky nad dlhým kontextom s cachovaním, takže si milión tokenov kontextu držíte v cache a platíte len za prompt. Thinking budgety, ktorými meníte latenciu za kvalitu uvažovania. A hlasové Live API, ktoré je v tomto priestore jediná schopnosť len pre Gemini, pri ktorej naozaj padne sánka.

A záverečný modul je krátka odbočka k A2A, protokolu medzi agentmi. Je zámerne krátky, pretože A2A je priveľmi nové na to, aby sa učilo ako infraštruktúra, ale priveľmi dôležité na to, aby sme ho preskočili.

---

## Slide 17 — Four artifacts per module

Každý modul prináša štyri artefakty, ktoré spolu držia krok. Po prvé slidy, na ktoré sa práve pozeráte. Po druhé speaker notes, ktoré práve čítam, dostupné ako markdown, takže si ich môžete nahrať vlastným hlasom, preložiť alebo jednoducho prečítať. Po tretie kapitola v učebnici, teda dlhšia prozaická verzia s vypracovanými príkladmi a chytákmi. A po štvrté Jupyter notebook s presne tým kódom, ktorý ste videli v demu, spustiteľný odhora nadol s vaším vlastným API kľúčom.

Naprieč všetkými štyrmi platí jedna kľúčová vlastnosť: pojem definovaný na slide je ten istý pojem v speaker notes, ten istý v učebnici a ten istý v notebooku. Vyberte si teda artefakt, ktorý sedí tomu, ako sa učíte najlepšie, a spoľahnite sa, že ostatné s ním zostávajú konzistentné.

---

## Slide 18 — Write these down

Agent. Runner. Event. Session. Ak tieto štyri viete povedať nahlas bez pozerania na slide, ste pripravení na to, čo príde. Ak ste pri niektorom zaváhali, prelistujte sa späť k ilustráciám event streamov na predchádzajúcich slidoch, alebo si otvorte notebook a nanovo spustite bunky, ktoré sme spúšťali spolu.

Nabudúce sa pustíme do nástrojov. Dnes sme mali jeden druh, obyčajnú funkciu v Pythone. ADK má ďalšie tri druhy nástrojov a postavíme si po jednom z každého. Vidíme sa tam.
