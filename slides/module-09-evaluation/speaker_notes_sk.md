# M09 — Speaker notes (SK)

---

## Slide 1 — Title

Evaluácia. To je téma tohto modulu a je to prirodzený ďalší krok teraz, keď už vieme stavať agentov, ktorí naozaj fungujú. Prejdeme si dve vstavané evaluačné metriky ADK, povieme si, prečo je jedna z nich jednoznačná výhra a druhá väčšinou slabá, a ukážeme si každodenný workflow, ktorým regresie vo vašich agentoch zachytíte skôr, než sa dostanú k zákazníkom.

---

## Slide 2 — Up to now / This module

Rámec dnešnej témy vidíte na slide. Na otázku, či agent funguje, sme doteraz odpovedali pohľadom na vypísaný výstup, presne tak, ako by ste to robili pri prototypovaní. V tomto module to nahradíme testami, ktoré bežia automaticky, pri každej zmene, a hlásia pass alebo fail voči pomenovaným kritériám.

---

## Slide 3 — Two built-in metrics

ADK prináša rovno v základe dve vstavané evaluačné metriky a každá sedí na opačnom konci toho, čo by ste chceli kontrolovať.

Prvá je `tool_trajectory_avg_score` a pýta sa, či agent zavolal správne nástroje, v správnom poradí a so správnymi argumentmi. Škála ide od nuly po jednotku a východiskový prah je jedna celá nula, čo znamená presnú zhodu na každom tool calle, inak test padne.

Druhá je `response_match_score` a pýta sa, ako blízko je skutočná finálna odpoveď agenta k tej očakávanej. Škála je opäť od nuly po jednotku, počíta sa ako ROUGE-1 unigram overlap a východiskový prah je nula celá osem.

Naozaj novátorská je tá trajectory metrika. Väčšina eval frameworkov na trhu skóruje iba výstupy, teda pýta sa, či finálna odpoveď agenta vyzerá správne. ADK pridáva ako rovnocennú informáciu aj to, ako sa k nej agent dostal. A to pri agentoch postavených na nástrojoch presne zodpovedá realite.

---

## Slide 4 — Why trajectory matters

Prečo teda na trajektórii tak veľmi záleží? Jadro pointy na slide je toto. Správna odpoveď dosiahnutá nesprávnym uvažovaním je bug, ktorý len čaká na svoju chvíľu. Ak váš agent dnes dal správnu odpoveď tak, že zavolal nesprávny nástroj alebo preskočil povinný overovací krok, zajtra na mierne odlišnom vstupe zlyhá. A to zlyhanie bude mätúce, pretože predchádzajúca správna odpoveď vás oklamala a mysleli ste si, že agent funguje.

Presne toto trajectory testovanie zachytáva. Zafixuje cestu uvažovania, nielen výstup. Takže ak agent prestane používať nástroj, ktorý ste očakávali, uvidíte to pri najbližšom CI behu, a nie až po sťažnosti zákazníka.

---

## Slide 5 — The eval loop

Poďme si prejsť, ako vyzerá každodenný workflow. Sú to v podstate len tri príkazy, ktoré do seba zapadajú do tesnej slučky spätnej väzby, a túto slučku budete točiť počas toho, ako na agentovi iterujete.

Najprv si lokálne spustíte `adk web` a s agentom sa porozprávate. Keď agent urobí niečo dobré, či už správne odpovie, zavolá správne nástroje, alebo zvládne hraničný prípad, kliknete na tlačidlo „Save as eval“. To konverzáciu exportuje ako `.test.json` súbor priamo vedľa kódu agenta.

Potom spustíte `adk eval` nasmerovaný na priečinok agenta a na eval súbor. Prebehnú všetky testovacie prípady, oskórujú sa voči prahom a pri každom sa nahlási pass alebo fail.

Nakoniec sa vrátite a agenta doladíte. Možno zmeníte inštrukciu, pridáte nový nástroj alebo prehodíte model. Potom znova spustíte `adk eval`, aby ste videli, či zmena pomohla, a celý cyklus zopakujete.

Slučka je dosť rýchla na to, aby ste ju používali už pri prototypovaní, takže si evalset budujte priebežne, ako iterujete. Vždy keď agent zvládne niečo záludné, uložte si tú konverzáciu ako testovací prípad. O pár týždňov budete mať desiatky takýchto prípadov, ktoré vás potichu chránia pred regresiami.

---

## Slide 6 — A minimal test.json

Ako testovací súbor naozaj vyzerá, vidíte na slide. Každý prípad je konverzácia a v každom ťahu deklarujete tri veci. Prvá je, čo hovorí používateľ. Druhá je, čo má agent nakoniec odpovedať. A tretia je, ktoré nástroje má agent cestou zavolať.

Tieto súbory si môžete písať ručne, alebo ich ukladať z vývojárskeho UI. Na jednorazový test je ručné písanie v poriadku. Pri skutočnom projekte ale vždy ukladajte z UI. Zachytí to presnú štruktúru eventov, akú ADK očakáva, vrátane vecí ako invocation ID a tvary obsahu odpovedí, ktoré by ste si inak museli naštudovať zo schémy.

---

### Notebook break — Strict eval reveals the ROUGE-1 weakness

[Prepnite obrazovku na notebook.]

Spustím evaluátor so zámerne prísnym prahom nula celá deväťdesiatpäť na response match. Očakávaná odpoveď je jedna formulácia počasia, zatiaľ čo skutočná odpoveď agenta je mierne odlišná formulácia toho istého faktu. [Spustite bunku.] Sledujte výstup. Trajectory skóre sa vráti ako dokonalá jedna celá nula, takže štrukturálne agent urobil správnu vec. Ale response match skóre pristane na nula celá osemdesiatsedem, oproti prahu nula celá deväťdesiatpäť. Test padne, hoci človek, ktorý si tie dve vety prečíta, by ich označil za ekvivalentné.

[Prepnite späť na prezentáciu.]

---

## Slide 7 — The failure tells a story

Čo nám ten beh vlastne ukázal? Prejdime si čísla, ktoré vidíte na slide.

Očakávaná odpoveď bola „The weather in Prague is cloudy and 14 degrees Celsius.“ Skutočná odpoveď agenta bola „The weather in Prague is cloudy, and the temperature is 14 degrees Celsius.“ Response match skóre vyšlo nula celá osemdesiatsedem oproti prahu nula celá deväťdesiatpäť, takže test padol.

Obe vety nesú tú istú informáciu, len mierne inými slovami. Prvá hovorí „cloudy and 14 degrees“ a druhá „cloudy, and the temperature is 14 degrees“. Keby ste ich prečítali nahlas človeku, ohodnotil by ich ako ekvivalentné. ROUGE-1 ich naproti tomu skóruje na nula celá osemdesiatsedem.

A všimnite si aj druhú polovicu obrazu. Trajectory skóre sa vrátilo ako čistá jedna celá nula, čo znamená, že štrukturálne agent urobil správnu vec. Zlyhanie je tu čisto o formulácii.

---

## Slide 8 — The honest summary

Dovoľte mi úprimné zhrnutie toho, čo sme práve videli. Trajectory testovanie je skutočne užitočné a mali by ste ho spúšťať pri každej zmene. ROUGE-1 porovnávanie odpovedí je naproti tomu slabá metrika a v praxi si na jej používanie budete musieť dávať pozor.

ROUGE-1 trestá legitímnu štylistickú variáciu. Ako hrubý sanity check, teda či výstup obsahoval aspoň časť očakávaných slov, je v poriadku. Ale naozaj to nie je spoľahlivý ukazovateľ správnosti, čo znamená, že pri produkčnej evaluácii sa naň spoliehať nemôžete.

---

## Slide 9 — Adjust the thresholds

Čo teda v praxi naozaj robiť? Prvý krok je prepísať východiskové prahy, čo urobíte tak, že vedľa testovacieho súboru položíte súbor `test_config.json`. Toto by som vám odporučil doň dať.

Pri trajektórii zostaňte prísni. Nastavte jedna celá nula pre presnú zhodu na tool calloch, pretože chcete okamžite vedieť, keď agent začne robiť niečo iné, než robil doteraz.

Pri response match je pracovné pásmo zhruba nula celá šesť až nula celá sedem pre krátky text. Pod tým prejde testom takmer čokoľvek. Nad tým padne aj legitímna štylistická variácia. A pri dlhom texte, ako sú viacodstavcové zhrnutia alebo vysvetlenia, na `response_match_score` rovno zabudnite, pretože na tú prácu to nie je správny nástroj.

A teraz úprimne. Zníženie prahu nie je žiadna výhra. Je to skôr priznanie, že samotná metrika je na meranie kvality odpovede nesprávny nástroj. A presne preto je skutočný upgrade LLM-as-judge, teda LLM v úlohe sudcu, ktorému sa venuje ďalší slide.

---

## Slide 10 — LLM-as-judge

LLM-as-judge je produkčný vzor na evaluáciu kvality odpovedí a pseudokód na slide načrtáva jeho myšlienku. Pre každý testovací prípad spustíte agenta a zachytíte jeho skutočnú odpoveď. Potom zavoláte druhý LLM a podáte mu pôvodný prompt, očakávanú odpoveď a skutočnú odpoveď. Ten druhý LLM požiadate, aby oskóroval sémantickú správnosť, a naspäť dostanete číslo.

ADK od verzie 1.29 prináša integráciu s Gen AI Evaluation Service, ktorá to za vás urobí rovno v základe, a v čase nahrávania je v public preview. Ak bežíte na Vertex AI, môžete na ňu nasmerovať svoje eval sety a sudcu za vás prevádzkuje Google. Pri self-hosted práci si sudcu zapojíte sami, cez samostatné LiteLLM volanie, s grading rubrikou, teda hodnotiacimi kritériami napísanými priamo v prompte, a so skóre vráteným ako výstup.

Kľúčový posun je tu naozaj v rámcovaní. Trajectory testovanie sa pýta, či agent cestou urobil správne veci. LLM-as-judge sa naproti tomu pýta, či agent vo finálnej odpovedi povedal správnu vec. Obe otázky sú pre správnosť v reálnom svete dôležité a ani jednu z nich nezodpovie ROUGE-1.

---

## Slide 11 — The full picture

Slide skladá dokopy celý obraz toho, ako vyzerá evaluácia produkčnej kvality. Ide o štyri evaluačné vrstvy a kombinujete ich v rôznych kadenciách tak, aby sa navzájom podopierali.

Prvá vrstva je trajectory skóre, ktoré spúšťate pri každom pull requeste. Je rýchle, deterministické a štrukturálne regresie zachytí skoro, skôr než sa dostanú k zákazníkom.

Druhá vrstva je ROUGE-1, používaná ako hrubá regresná kontrola, nie ako skutočné meranie kvality. Nezáleží tu na absolútnom čísle, ale na tom, ako sa to číslo vyvíja v čase.

Tretia vrstva je LLM-as-judge, ktorý by ste púšťali ako nightly run, nie pri každom PR. Je drahší než prvé dve vrstvy, pretože pridáva druhé LLM volanie na každý testovací prípad, ale zachytí to, čo ROUGE-1 minie. Nasmerujete ho na celý svoj evalset a prezriete si prípady, ktoré označí ako borderline.

A štvrtá vrstva je ľudská kontrola, ktorá sedí na konci pipeline. Tá je nevyhnutná pri prípadoch, na ktorých naozaj záleží, ako sú nové nasadenia agentov, problémy nahlásené zákazníkmi alebo čokoľvek, kde ide o veľa. Necháte človeka pozrieť sa na skutočné odpovede, týždenne alebo pri každom release.

Pointa celého obrazu je, že si z týchto vrstiev nevyberáte iba jednu. Kombinujete ich v správnych kadenciách tak, aby sa navzájom podopierali.

---

## Slide 12 — Production gotcha: read-only filesystems

Skôr než modul uzavrieme, je tu ešte jedna záludnosť, ktorú sa oplatí pomenovať. `adk eval` zapisuje súbory späť do priečinka agentov, pretože si pre eval behy ukladá aktualizované histórie sessions. Takže ak je váš deployment image read-only, čo je v Kubernetes s read-only root filesystémami bežné, eval narazí na PermissionError.

Upstream issue je adk-python číslo 3887.

Riešenie je priamočiare. Buď priečinok agentov počas eval behov namountujete ako writable, teda s právom zápisu, alebo eval spustíte úplne mimo nasadeného image, či už v CI, na vývojárskom stroji, alebo v samostatnej eval pipeline. Kód agenta je úplne rovnaký, líši sa len runtime prostredie. Pri práci v triede to nič neblokuje, ale stáva sa to skutočnou starosťou, keď eval zapojíte do CI/CD proti kontajneru postavenému tak ako v produkcii.

---

## Slide 13 — What to carry forward

Čo by ste si teda z tohto modulu mali odniesť? Na troch veciach naozaj záleží.

Prvá je testovať trajektóriu prísne. To je metrika s vysokou hodnotou, ktorú vám ADK dáva tak čisto ako nikto iný, takže ju používajte.

Druhá je testovať kvalitu odpovedí cez LLM-as-judge, nie cez ROUGE-1, pri akejkoľvek skutočnej práci. Pseudokódový vzor spred pár slidov je základ a ak idete cestou Vertexu, integrácia v ADK vám ho zabalí hotový.

A tretia je neveriť ROUGE-1 nad úroveň sanity checku. Ako nenáročný regresný signál je užitočný. Nie je to meranie správnosti, a ak sa budete jeho číslom riadiť, akoby ním bolo, zavedie vás.

---

## Slide 14 — Up next

Nabudúce nás čaká nasadenie. Prejdeme si `adk deploy cloud_run` ako príbeh jedného príkazu, obyčajný Dockerfile, ktorý toho istého agenta spustí na ľubovoľnom cloude, a krátky pohľad na Vertex AI Agent Engine ako názorovo vyhranenú spravovanú cestu. Potom sa začne druhá časť kurzu, kde sa pustíme do funkcií špecifických pre Gemini, o ktoré prichádzate, keď zostanete plne vendor-neutrálni. Vidíme sa tam.
