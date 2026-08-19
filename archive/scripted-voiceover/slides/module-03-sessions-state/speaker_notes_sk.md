# M03 — Speaker notes (SK)

---

## Slide 1 — Title

Sessions, state, eventy a artifakty. To je téma tohto modulu. Väčšina zlyhaní agentov v produkcii totiž nie je o uvažovaní, ale o pamäti. Agent zabudne, kto ste, medzi jednotlivými sessions, zabudne, čo ste mu povedali pred piatimi minútami, alebo ešte horšie, pamätá si niečo, čo už nie je pravda. Tento modul je o tom, ako pamäť v ADK naozaj funguje a ako ju dobre navrhnúť. Na konci budete vedieť, ako prinútiť agenta zapamätať si používateľa naprieč oddelenými konverzáciami, prečo päťznakový prefix rozhoduje o tom, či pamäť vydrží jeden ťah alebo navždy, a spoznáte tri vzory zápisu stavu, z ktorých dva fungujú a jeden potichu zlyháva. Poďme na to.

---

## Slide 2 — Stateless vs stateful

Rámec celého modulu je jednoduchý. Bezstavový agent je len salónny trik. Každý ťah začína od nuly, takže medzi konverzáciami nevedie žiadna niť. Čokoľvek ste agentovi povedali včera, je preč. Čokoľvek zistil v minulej session, je tiež preč. Stavový agent je naproti tomu infraštruktúra. Vie, kto sú jeho používatelia, na čo sa už pýtali a aké rozhodnutia už urobil. A presne toto je rozdiel medzi demom a produktom.

---

## Slide 3 — A session is two things

Poďme rozbaliť, čo vnútri session naozaj žije. Session identifikujú tri reťazce, teda názov aplikácie, ID používateľa a ID session. Táto trojica je primárny kľúč každej session v každom session store, bez ohľadu na backend.

Samotná session drží dve veci. Prvou je zoznam eventov, teda úplná usporiadaná história každej správy, každého tool callu, každej tool response a každej mutácie stavu. Z vlastného kódu do nej nič nepridávate, to robí ADK za vás, takže z vašej strany je read-only.

Druhou je state dict, teda stavový slovník. Ide o meniteľné key-value úložisko pre čokoľvek, čo má agent prenášať medzi ťahmi. A práve tam sa deje to podstatné.

---

## Slide 4 — Three session services

ADK prináša tri session services. Prvá je in-memory a všetko ukladá do slovníka v Pythone. Pri reštarte procesu stratí úplne všetko, takže je ideálna na testy a notebooky, a práve ju budeme používať väčšinu kurzu. Druhá je databázová, beží na SQLAlchemy a funguje proti Postgresu, MySQL aj SQLite. To je produkčný štandard. Tretia je postavená na Vertex AI a siahli by ste po nej len vtedy, keď už bežíte na Google Cloude a plánujete tam zostať.

Rozhranie je pri všetkých troch rovnaké. Neskôr v kurze, keď sa perzistentná pamäť stane témou celého modulu, vymeníme in-memory službu za databázovú a kód agenta sa pritom nezmení. Presne to je zmysel celej abstrakcie.

---

## Slide 5 — State with scope prefixes

Teraz k dôležitej časti, ktorou je state so scope prefixami, teda prefixami rozsahu. Je to najužitočnejšia slabo zdokumentovaná funkcia v ADK a zároveň tá, ktorú budete používať každý jeden deň.

---

## Slide 6 — Four scope tiers

Stavový slovník je obyčajný Python dict, ale prefix v kľúči rozhoduje o životnosti hodnoty. Existujú štyri úrovne.

Prvou sú kľúče bez prefixu. Tie žijú iba v tejto jednej session, takže keď session zmažete, sú preč.

Druhou je `user:` prefix, čítame ho ako user dvojbodka, ktorý pretrváva naprieč všetkými sessions daného používateľa. Takže ak má Alica session jeden a session dva, čokoľvek zapíše do `user:favorite_color` v prvej session, uvidí aj v tej druhej.

Treťou je `app:` prefix, ktorý je globálny naprieč celou aplikáciou. Rovnaké `app:` hodnoty vidia všetci používatelia, a preto si ho chcete šetriť na veci, ktoré sú naozaj celoaplikačné.

A napokon `temp:` prefix, ktorý platí len pre jednu invokáciu. Hodnota žije počas tohto jedného behu a po jeho skončení sa zahodí. Hodí sa na pracovné medzivýsledky, ktoré nástroj potrebuje preniesť medzi krokmi v rámci jedného volania.

Dokopy sú to teda štyri prstence rozsahu a prstenec si vyberáte voľbou prefixu.

---

## Slide 7 — Mental model: four rings

Na slide vidíte vizuálnu podobu týchto štyroch úrovní. App state je úplne vonkajší prstenec, viditeľný pre všetkých. Vo vnútri je user state, ohraničený na jedného používateľa. Ešte hlbšie je session state, ohraničený na jednu session jedného používateľa. A v strede je temp state, ktorý zmizne v momente, keď beh skončí.

Praktické pravidlo znie: pri zápise si vyberte správny prstenec. Obľúbená farba patrí do `user:`, pretože nemá presiaknuť k iným používateľom, ale má prežiť session. Šablóna system promptu patrí do `app:`, pretože ju všetci používatelia používajú rovnakú. A pracovný výpočet aktuálneho ťahu patrí do `temp:`, pretože ten nikto iný nikdy nepotrebuje vidieť.

---

## Slide 8 — Writing state from a tool

Tu máme funkciu `remember_favorite_color`. Vezme farbu ako reťazec a zapíše ju do stavu agenta, aby si ju agent vedel neskôr vybaviť. Samotný zápis sa deje na tomto riadku: `tool_context.state["user:favorite_color"] = color`. Toto jediné priradenie spôsobí, že hodnota pretrvá.

Poďme rozobrať, ako to funguje. Funkcia nástroja má navyše parameter `tool_context: ToolContext`. Ten pri volaní nepodávate vy, ADK doň automaticky vloží bežiaci kontext zakaždým, keď sa nástroj spustí. Z pohľadu vášho kódu sa `tool_context.state` správa ako obyčajný slovník v Pythone. Všetko, čo doň priradíte, sa ale v pozadí zaznamená ako event, a práve tento event session service uloží.

V kóde si všimnite dve veci. Po prvé, parameter sa musí volať presne `tool_context`, s podčiarkovníkom, pretože ADK hľadá presne toto meno, takže ani `context`, ani `ctx` fungovať nebudú. Po druhé, `user:` prefix v kľúči je to, vďaka čomu hodnota prežije aj za hranicou tejto session. Keď prefix vynecháte, hodnota zmizne spolu so zmazanou session.

---

### Notebook break — Cross-session memory in action

[Prepnite obrazovku na notebook.]

Ukážem vám, ako to naozaj beží. Farbový agent je tu už pripravený, aj s nástrojmi `remember_favorite_color` a `recall_favorite_color`, ktoré sme si práve pozreli na slide. Začnem prvou session, v ktorej agentovi poviem, že moja obľúbená farba je teal. [Spustite bunku prvej session.] Pozrite na event stream, ktorý sa vráti. Vidíte tool call na `remember_favorite_color` s argumentom `color='teal'` a potom state deltu, ktorá zaznamenáva zápis do `user:favorite_color`. Session tu končí.

Teraz spustím druhú session. Rovnaký používateľ, ale úplne nové session ID a žiadny počiatočný state. Jednoducho sa spýtam: „what's my favorite color?" [Spustite bunku druhej session.] Sledujte, čo sa stane. State nie je prázdny. ADK načítalo session, videlo, že tento používateľ už má kľúč s `user:` prefixom, a automaticky prenieslo `favorite_color = 'teal'` do novej session. Agent zavolá `recall_favorite_color`, prečíta hodnotu a odpovie „teal".

[Prepnite späť na prezentáciu.]

---

## Slide 9 — The wow moment

Práve ste to videli bežať. Na slide je tá istá vec ako diagram, ktorý si môžete odniesť v hlave. Prvá session zapisuje, druhá session hodnotu číta späť a medzi nimi nie je nič okrem `user:` prefixu, ktorý robí celú prácu.

Pamäť naprieč sessions ste dostali za päť znakov. Žiadne nastavovanie databázy, žiadny vector store, žiadna embedding pipeline, len konvencia prefixu na kľúči slovníka.

---

## Slide 10 — Three ways to write state

Existujú tri vzory zápisu stavu. Dva z nich fungujú, jeden nie, a bohužiaľ je to práve ten, po ktorom ľudia siahnu ako po prvom.

Prvý vzor je `output_key=` na agentovi. Keď konštruujete LlmAgent, podáte mu `output_key="last_response"`. Po každom behu sa finálna textová odpoveď modelu automaticky uloží pod tento kľúč. Hodí sa to na cachovanie a tiež na odovzdávanie výstupu medzi workflow agentmi, čo uvidíme v neskoršom module.

Druhý vzor je `tool_context.state[key] = value` vnútri nástroja. To je presne ten vzor, ktorý ste videli na predchádzajúcich slidoch. Funguje a hodnoty pretrvajú.

Tretí vzor je pasca. Cez `get_session()` si vytiahnete session, dostanete späť objekt so slovníkom `.state` a priradíte doň priamo, teda `session.state["foo"] = "bar"`. Toto priradenie nepretrvá, pretože pri ďalšom volaní `get_session()` pre tú istú trojicu je preč. Nikto vám nepovie, že sa to deje, len sedíte a čudujete sa, prečo sa state neukladá.

---

## Slide 11 — The rule

Celé pravidlo sa zmestí na jeden slide. Na agentovi používajte `output_key=`, vnútri nástroja používajte `tool_context.state[...]` a nikdy nepriraďujte priamo do slovníka `.state` vrátenej session. Prvé dva spôsoby pretrvajú, pretože idú cez eventy. Tretí eventy obchádza, a pritom práve cez eventy ADK stav ukladá.

V notebooku nájdete bunku, ktorá túto pascu explicitne demonštruje. Spustite si ju vo voľnej chvíli a uvidíte, ako hodnoty z priameho priradenia pri ďalšom načítaní zmiznú.

---

## Slide 12 — Events and Artifacts

Druhá časť modulu patrí eventom a artifaktom. Prejdeme ňou rýchlejšie, pretože v každodennej praxi je najdôležitejšia práve látka o state.

---

## Slide 13 — Events: the immutable ledger

Eventy sú nemenná účtovná kniha session, po anglicky immutable ledger. Každý ťah vyprodukuje eventy a session si ich všetky ponechá. Cez `session.events` viete prejsť a zauditovať, čo sa stalo, prehrať si konverzáciu odznova alebo ju podať evaluačnej sade.

Diagram na slide ukazuje skutočnú históriu eventov z dema s obľúbenou farbou. Dokopy sú to štyri eventy. Najprv vstup používateľa, potom tool call, potom tool response so state deltou zaznamenávajúcou zápis farby a napokon finálna textová odpoveď s druhou state deltou, ktorá zaznamenáva uloženie cez `output_key`.

State je v skutočnosti len projekcia tohto event streamu. Keď si session vytiahnete, ADK prehrá eventy v poradí, aplikuje state delty a podá vám výsledný stav. Tomuto prístupu sa hovorí event sourcing a je to dôvod, prečo neskôr v kurze vymeníte in-memory sessions za databázové bez toho, aby si to kód agenta všimol. Dátový model je rovnaký, mení sa len úložisko.

---

## Slide 14 — Artifacts: binary blobs outside events

Ešte krátko k štvrtému konceptu, ktorým sú artifakty. Artifakty slúžia na binárne dáta, teda obrázky, audio, PDF alebo akýkoľvek veľký blob, ktorý chcete priviazať k session, ale nechcete ho serializovať priamo do eventov.

Dobrá analógia je Git LFS pre agentov. Ukazovateľ žije v event streame, zatiaľ čo samotný obsah žije v oddelenom úložisku.

Tri artifact services zrkadlia session services. Existuje in-memory verzia na testy, verzia nad Google Cloud Storage pre produkciu a základná trieda, ktorú si viete sami implementovať pre S3, Azure, MinIO alebo čokoľvek iné, čo používate. Pri textových agentoch v prvej časti kurzu artifakty v podstate nebudete potrebovať. Svoju hodnotu ukážu neskôr, v module o hlasovom Live API.

---

## Slide 15 — Skeptical Memory

Nasleduje krátka vsuvka z publikácie Agentic Design Patterns, konkrétne z druhej kapitoly o perzistentnom kontexte. Vzor má meno Skeptical Memory, teda skeptická pamäť.

---

## Slide 16 — Memory staleness is real

Zastaranosť, po anglicky staleness, je to, čo vám demo neukáže. Demo vyzerá čisto, pretože state ešte nemal čas zostarnúť. V produkcii to takto nefunguje.

Obľúbená farba používateľa spred troch mesiacov zrejme stále platí. Jeho aktuálny projekt už ale pravdepodobne nie, pretože sa mohol posunúť ďalej bez toho, aby to agentovi povedal. Tikety, ktoré si agent včera zapamätal ako otvorené, môžu byť dnes všetky zatvorené. A IP adresa servera, ktorú si nacachoval MCP nástroj, mohla byť medzitým pridelená inému stroju.

Uložená pamäť je preto len nápoveda, nie fakt. Ak s ňou zaobchádzate ako s faktom, deň, keď zostarne, bude dňom, keď váš agent urobí niečo trápne.

---

## Slide 17 — Three guidelines from the publication

Z publikácie vychádzajú tri usmernenia.

Po prvé, pri rozhodnutiach, kde ide o veľa, uprednostnite retrieval namiesto recall, teda vyhľadávanie namiesto spomínania. Skôr než agent pošle e-mail, strhne platbu z karty alebo nasadí kód, mal by zavolať read-only nástroj a stav si nanovo overiť, nie veriť vlastnému uloženému state. Jeden tool call navyše je lacný v porovnaní s cenou konania na základe zastaranej informácie.

Po druhé, ohraničujte svoj state agresívne. Používajte `temp:` pre pracovné poznámky, kľúče bez prefixu pre veci platné v jednej session, `user:` pre veci, ktoré sa menia len vtedy, keď ich používateľ výslovne zmení, a `app:` pre naozaj nemennú konfiguráciu. Čím užšie je state ohraničený, tým menej zastaranosti dokáže spôsobiť.

Po tretie, keď zapisujete do user alebo app rozsahu, zalogujte dôvod. O pár mesiacov budete debugovať agenta konajúceho na základe polročnej pamäte a jednoriadková poznámka o tom, prečo sa hodnota uložila, vám ušetrí hodiny pátrania.

Celý vzor sa volá Skeptical Memory a hovorí, že s vlastným uloženým kontextom máte zaobchádzať ako s neovereným, kým sa nepreukáže opak.

---

## Slide 18 — What to carry forward

Čo si teda z dnešného modulu odniesť? Sú to štyri mechanické nástroje a jeden princíp.

Tie štyri nástroje sú state, eventy, artifakty a scope prefixy. Presne toto vám ADK dáva na to, aby si agent vedel veci pamätať.

A jeden princíp zo vzoru Skeptical Memory znie, že uložený state je nápoveda, nie fakt.

---

## Slide 19 — Up next

Nabudúce otvoríme abstrakciu modelu, s ktorou sme doteraz zaobchádzali ako s čiernou skrinkou. Rovnaký kód agenta pobeží na Claude, GPT, Qwene aj na lokálne hostovanom Ollama modeli, a to všetko z jedného riadku konfigurácie. Preberieme aj konkrétny chyták okolo `ollama_chat` prefixu, ktorý pri nesprávnom použití spôsobuje nekonečné slučky tool callov. Vidíme sa tam.
