# M08 — Speaker notes (SK)

---

## Slide 1 — Title

Témou tohto modulu je pamäť a prichádza v dvoch podobách, ktoré budeme po celý čas dôsledne oddeľovať. Prvou je persistencia, vďaka ktorej sessions prežijú reštart procesu. Druhou je dlhodobá pamäť, ktorá agentovi umožní prehľadávať minulé konverzácie aj o týždne či mesiace neskôr. Obe si postavíme jednoriadkovými doplnkami k tomu, čo už máte, a na záver sa opäť vrátime k vzoru Skeptical Memory, teda skeptickej pamäti, pretože na dlhých časových horizontoch pamäť zastaráva a konať na základe zastaranej pamäte je drahé.

---

## Slide 2 — The persistence problem

Problém persistencie vidíte na slide. `InMemorySessionService` stráca pri reštarte procesu úplne všetko, takže keď reštartujete svoj Python proces, každá session vašich používateľov je preč. Pre tutoriál je to v poriadku. Pre skutočný produkt to ale znamená, že agent pri každom nasadení zabudne na všetkých.

---

## Slide 3 — Two different time scales

Agenti si potrebujú pamätať na dvoch rôznych časových škálach a hranica medzi nimi je to najdôležitejšie, čo si z tohto modulu treba odniesť správne.

Prvá škála je v rámci jednej konverzácie. To je látka, ktorú sme prebrali pri session state skôr v kurze. Agent sleduje kontext aktuálneho ťahu a state s prefixom `user:` sa prenáša medzi sessions toho istého používateľa v rámci jednej session service.

Druhá škála siaha cez týždne, naprieč nesúvisiacimi sessions. To je práca pre `MemoryService` a nástroj `load_memory`. Agent explicitne prehľadáva archív minulých konverzácií. Toto je územie otázok typu „o čom sme sa rozprávali minulý utorok“.

Základné pravidlo znie takto. Session state rieši dnešnú konverzáciu. MemoryService rieši históriu.

---

## Slide 4 — Part 1: DatabaseSessionService

Začnime prvou časťou modulu, persistenciou cez `DatabaseSessionService`. Cieľ je jednoduchý. Chceme, aby sessions prežili reštart procesu, takže keď svoju službu znova nasadíte, rozbehnuté konverzácie používateľov len tak nezmiznú. Nasledujúce slidy prejdú jednoriadkovú výmenu, ktorá vás tam dostane.

---

## Slide 5 — The swap

Na slide máme tú jednoriadkovú výmenu, bok po boku s in-memory verziou, ktorú sme doteraz používali. Namiesto `InMemorySessionService()` napíšete `DatabaseSessionService(db_url=...)`. Zvyšok kódu ostáva presne rovnaký: rovnakí agenti, rovnaké runnery, rovnaké nástroje, rovnaké callbacky.

Na demá použite SQLite s URL `sqlite+aiosqlite:///app.db`. V skutočnej produkcii by ste mierili na Postgres alebo MySQL cez connection string ako `postgresql+asyncpg://...`. Rozhranie je v oboch prípadoch rovnaké, len si vyberáte backend.

---

## Slide 6 — The async-URL gotcha

Hneď na začiatku stojí za to upozorniť na jednu gotchu. DatabaseSessionService v ADK používa async engine zo SQLAlchemy, čo znamená, že obyčajnú schému `sqlite://` použiť nechcete. Tá siaha po sync driveri a padne s nič nehovoriacou chybou. Namiesto nej explicitne použite `sqlite+aiosqlite://`.

Budete tiež musieť doinštalovať dva balíky, `aiosqlite` ako async driver a `greenlet` ako tranzitívnu závislosť SQLAlchemy. Oba sú ľahké, oba sa inštalujú cez pip. A keď na niektorý zabudnete, chybová hláška vám nepovie, čo s tým.

---

### Notebook break — Write, restart, recall

[Prepnite obrazovku na notebook.]

Ukážem to v akcii. Notebook má pripravené dve inštancie služby, ktoré mieria na ten istý SQLite súbor, ale staviame ich postupne, aby sme medzi nimi vedeli nasimulovať reštart procesu. Najprv vytvorím inštanciu jedna a zapíšem do state hodnotu `user:preference = "terse"`. [Spustite bunku.] Vidíte, že SQLite súbor na disku narástol. Teraz inštanciu jedna zahodím a od nuly postavím inštanciu dva, ktorá mieri na ten istý súbor. [Spustite ďalšiu bunku.] Potom pre toho istého používateľa vytvorím novú session, bez akéhokoľvek počiatočného state. [Spustite poslednú bunku.] Sledujte, čo sa stane. State už obsahuje `user:preference = "terse"`. Inštancia dva ho načítala z disku, presne akoby inštancia jedna nikdy nezmizla.

[Prepnite späť na prezentáciu.]

---

## Slide 7 — Three-step recap

Na slide je pre referenciu rozpísaná trojkroková sekvencia, teda zápis, reštart a načítanie. Funguje to vďaka event sourcingu, ktorého sme sa dotkli skôr v kurze. Aj `output_key=`, aj `tool_context.state[...]` produkujú state-delta eventy, ktoré služba zapisuje do úložiska. Pri `create_session` potom služba prečíta minulý state z úložiska a vráti vám ho pripravený na použitie. Kód agenta sa nemení, mení sa iba persistencia.

---

## Slide 8 — Part 2: MemoryService and load_memory

Prejdime k druhej časti modulu, dlhodobej pamäti s `MemoryService` a nástrojom `load_memory`. Práve toto umožní vášmu agentovi prehľadávať minulé konverzácie o týždne či mesiace neskôr, aj keď sa aktuálna konverzácia na tie minulé sessions nijako neodvoláva. Persistencia drží session nažive, dlhodobá pamäť dáva agentovi schopnosť pamätať si veci naprieč úplne nesúvisiacimi sessions.

---

## Slide 9 — The shape

Dlhodobá pamäť v ADK má štyri kroky. Prejdime si ich.

Po prvé, prebehne konverzácia. Používateľ agentovi niečo povie, napríklad na akom projekte pracuje, akú má preferenciu alebo nejaký fakt o sebe.

Po druhé, session explicitne archivujete do pamäte cez `await memory_service.add_session_to_memory(session)`. Toto je ten zámerný krok. ADK nearchivuje automaticky, vy rozhodujete, kedy sa session stane súčasťou prehľadávateľnej dlhodobej histórie agenta.

Po tretie, v budúcej, nesúvisiacej session má agent nástroj `load_memory`. Je vstavaný, stačí ho importovať z `google.adk.tools` a pridať do zoznamu `tools=` agenta.

A po štvrté, keď sa používateľ spýta na niečo, čo by sa dalo zodpovedať z histórie, agent zavolá `load_memory` s vyhľadávacím dopytom. Pamäťová služba vráti zodpovedajúce útržky, agent si ich prečíta a oprie o ne svoju odpoveď.

V jadre je to teda explicitné vyhľadávanie, nie samovoľné spomínanie. Model rozhoduje, kedy hľadať, a nástroj vráti, čo našiel.

---

## Slide 10 — Two memory services

ADK prináša dve pamäťové služby priamo v balení.

Prvou je `InMemoryMemoryService`. Stojí na obyčajnom slovníku, je perfektná na demá a testy a pri reštarte stráca všetko. Práve tú používa notebook.

Druhou je `VertexAiMemoryBankService`, ktorá je spravovaná a beží len na Google Cloude. Je výrazne sofistikovanejšia. Zo surových sessions extrahuje destilované fakty, deduplikuje ich a časom konsoliduje. To je reálna cesta do produkcie, ak ste sa upísali Vertex AI.

Pre self-hosted produkciu na inom stacku by ste implementovali `BaseMemoryService` nad Postgresom s vector extension, alebo nad svojou existujúcou vyhľadávacou infraštruktúrou. Rozhranie je stabilné, úložisko pod ním je vaše.

---

### Notebook break — Long-term recall in action

[Prepnite obrazovku na notebook.]

Je čas vidieť dlhodobú pamäť v akcii. Notebook prechádza demo v štyroch krokoch. Najprv máme viacťahovú minulú konverzáciu, v ktorej používateľ opisuje svoj Raspberry Pi projekt menom RaspiKitchen, vrátane hardvéru a toho, na čo slúži. [Spustite bunku.] Tá session sa skončí. Potom ju explicitne archivujeme do pamäte cez `add_session_to_memory`. [Spustite ďalšiu bunku.] Teraz otvoríme čerstvú session s úplne novým session ID a spýtame sa „what project am I working on?“. [Spustite poslednú bunku.] Sledujte event stream. Agent zavolá `load_memory` s vyhľadávacím dopytom, dostane späť útržky z minulej konverzácie a vyprodukuje odpoveď opretú o fakty zo session, na ktorej sa nikdy priamo nezúčastnil.

[Prepnite späť na prezentáciu.]

---

## Slide 11 — The event stream

Tu je tá istá sekvencia zachytená ako statická referencia. Tri takty: agent zavolal `load_memory` s vyhľadávacím dopytom, nástroj vrátil `MemoryEntry` s textom z minulej konverzácie a agent vyprodukoval podloženú odpoveď o projekte RaspiKitchen, o Pi 5 s 8GB RAM a o mikrofónovom poli na ESP32.

Dôležité je zvnútorniť si, že tieto fakty NIE SÚ v kontextovom okne aktuálnej konverzácie. Aktuálna session sa práve začala. Minulá session je úplne oddelená. Agent ich vytiahol zámerne, cez `load_memory`.

---

## Slide 12 — Skeptical Memory, revisited

Nasleduje krátka odbočka k vzoru Skeptical Memory. Krátko sme sa s ním stretli skôr v kurze. Teraz, keď máme pamäť siahajúcu cez týždne a mesiace, stojí za to prebrať ho poriadne.

---

## Slide 13 — Memory staleness at long horizons

Prejdime si problém zastarávania v plnej podobe. Pred tromi mesiacmi používateľ agentovi povedal, že pracuje v Anthropicu. Pamäť sa uložila. Dnes agent prehľadá pamäť na dopyt „employer“, nájde Anthropic a oprie o to svoju odpoveď v duchu „Ako zamestnanec Anthropicu...“.

Lenže používateľ mohol medzitým zmeniť prácu. Tá spomienka je presná k dňu, keď sa uložila. K dnešnému dňu presná nie je. Agent, ktorý sebavedomo koná na základe tri mesiace starého faktu, je teda sebavedomo vedľa.

Na dlhých časových horizontoch, či už ide o týždne alebo mesiace, je zastaranosť v skutočnosti východiskový stav, nie výnimka. Väčšina toho, čo platilo pri zápise, platí stále, ale nejaké kritické percento už nie. A váš agent musí počítať s oboma možnosťami.

---

## Slide 14 — Three defensive patterns

Pri práci so zastaranou dlhodobou pamäťou sa oplatí poznať tri obranné vzory.

Prvým je retrieve-and-verify, teda vyhľadaj a over, obzvlášť pri akciách, kde ide o veľa. Skôr než agent pošle email, urobí nákup alebo čokoľvek nevratné, ďalším krokom po `load_memory` by mal byť tool call, ktorý vytiahnutý fakt znova overí. Naprogramovali by ste teda niečo v zmysle „Len si to potvrďme, stále pracujete v Anthropicu?“, a to pred akciou, nie až keď akcia zlyhá.

Druhým vzorom je označovať spomienky recency metadátami, teda metadátami čerstvosti. V praxi to znamená, že popri každom zápise na úrovni `user:` alebo `app:` uložíte dátum a pri vyhľadaní ukážete modelu aj vek spomienky. Keď model vek vidí, tri mesiace starému faktu prirodzene dôveruje menej než čerstvému. Bez neho nemá ako rozoznať rozdiel.

A tretím vzorom je agresívny decay, teda prirodzené zastarávanie, prípadne konsolidácia, pretože pamäť sa časom plní. Staré záznamy môžete nechať vyprchať, po určitom počte dní ich mazať, alebo viacero záznamov konsolidovať do jedného súhrnu. Memory Bank to robí automaticky. Pri `InMemoryMemoryService` si túto politiku implementujete sami.

---

## Slide 15 — The framing

Rámec, ktorý si z tejto odbočky odneste, je na slide. Dlhodobá pamäť je denník, nie cache. Každá vytiahnutá spomienka je tvrdenie zo dňa, keď sa zapísala, nie fakt, ktorý automaticky platí aj dnes. Zaobchádzajte s ňou preto ako s indíciou, ktorú treba overiť, nie ako s ground truth.

---

## Slide 16 — Up next

Nabudúce nás čaká evaluácia. Doteraz sme v kurze na otázku „funguje ten agent?“ odpovedali tak, že sme okom prebehli event stream. Ďalší modul predstaví evaluačný framework ADK. Stretneme `AgentEvaluator` a `EvalSet`, trajectory metriky, ktoré kontrolujú, či agent volal správne nástroje v správnom poradí, aj response-match metriku ROUGE-1, spolu s úprimným varovaním, prečo je ROUGE na skutočnú prácu slabá. A k tomu slučku `adk eval` v CLI: chat, uloženie evalsetu, doladenie promptu, nové spustenie. Vidíme sa tam.
