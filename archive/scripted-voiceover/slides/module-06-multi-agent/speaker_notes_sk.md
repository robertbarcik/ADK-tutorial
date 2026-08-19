# M06 — Speaker notes (SK)

---

## Slide 1 — Title

Vitajte späť. Tento modul je o multi-agent hierarchiách, teda o situácii, keď LLM na vrchole celej zostavy rozhoduje, ktorý agent má vybaviť požiadavku používateľa. Keď o tom, ktorý špecialista pobeží, rozhoduje vstup používateľa, nechcete workflow agenta. Chcete, aby routoval LLM. ADK má presne na toto dva vzory. Na povrchu vyzerajú podobne, ale správajú sa veľmi rozdielne, a dnes si ich rozoberieme.

---

## Slide 2 — Three ways to combine agents

Spôsoby, ako v ADK skladať agentov dokopy, sú celkovo tri a oplatí sa ich pomenovať hneď na začiatku, aby ste videli, kam dnešná téma zapadá.

Prvý spôsob sú workflow agenti, kde riadiaci tok deklarujete ako pomenovaný primitív, napríklad Sequential, Parallel alebo Loop. Samotný vzor potom spúšťa framework. Siahnite po nich vtedy, keď viete workflow pomenovať.

Druhý spôsob sú sub-agenti, čo je LLM-riadený routing cez transfer. LLM koordinátora vyberie, ktorý špecialista má prevziať prácu, a ADK mu odovzdá riadenie.

Tretí spôsob je AgentTool, tiež LLM-riadený, ale routing prebieha cez volanie funkcie namiesto transferu. Koordinátor vyberie, ktorého špecialistu zavolá, špecialista pobeží a koordinátor zostáva pánom konverzácie.

Dnes sa sústredíme na tie dva LLM-riadené vzory, pekne vedľa seba, pretože na prvý pohľad vyzerajú podobne a ľudia si ich pletú.

---

## Slide 3 — The one question

Celý modul sa dá zhustiť do jednej otázky a vidíte ju na slide. Keď špecialista dokončí svoju prácu, kto má konverzáciu na starosti? Ak špecialista, chcete `sub_agents`. Ak koordinátor, chcete AgentTool. To je celé rozhodnutie a všetko ostatné je už len mechanika.

---

## Slide 4 — sub_agents: the org-chart transfer

Začnime prvým vzorom, prístupom cez `sub_agents`, ktorý vnímam ako org-chart transfer, teda presmerovanie podľa organizačnej štruktúry. Myšlienka je, že koordinátor odovzdá otázku používateľa celú jednému zo svojich špecialistov, podobne ako manažér prepošle e-mail tomu, kto má v skutočnosti odpovedať. Nasledujúce slidy rozoberajú, ako je to zapojené a ako to vyzerá v kóde.

---

## Slide 5 — How sub_agents works

Prejdime si mechaniku. Koordinátorovi dáte zoznam `sub_agents=`, ADK to rozpozná a automaticky mu vloží built-in tool menom `transfer_to_agent`. Nič neregistrujete, jednoducho tam je.

Keď si model koordinátora prečíta správu používateľa a usúdi, že sa hodí niektorý špecialista, vydá štruktúrované volanie, niečo ako `transfer_to_agent(agent_name='weather_specialist')`. ADK to volanie zachytí a presmeruje riadenie na pomenované dieťa. Dieťa potom beží, vyprodukuje odpoveď a práve tú odpoveď vidí používateľ.

Po transferi zostáva dieťa v predvolenom nastavení aktívnym agentom po zvyšok session. Takže keď používateľ pošle doplňujúcu otázku, ide špecialistovi, nie späť koordinátorovi. Inými slovami, od toho momentu konverzáciu vlastní špecialista.

Predstavte si to ako org-chart. Koordinátor je manažér, ktorý číta inbox, a špecialista ide na samotné stretnutie.

Jeden detail, na ktorom v produkcii záleží, stojí za zmienku. Pole `description=` dieťaťa je presne to, čo si LLM koordinátora číta, keď rozhoduje, či tam routovať. Popisy preto píšte pre model, nie pre ľudského recenzenta. „Handles greetings“ je v poriadku, „Agent that greets users warmly and makes them feel welcome“ je už len šum.

---

## Slide 6 — sub_agents in code

Na slide máme vzor sub_agents v kóde. Hore sú dvaja špecialisti, každý s menom, popisom, ktorý je v skutočnosti routing schémou, a vlastnou inštrukciou. Dole je koordinátor, ktorý má oboch špecialistov vo svojom zozname `sub_agents=`. Tým to celé končí, žiadny routing kód nepíšete, pretože mechanizmus transferu rieši ADK za vás.

---

### Notebook break — Transfer routing in action

[Prepnite obrazovku na notebook.]

Ukážem vám to v akcii. Koordinátor a jeho dvaja špecialisti sú v notebooku už zapojení. Najprv pošlem pozdrav. [Spustite bunku.] Sledujte event stream. Model koordinátora vydá volanie `transfer_to_agent` s `agent_name='greeter'` a ADK presmeruje. Finálnu odpoveď vyprodukuje greeter a práve tú vidí používateľ. Teraz otázka na počasie. [Spustite ďalšiu bunku.] Rovnaký tvar, iný cieľ routingu: `transfer_to_agent(agent_name='weather_specialist')`. Preberá weather specialist a produkuje odpoveď.

[Prepnite späť na prezentáciu.]

---

## Slide 7 — The event stream

To, čo vidíte na slide, je ten istý event stream, zachytený ako statická referencia. Koordinátor vydal `transfer_to_agent` s `agent_name='weather_specialist'`, ADK presmerovalo a finálnu odpoveď vyprodukoval weather specialist.

Kľúčové je všimnúť si autora tej finálnej odpovede. Je ním špecialista, nie koordinátor. A presne to prezrádza, že ide o transfer pattern.

---

## Slide 8 — AgentTool: the consultant pattern

Prejdime k druhému vzoru, prístupu cez AgentTool, známemu aj ako consultant pattern, teda vzor konzultanta. Ide o tú istú myšlienku LLM-riadeného routingu, ale zapojenie je iné a výsledné správanie tiež. Nasledujúce slidy rozoberajú, ako funguje a ako vyzerá v kóde.

---

## Slide 9 — How AgentTool works

Rovnaký tím, len iné zapojenie. Namiesto toho, aby ste špecialistov dali do `sub_agents=`, zabalíte každého do `AgentTool(agent=...)` a vložíte ich do zoznamu `tools=` koordinátora.

Pre LLM koordinátora teraz špecialisti vyzerajú ako nástroje. Nijako sa nelíšia od FunctionToolu, OpenAPI nástroja alebo MCP nástroja. Keď sa koordinátor rozhodne špecialistu použiť, vydá bežné volanie funkcie, teda ten istý mechanizmus, ktorý pri ostatných typoch nástrojov spúšťa `get_weather` alebo `search_tickets`.

ADK potom spustí špecialistu ako čerstvé LLM volanie. Špecialista vyprodukuje svoj výstup a ten sa vráti koordinátorovi ako tool-response event. Koordinátor si ho prečíta a finálnu odpoveď pre používateľa napíše sám.

Špecialista sa teda nikdy nedostane k mikrofónu. Odpovie na štruktúrovanú otázku, vráti výsledok a koordinátor hovorí v jeho mene.

---

## Slide 10 — AgentTool in code

Slide ukazuje tých istých dvoch špecialistov ako predtým, teraz však zabalených v AgentTool a umiestnených v zozname `tools=` koordinátora, nie v `sub_agents=`. Ten drobný rozdiel jediného slova v konštruktore je v podstate celý rozdiel v správaní oboch vzorov.

---

### Notebook break — Consultant calls in action

[Prepnite obrazovku na notebook.]

Tí istí špecialisti, teraz zabalení ako AgentTool konzultanti v zozname nástrojov koordinátora. Sledujte, ako sa event stream líši od transfer dema. Najprv pozdrav. [Spustite bunku.] Koordinátor vydá tool call, ale tým nástrojom je `greeter`, teda špecialista. Špecialista vráti svoj výstup ako tool-response event. A potom finálnu odpoveď používateľovi vyprodukuje koordinátor, nie špecialista. Teraz otázka na počasie. [Spustite ďalšiu bunku.] Rovnaký tvar: koordinátor zavolá `weather_specialist` ako nástroj, dostane odpoveď a finálnu odpoveď pre používateľa napíše sám.

[Prepnite späť na prezentáciu.]

---

## Slide 11 — The event stream: note the author

Na slide je event stream z consultant patternu, rozložený ako referencia. Koordinátor zavolal `weather_specialist` ako nástroj. Späť prišiel tool-response event s výsledkom. A finálnu odpoveď používateľovi potom vyprodukoval koordinátor, nie špecialista.

Presne takto vyzerá vzor konzultanta v akcii. Špecialista odpovedal na konkrétnu otázku a ustúpil, zatiaľ čo rozhovor s používateľom mal celý čas na starosti koordinátor.

---

## Slide 12 — The tell-tale sign

Tu je na jednom slide tell-tale sign, teda rozpoznávací znak oboch vzorov. Pozrite sa na autora finálnej odpovede.

Ak je autorom špecialista, pozeráte sa na transfer, čiže na vzor sub_agents.

Ak je autorom koordinátor, pozeráte sa na konzultantské volanie, čiže na vzor AgentTool.

To je celá diagnostika. Vypíšte si event stream, prečítajte posledného autora a viete, ktorý vzor je v hre.

---

## Slide 13 — When to pick which

Kedy teda siahnuť po ktorom? Dám vám štyri ukazovatele pre každú stranu.

Sub_agents, teda transfer pattern, použite vtedy, keď má dialóg vlastniť špecialista. Keď špecialista môže s používateľom prejsť viacero kôl, kým odovzdá slovo späť. Keď zmena témy znamená, že špecialista je naozaj tým správnym partnerom pre celú tému. A keď chcete, aby mal používateľ pocit, že hovorí so špecialistom.

AgentTool, teda consultant pattern, použite vtedy, keď špecialista odpovie na jednu otázku a ustúpi. Keď má špecialista čistý vstupno-výstupný kontrakt. Keď koordinátor potrebuje výstup špecialistu skladať s ďalšími zdrojmi, napríklad s viacerými nástrojmi alebo inými špecialistami. A keď chcete, aby mal používateľ pocit, že hovorí s jedným asistentom, ktorý má špecialistov len v zákulisí.

---

## Slide 14 — Concrete examples

Ukotvime tie pravidlá dvoma konkrétnymi príkladmi.

Najprv scenár pre sub_agents. Predstavte si IT support desk so špecialistom na fakturáciu a špecialistom na hardvér. Používateľ napíše „my laptop won't boot“. Koordinátor routuje na hardvér. Počas nasledujúcich piatich kôl session prevedie hardvérový špecialista používateľa diagnostikou, od napájania cez káble a BIOS až po poradie bootovania. To je dlhší rozhovor, do ktorého koordinátor nemá čo vstupovať. Preto sa transfer spraví raz a špecialista si vybaví celú tému.

Teraz scenár pre AgentTool. Predstavte si kódovacieho asistenta, ktorého orchestrátor obaľuje špecialistu na analýzu kódu, špecialistu na vyhľadávanie v dokumentácii a špecialistu na spúšťanie testov. Používateľ sa spýta „why is my test failing?“. Orchestrátor usúdi, že relevantní sú všetci traja špecialisti, zavolá všetkých troch v jednom kole, prečíta si tri tool response a syntetizuje jednu odpoveď. Každý špecialista prispeje jednou štruktúrovanou odpoveďou a kompozíciu vlastní orchestrátor.

---

## Slide 15 — Multi-Agent Decomposition

Nasleduje krátka odbočka k publikácii Agentic Design Patterns a jej kapitole osem o multi-agent dekompozícii. Pozrieme sa na trochu teórie o tom, kedy si multi-agent architektúry zarobia na svoju coordination tax, teda daň za koordináciu, a čo je rovnako dôležité, kedy nie.

---

## Slide 16 — The coordination tax

Multi-agent architektúry sú v móde, a zároveň sú drahé. Skôr než úlohu rozložíte na špecialistov, musíte zvážiť coordination tax a tá má tri časti.

Po prvé, LLM volania navyše. Každý transfer a každé AgentTool volanie je ďalšia invokácia modelu. Systém s dvomi špecialistami spraví aspoň dve volania na jedno kolo používateľa, jedno na routing a jedno na vyriešenie. Systém s piatimi špecialistami ich môže spraviť desať aj viac. V produkcii sa to sčíta v latencii aj v nákladoch.

Po druhé, routing chyby. Každé routing rozhodnutie je príležitosť vybrať nesprávneho špecialistu. Čím viac špecialistov máte, tým širšia je plocha, kde sa dá minúť. Popisy musíte navrhnúť tak starostlivo, aby sa LLM koordinátora nikdy nepomýlilo, a keď sa to raz nevyhnutne stane, musí to zachytiť vaše testovanie.

A po tretie, kontextová fragmentácia. Každé dieťa má vlastný system prompt, čo znamená, že informácia, ktorú dáte do inštrukcie koordinátora, sa k deťom automaticky nedostane. Špecialisti niekedy zlyhajú preto, že im chýba kontext, ktorý koordinátor mal. V monolitickom agentovi tento problém jednoducho neexistuje, prompt je len jeden.

---

## Slide 17 — Three tests before you decompose

Publikácia vám dáva tri testy, ktoré si spravte skôr, než sa do dekompozície pustíte.

Prvý je test opätovného použitia. Použije sa niektorý z týchto špecialistov aj inde, iným top-level agentom, v inom produkte alebo iným tímom? Ak áno, dekompozícia dáva zmysel, pretože špecialisti sa stanú znovupoužiteľnými komponentmi. Ak nie, zvážte, či nezostať pri jednom agentovi a len mu nepridať viac nástrojov.

Druhý je test heterogenity modelov. Prospeje každému špecialistovi iný model? Lacné routing rozhodnutia na Haiku a ťažké riešenia na Opuse, takýto mix je možný len vtedy, keď dekomponujete. Ak však všetci vaši špecialisti aj tak používajú rovnaký model, dekompozícia vám prináša menej.

A tretí je test rozsahu inštrukcie. Rastie vám jeden system prompt do nezvládnuteľných rozmerov, povedzme päťsto riadkov s prekrývajúcimi sa pravidlami pre rôzne scenáre? Rozbiť ho na špecialistov s užšími promptami je legitímny spôsob, ako zredukovať každý prompt na jeho hlavnú úlohu. Ak má však váš jednoagentový prompt len tridsať riadkov, nerozdeľujte ho len preto, že sa to dá.

---

## Slide 18 — The default

Čo teda robiť, keď neprejde ani jeden z tých troch testov? Predvolená voľba je zostať pri jednom agentovi s nástrojmi. Jeden dobre napísaný agent s ôsmimi nástrojmi je takmer vždy jednoduchší, lacnejší a rýchlejší než architektúra koordinátora a špecialistov, ktorá robí tú istú prácu. Multi-agent je niekedy správna odpoveď, len nie je správnou odpoveďou automaticky.

---

## Slide 19 — Up next

Nabudúce prídu na rad callbacky ako middleware. Šesť lifecycle hookov obaľuje každú invokáciu: `before_agent`, `after_agent`, `before_model`, `after_model`, `before_tool` a `after_tool`. Keď vrátite `None`, všetko pokračuje normálne. Keď vrátite objekt odpovede, LLM alebo nástroj úplne obídete. Predstavte si Django middleware, Express middleware alebo plugin hooky, ale pre agentov. Demo, kde blocklist funguje ako ochranná funkcia, je malé, vizuálne a je to najčistejší príklad bezpečnosti na úrovni kódu v celom kurze. Vidíme sa tam.
