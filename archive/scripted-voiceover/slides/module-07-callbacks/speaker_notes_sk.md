# M07 — Speaker notes (SK)

---

## Slide 1 — Title

Callbacky ako middleware. Presne o tom je tento modul. Šesť lifecycle hookov, teda hookov životného cyklu, obaľuje každú invokáciu vášho agenta a všetky sa riadia jedným jednoduchým pravidlom: vráťte `None` a beh pokračuje normálne, alebo vráťte hodnotu a cestu skrátite. Táto jediná konvencia mení mechanizmus hookov na univerzálnu vrstvu ochrany a zachytávania, a práve preto ten istý vzor pokrýva veci ako bezpečnostné mechanizmy, cache, PII redakciu aj testovacie mocky.

---

## Slide 2 — Middleware analogy

V hlave si držte túto analógiu. Callbacky sú pre agentov tým, čím je middleware pre webové handlery. Ak ste niekedy robili s Express middleware, Django middleware alebo plugin hookmi v akomkoľvek frameworku, tento tvar už poznáte. Je to pipeline pre-hookov a post-hookov okolo každého kroku životného cyklu požiadavky. ADK berie rovnakú myšlienku a aplikuje ju na životný cyklus agenta.

---

## Slide 3 — Six hooks

Poďme si prejsť všetkých šesť hookov. Existujú tri udalosti životného cyklu a každú obaľuje dvojica before a after.

Prvou je samotný beh agenta, s hookmi `before_agent_callback` a `after_agent_callback`. Tie sa spúšťajú na hraniciach celej invokácie.

Druhou je volanie modelu, s hookmi `before_model_callback` a `after_model_callback`. Tie sa spúšťajú okolo každej LLM požiadavky.

A treťou je tool call, s hookmi `before_tool_callback` a `after_tool_callback`. Tie sa spúšťajú okolo každého spustenia nástroja.

Nad rámec tejto šestice existujú ešte dva hooky na spracovanie chýb, `on_model_error_callback` a `on_tool_error_callback`, ktoré slúžia na zotavenie z výnimiek. Používajú sa menej často, pretože predvolene sa chyba jednoducho propaguje ďalej.

---

## Slide 4 — Return to override

Celé API callbackov sa dá zhrnúť do jedného pravidla, ktoré volám return-to-override, teda vrátiť hodnotu znamená prepísať. Uvidíte ho na každom príklade v tomto module. Vráťte z callbacku `None` a všetko pokračuje normálne. Vráťte hodnotu a cesta sa skráti. Nasledujúci slide rozoberá, prečo táto jediná konvencia zvládne tak veľa práce.

---

## Slide 5 — The entire API on one slide

Na slide vidíte celé API callbackov. Je to funkcia, ktorá dostane kontext a niekoľko argumentov špecifických pre daný hook. Vo vnútri pozorujete, logujete alebo validujete. A na konci sa rozhodnete.

`return None` znamená, že len pozorujete a skutočné volanie má normálne prebehnúť.

`return` s hodnotou znamená, že skutočné volanie sa preskočí a použije sa to, čo ste vrátili.

To je všetko. Rovnaký vzor platí naprieč všetkými šiestimi hookmi. Jediné, čo sa mení, je typ hodnoty, ktorú jednotlivé hooky akceptujú ako náhradu.

---

## Slide 6 — Demo 1: before_model_callback for blocklist

Poďme na prvé demo. Pomocou `before_model_callback` postavíme bezpečnostný mechanizmus s blocklistom, a to len v piatich riadkoch kódu. Zostava vyzerá triviálne, ale keď ju uvidíte bežať, dôsledky siahajú dosť ďaleko.

---

## Slide 7 — Five lines of safety gate

Na slide máme ten blocklistový bezpečnostný mechanizmus v kóde. Hore je zoznam zakázaných slov, pod ním callback funkcia, ktorá porovná poslednú správu používateľa so zoznamom, a keď nájde zhodu, vráti pripravenú odpoveď ako `LlmResponse`. Výsledkom je, že LLM sa vôbec nezavolá.

Dva detaily stoja za pozornosť. Po prvé, zoznam `llm_request.contents` obsahuje celú históriu chatu a posledný ťah je jeho poslednou položkou. Po druhé, vrátená hodnota je riadny objekt `LlmResponse` s obsahom, ktorý nesie rolu modelu. Presne to ADK očakáva, keď cestu skrátite.

---

### Notebook break — The blocklist in action

[Prepnite obrazovku na notebook.]

Poďme to spustiť. Cez toho istého agenta pošlem dva prompty. Prvý je neškodná otázka o fotosyntéze. [Spustite bunku.] Callback prebehne, nevidí žiadne zakázané slová, vráti `None` a LLM vyprodukuje normálnu odpoveď. Teraz druhý prompt, ktorý obsahuje slovo „password“. [Spustite ďalšiu bunku.] Callback zaberie, všimne si zakázané slovo a vráti svoju pripravenú `LlmResponse`. Pozrite sa na prúd eventov: nie sú v ňom vôbec žiadne eventy uvažovania modelu. LLM sa nikdy nezavolalo.

[Prepnite späť na prezentáciu.]

---

## Slide 8 — On the blocked run, the LLM was never called

Tu je skutočná pointa toho, čo ste práve videli v deme. Pri zablokovanom behu sa LLM vôbec nezavolalo. To znamená nula účtovaných tokenov a garantované odmietnutie, ktoré nezávisí od dobrého správania modelu.

Porovnajte to s mäkkou ochranou, napríklad inštrukciou, ktorá hovorí „odmietni sa baviť o heslách“. Inštrukcia je v skutočnosti len zdvorilá prosba, ktorú si model môže vyložiť nesprávne alebo ju niekto obíde jailbreakom. Kontrola na úrovni kódu v callbacku je naproti tomu múr. Nedá sa obísť ničím, čo používateľ napíše, pretože text sa k modelu vôbec nedostane.

Toto je najdôležitejší dôvod, prečo sa callbacky učiť. Sú spôsobom, ako presadiť bezpečnosť na úrovni frameworku, a nie na úrovni promptu, kde sa s ňou dá polemizovať.

---

## Slide 9 — Demo 2: after_tool_callback for PII redaction

Prejdime na druhé demo, `after_tool_callback` aplikovaný na PII redakciu. Ide o rovnaký vzor s iným lifecycle hookom a úplne iným produkčným prípadom použitia.

---

## Slide 10 — Redact sensitive fields

Slide ukazuje redakčný callback v kóde. Funkcia sa volá `redact_pii` a hneď nad ňou máme množinu názvov citlivých polí: plat, SSN a adresa bydliska. To sú polia, ktoré model nikdy nemá vidieť.

Samotná funkcia robí niečo jednoduché. Beží po tom, čo nástroj vrátil výsledok, ale skôr, než sa naň pozrie model. Keď je odpoveď slovník, funkcia si spraví kópiu, hodnoty citlivých kľúčov nahradí reťazcom `[REDACTED]` a odovzdá ďalej vyčistenú verziu. ADK potom túto vyčistenú verziu použije ako tool response, ktorý model naozaj uvidí, zatiaľ čo pôvodná návratová hodnota funkcie nástroja ostáva nedotknutá.

Vo vašom vlastnom kóde bude množinou citlivých polí čokoľvek, čo nechcete, aby uniklo, napríklad čísla kariet zákazníkov, SSN zamestnancov alebo interné ID. Tvar funkcie ostáva rovnaký.

---

### Notebook break — PII redaction in action

[Prepnite obrazovku na notebook.]

HR agent v notebooku je nastavený tak, aby vyhľadal zamestnankyňu menom Alice. [Spustite bunku.] Pozrite sa na tool-response event vo výstupe. Funkcia nástroja vrátila Alicin kompletný záznam, vrátane emailu, oddelenia, platu, SSN a adresy bydliska. No kým sa odpoveď dostala k modelu, plat, SSN aj adresa bydliska sú označené ako `[REDACTED]`. Callback zachytil výstup nástroja na spiatočnej ceste, skopíroval ho a citlivé polia z neho odstránil. Model vidí len bezpečnú verziu a jeho finálna odpoveď je primerane zdržanlivá.

[Prepnite späť na prezentáciu.]

---

## Slide 11 — Why this matters

Kľúčové pozorovanie z toho dema znie takto. Samotná funkcia nástroja vrátila kompletný záznam, čo znamená, že váš Python kód, vaše audit logy aj zápisy do databázy videli skutočné hodnoty. Model však videl redigovanú verziu.

A presne v tom je produkčná hodnota. Blast radius, teda rozsah dopadu úniku PII, obmedzujete na vrstve callbacku, nie na vrstve funkcie nástroja. Iné systémy, ktoré kompletné dáta legitímne potrebujú, ako váš fakturačný pipeline alebo HR databáza, môžu funkciu nástroja naďalej volať priamo bez callbacku a dostanú skutočné hodnoty.

---

## Slide 12 — Demo 3: before_tool_callback for test mocks

A teraz tretie demo, `before_tool_callback` aplikovaný na mocking, teda na napodobnenie drahých alebo externých nástrojov v testoch.

---

## Slide 13 — Short-circuit expensive tools

Pozrite sa na kód na slide. Toto je vzor mockovania v praxi. Hore je slovník mock odpovedí kľúčovaný tickerom a pod ním callback, ktorý sa spustí skôr, než nástroj zbehne. Callback skontroluje, či sa volá nástroj `fetch_stock_price` a či má daný ticker mock záznam. Ak áno, vráti mock a skutočný nástroj sa vôbec nespustí. Ak nie, vráti `None` a skutočný nástroj zbehne normálne.

---

### Notebook break — Mocking in action

[Prepnite obrazovku na notebook.]

Ukážem vám tento vzor v akcii. Agent má nástroj `fetch_stock_price`, ktorý by normálne volal skutočné API, a callback je zapojený s malým slovníkom mock cien. Najprv sa spýtam na cenu AAPL, ktorá mock záznam má. [Spustite bunku.] Sledujte prúd eventov. Callback sa spustí pred nástrojom, vidí, že AAPL je v mock slovníku, a skráti cestu mockom. Skutočné API volanie sa nikdy nevykonalo; keby áno, videli by ste vypísaný riadok `REAL`, a tam nič také nie je. Teraz sa spýtam na ticker, ktorý v mockoch nie je. [Spustite ďalšiu bunku.] Tentoraz callback vráti `None` a spustí sa skutočný nástroj.

[Prepnite späť na prezentáciu.]

---

## Slide 14 — Production win

Produkčná hodnota tohto vzoru sa zmestí na jeden slide. Dostanete rovnaký kód agenta a testy, ktoré nevolajú skutočné API. V testoch callback zapojíte a v produkcii ho vynecháte. Nepotrebujete samostatné testovacie dvojníky ani kódové vetvy určené len pre testy vo vašom agentovi. Callback je testovacie rozhranie.

Presne takto spravíte kód agenta unit-testovateľným. A rovnako tak budujete odolnosť. Ak skutočné API vypadne, `before_tool_callback` môže vrátiť cached fallback namiesto toho, aby celá požiadavka zlyhala.

---

## Slide 15 — Six hooks reference

Pozrime sa na všetkých šesť hookov spolu s ich typickými prípadmi použitia, aby ste mali jednu referenčnú kartu, ktorú si udržíte v hlave.

Hooky na úrovni agenta sa používajú najmenej. Before-agent hook slúži na prípravu pred štartom a after-agent hook na logovanie finálneho výstupu.

Hooky na úrovni modelu sú miestom, kde žijú bezpečnostné mechanizmy, cachovanie a kontroly na prompt injection.

A hooky na úrovni nástrojov sú miestom pre mocking, PII redakciu a validáciu argumentov.

Zapamätajte si prinajmenšom tie tri „before“ hooky. Práve po nich siahate, keď chcete niečomu skrátiť cestu.

---

## Slide 16 — Callbacks vs alternatives

Kedy teda siahnuť po callbackoch a kedy po iných mechanizmoch? Do životného cyklu agenta sa dá zasiahnuť v podstate štyrmi spôsobmi a každý má svoj prípad použitia.

Prvým je samotná inštrukcia, teda system prompt, ktorá sa hodí na mäkké preferencie a štýl. Pokrýva správanie jedného agenta na úrovni modelu.

Druhým je kód funkcie nástroja, ktorý je správnym miestom pre ochranné funkcie pri nevratných operáciách. Pokrýva bezpečnosť jedného nástroja.

Tretím sú callbacky, téma tohto modulu. Používajte ich na prierezové záležitosti naprieč celým životným cyklom jedného agenta, ako sú bezpečnostné mechanizmy, PII redakcia a cachovanie.

A štvrtým sú pluginy, ktoré sú novšie, širšie a aplikujú sa na každého agenta v runneri. Pluginy sú pre org-wide pravidlá, teda pravidlá platné naprieč celou organizáciou, a pre audit logging.

Základné pravidlo znie takto. Callbacky používajte na logiku špecifickú pre jedného agenta a pluginy na pravidlá platné pre celú aplikáciu. Ak musí to isté pravidlo zabrať na každom agentovi vo vašej aplikácii, siahnite po plugine. Ak je špecifické pre jedného agenta, správnym nástrojom sú callbacky.

Pluginy dnes necháme bokom; vrátime sa k nim neskôr v kurze, keď sa budeme venovať produkčným nasadeniam.

---

## Slide 17 — Observability gotcha

Než uzavrieme, je tu jedna reálna observability gotcha, teda zákernosť, ktorú treba pomenovať, aby vás neprekvapila. Vykonanie callbacku sa automaticky neobjavuje v OpenTelemetry traces ADK, a overili sme to až po release 2.4 vrátane. Ak ste na novšej verzii, skontrolujte release notes, pretože toto sa môže zmeniť.

Konkrétne, ak na sledovanie behov používate niečo ako Cloud Trace, Langfuse alebo Arize, uvidíte LLM volania, tool cally a state delty. Neuvidíte však žiadny span so správou, že `before_model_callback` prebehol a vrátil `None`.

Práve preto, ak sa na callbacky spoliehate pri rozhodnutiach o pravidlách a potrebujete, aby ich vykonanie bolo v produkcii pozorovateľné, budete si callbacky musieť inštrumentovať ručne. Pomôžu print príkazy, riadky v logoch alebo manuálne spany cez OpenTelemetry API. Je to zdokumentovaná medzera; priznáva ju aj samotný ADK blog od Googlu.

---

## Slide 18 — What to carry forward

Čo by ste si teda z dneška mali odniesť? Na troch veciach naozaj záleží.

Prvou je šestica hookov samotná a jediné pravidlo, ktoré ich všetky riadi: vráťte `None` a beh prejde ďalej, alebo vráťte hodnotu a cestu skrátite. To je celé API a budete ho používať zakaždým rovnako.

Druhou je zistenie, že ten istý vzor pokrýva veľmi rozdielne produkčné potreby. Bezpečnostné mechanizmy, PII redakcia, testovacie mocky aj cache používajú úplne rovnakú signatúru callbacku, len v inom bode životného cyklu. Keď napíšete jeden, viete napísať aj ostatné.

A treťou je dôvod, prečo po callbackoch vôbec siahať. Sú spôsobom, ako presadzovať pravidlá v kóde a nie v promptoch. S inštrukciou sa dá polemizovať, s callbackom nie. Preto sú vaším predvoleným nástrojom na všetko, čo sa musí správať spoľahlivo pod nepriateľským vstupom alebo produkčnou záťažou.

---

## Slide 19 — Up next

Nabudúce nás čaká pamäť. Celú vendor-agnostickú časť kurzu sme doteraz bežali na in-memory session state a v nasledujúcom module dostanú sessions skutočnú persistenciu. Prepneme na `DatabaseSessionService` postavenú nad SQLite, predstavíme si nástroj `load_memory` a `MemoryService` pre explicitnú dlhodobú pamäť a s väčšou hĺbkou sa vrátime k vzoru Skeptical Memory, ktorý sme už stretli. Vidíme sa tam.
