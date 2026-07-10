# M11 — Speaker notes (SK)

---

## Slide 1 — Title

Témou tohto modulu sú grounding a context caching. Obe schopnosti sú špecifické pre Gemini, ani jedna sa neprenesie cez LiteLLM a spolu tvoria prvé dve z funkcií, ktoré druhá časť kurzu odomyká. Výmenou za skutočný lock-in dostávate skutočnú schopnosť a tento modul robí celú túto výmenu konkrétnou.

---

## Slide 2 — Part 1 vs Part 2 framing

Prvá časť kurzu bola vendor-neutrálne ADK, teda ľubovoľný model, ľubovoľný poskytovateľ a všetko bežiace cez LiteLLM. Druhá časť ukazuje, čo navyše odomkne natívne Gemini, teda to, čo vám wrapper poskytnúť nevie. V hre sú tri schopnosti a tento modul pokrýva prvé dve. Ostatné prídu v nasledujúcich moduloch.

---

## Slide 3 — The switch is mechanical

Zmena kódu medzi prvou a druhou časťou je jeden riadok. Namiesto balenia modelu do `LiteLlm(...)` podáte obyčajný reťazec `model="gemini-2.5-flash"`. Všetko ostatné zostáva rovnaké, teda nástroje, sessions, workflow agenti, callbacky, pamäťové služby aj evaluácia. Mení sa iba argument modelu.

---

## Slide 4 — Three unlocks

Pre druhú časť kurzu sú v hre tri schopnosti špecifické pre Gemini a tento modul pokrýva prvé dve.

Prvou je Google Search grounding, teda skutočné citácie so skutočnými URL, o ktoré sa stará grounding infraštruktúra Gemini. Žiadne externé vyhľadávacie API nemusíte spravovať.

Druhou je dlhý kontext v kombinácii s cachingom. Dostanete okná s miliónom tokenov a zľavu sedemdesiatpäť až deväťdesiat percent, keď sa rovnaký obsah opakovane používa naprieč viacerými dopytmi.

Zvyšné schopnosti prídu v nasledujúcich moduloch. Thinking budgety sú ovládač, ktorým určujete, koľko interného uvažovania model spraví, než odpovie. A Live API je obojsmerný hlasový streaming so spracovaním prerušení.

Všetky štyri vyžadujú natívne Gemini a kľúč z Google AI Studia. Ani jedna neprejde cez LiteLLM.

---

## Slide 5 — Grounding header

Prvou schopnosťou je Google Search grounding. Ide o built-in tool, teda vstavaný nástroj, ktorý vracia skutočné citácie.

---

## Slide 6 — Add google_search

`google_search` je funkcia, ktorú importujete z `google.adk.tools` a pridáte do zoznamu `tools=` vášho agenta. Tým je celá integrácia hotová.

Všimnite si, čo tu chýba. Nie je tu žiadny API kľúč na správu, žiadna klientská knižnica na inštaláciu a žiadna funkcia na parsovanie výsledkov. Gemini obsluhuje vyhľadávanie interne, pretože `google_search` je built-in tool, nie funkcia v Pythone, ktorú by spúšťalo ADK. Vy deklarujete zámer a Gemini odvedie prácu.

---

### Notebook break — Grounding in action

[Prepnite obrazovku na notebook.]

Otvorte bunku osem. Agent tam už má `google_search` nastavený v zozname nástrojov. Spustite bunku deväť, ktorá pošle faktickú otázku o hlavnom meste a jeho aktuálnej populácii, a sledujte event stream.

Všimnite si dve veci. Po prvé, pre `google_search` sa neobjaví žiadny tool call event. Je to built-in, takže Gemini obsluhuje volanie interne a neprechádza cez tool-call slučku ADK. Po druhé, pozrite sa na grounding metadáta na konci výstupu. Sú to skutočné URL, z ktorých Gemini pri odpovedi čerpalo. Sedem zdrojov na jednu otázku o populácii.

[Prepnite späť na prezentáciu.]

---

## Slide 7 — What you saw

Na výstupe vidíte, ako vyzerá zdrojovanie na úrovni citácií. Hlavné mesto, údaje o populácii z viacerých zdrojov a sedem grounding zdrojov so skutočnými URL, ktoré smerujú na Wikipédiu, Britannicu a ďalšie stránky.

V produkcii tieto zdroje ukážete svojim používateľom, napríklad riadkom „Zdroj: Wikipedia“ pod každým odsekom. Používateľ vidí, odkiaľ ktoré tvrdenie pochádza, a môže si ho overiť. Presne v tom je rozdiel medzi sebavedomým hádaním AI a odpoveďou s groundingom.

---

## Slide 8 — Cost reality

Skôr než prejdeme na caching, dva chytáky, ktoré súvisia s nákladmi.

Po prvé, vyhľadávanie sa účtuje oddelene od tokenov. Ide zhruba o tridsaťpäť dolárov za tisíc grounded requestov, účtovaných per-request, nie per-token. Pre agenta, ktorý robí sto grounded dopytov denne, je to vyše sto dolárov mesačne. Počítajte s tým v rozpočte.

Po druhé, built-in tooly, teda `google_search`, `BuiltInCodeExecutor` a Vertex AI Search, nemôžu v jednom agentovi existovať spolu s bežnými function toolmi. Gemini API takú požiadavku odmietne. Existujú dve obchádzky. Buď zabalíte každý built-in ako sub-agenta cez `AgentTool`, kde každý sub-agent drží jeden built-in, alebo na ADK 1.16 a novšom `google_search` prijme argument `bypass_multi_tools_limit=True`, ktorý mu dovolí miešať sa s bežnými nástrojmi.

---

## Slide 9 — Caching header

Druhou schopnosťou je dlhý kontext v kombinácii s context cachingom.

---

## Slide 10 — 1M tokens

Gemini 2.5 a novšie modely zvládnu až milión vstupných tokenov, Pro varianty dokonca dva milióny. 500-stranový PDF manuál, celá codebase alebo mesiace emailovej histórie, to všetko sa zmestí do jedného kontextového okna. Schopnosť je skutočná. Ekonomika si ale zaslúži pozornosť.

---

## Slide 11 — Economics problem

Tu sú čísla. Stostranové PDF je zhruba päťdesiattisíc tokenov. Dvadsať otázok nad ním, čo je bežné tempo support agenta nad PDF manuálom, znamená znovu posielať tých päťdesiattisíc tokenov pri každej jednej otázke. Pri štandardnej vstupnej sadzbe Gemini 2.5 Flash je to sedem a pol centa za hodinu na používateľa. Lacné pri jednom používateľovi, drahé vo veľkom.

Context caching to rieši tak, že za dokument zaplatíte raz pri uložení do cache a potom ho znovu používate s výraznou zľavou.

---

## Slide 12 — Two caching flavors

Caching existuje v dvoch podobách.

Implicit caching je automatický a nevyžaduje žiadnu zmenu kódu. Gemini deteguje opakované prefixy a na cachovanú časť uplatní sedemdesiatpäťpercentnú zľavu. Nemáte kontrolu nad tým, čo sa cachuje ani na ako dlho. Pre všetky modely 2.5 je zadarmo.

Explicit caching vyžaduje volanie `client.caches.create` s obsahom a TTL. Dostanete deväťdesiatpercentnú zľavu na cachovanú časť, plnú kontrolu nad tým, čo v cache je a na ako dlho, a k tomu malý poplatok za úložisko za každý cachovaný token a hodinu.

Implicit vyhráva vtedy, keď si nie ste istí, či obsah ešte znovu použijete. Explicit vyhráva vtedy, keď viete, že nad rovnakým obsahom položíte veľa otázok v definovanom časovom okne.

---

## Slide 13 — Explicit caching API

Volanie `client.caches.create` vezme váš obsah a TTL a vráti vám handle na cache. Nasledujúce volania `generate_content` podajú `cached_content=cache.name` a cachovaný obsah sa účtuje so zľavnenou sadzbou.

Dve obmedzenia majte na pamäti. Po prvé, minimálna veľkosť cache je okolo tridsaťdvatisíc tokenov. Pod touto hranicou náklady na úložisko prevýšia úsporu. Po druhé, explicit caching vyžaduje platený tier Gemini API. Free tier má nulovú kvótu na úložisko, takže bunka v notebooku, ktorá to demonštruje, vráti na free kľúči 429 error. Kód je správny, len sa bez plateného účtu nespustí.

---

## Slide 14 — Worked example

Prepočítaný príklad pracuje so sto stranami a dvadsiatimi dopytmi za hodinu. Bez cachingu vás to stojí sedem a pol centa za hodinu. S explicit cachingom asi jeden a tretinu centa, keď spočítate jednorazové vytvorenie cache, zľavnené čítanie pri každom dopyte a hodinu úložiska. To je šesťnásobné zníženie nákladov.

Úspora navyše škáluje. Pri sto dopytoch za hodinu nad rovnakým dokumentom sa rozdiel roztvorí na tridsaťnásobok aj viac.

A kde je bod zvratu? Pod tromi až piatimi dopytmi na dokument za hodinu je implicit caching zadarmo a pokryje väčšinu prínosu. Nad touto hranicou sa explicit oplatí aj so setup kódom navyše.

---

## Slide 15 — Native vs LiteLLM header

Postavme teraz natívne Gemini vedľa modelu zabaleného v LiteLLM. Tento kompromis je skutočný a oplatí sa ho vysloviť nahlas.

---

## Slide 16 — Feature matrix

Feature matrix na slide, teda matica funkcií, sa delí na dva stĺpce. Základný chat a tool cally fungujú oboma cestami. `google_search`, context caching, thinking budgety a Live API sú len natívne. LiteLLM nevie sprístupniť funkcie, ktoré v OpenAI-shaped interface, ktorý obaľuje, jednoducho neexistujú.

Výhodou LiteLLM je výmena modelu na jeden riadok. Na Claude, GPT alebo Qwen prepnete zmenou jedného reťazca. To je vzor vendor-neutrality zo skoršej časti kurzu.

Nejde pritom o dve alternatívy. Natívne Gemini použite vtedy, keď potrebujete funkciu, ktorá cez LiteLLM neprejde. Pre všetko ostatné použite model zabalený v LiteLLM.

---

## Slide 17 — Production pattern

Produkčný vzor je mať oboje.

Bežné dopyty od používateľov idú cez agenta zabaleného v LiteLLM. Je prenosný a má multi-model failover, takže keď má poskytovateľ výpadok, prehodíte model bez toho, aby ste sa dotkli kódu agenta.

Vyhľadávanie, dlhý kontext a hlasové dopyty idú cez natívneho Gemini agenta. Ste síce uzamknutí na Google, no výmenou dostávate grounding, caching a Live API, ktoré vám nikto iný neponúkne.

Skombinujete ich cez `sub_agents` alebo `AgentTool`. Koordinátor smeruje každý dopyt na správneho špecialistu. Architektúra je ten istý multi-agent vzor zo skoršej časti kurzu.

---

## Slide 18 — Next

Nabudúce prídu na rad thinking budgety, ovládací prvok dostupný len na Gemini, ktorým vymieňate latenciu za kvalitu uvažovania. Rovnaká otázka pri minimálnom budgete dostane okamžitú odpoveď, ktorá môže byť nesprávna. Pri maximálnom budgete dostane pomalšiu odpoveď, ktorá je oveľa pravdepodobnejšie správna. V ďalšom module spustíme rovnaký matematický príklad na oboch nastaveniach a rozdiel odmeriame.
