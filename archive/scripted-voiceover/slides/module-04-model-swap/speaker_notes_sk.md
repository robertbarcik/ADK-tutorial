# M04 — Speaker notes (SK)

---

## Slide 1 — Title

Vitajte vo štvrtom module, ktorý je o výmene modelu jedným riadkom. V tomto module otvoríme abstrakciu modelu, ktorú sme doteraz brali ako čiernu skrinku. Na jeho konci pobeží úplne rovnaký kód agenta na Claude, GPT, Gemini, Qwene aj Llame. Zakaždým sa zmení jeden riadok konfigurácie. Zvyšok agenta, teda inštrukcia, nástroje, session a Runner, sa nemení vôbec.

---

## Slide 2 — So far / This module

Východisko vidíte na slide. Doteraz každé demo používalo ten istý konkrétny model string, teda reťazec, ktorým sa model identifikuje. Tento modul ho otvára. Pozrieme sa, čo ten reťazec v skutočnosti znamená pod kapotou, ku ktorým štyrom ďalším poskytovateľom vás pripojí a kedy má výmena modelu v praxi zmysel.

---

## Slide 3 — What LiteLlm actually is

Vysvetlime si, čo je LiteLlm a prečo existuje. ADK napísal Google a Gemini mu rozumie natívne. Môžete teda podať `model="gemini-2.5-flash"` a jednoducho to funguje, pretože ADK hovorí priamo s SDK od Googlu.

Každý iný model potrebuje translačnú vrstvu a tou vrstvou je LiteLLM. Je to nezávislá open-source knižnica, ktorú udržiava samostatný tím, a sedí medzi vaším kódom a zhruba stovkou poskytovateľov LLM. Požiadavky prichádzajú v tvare OpenAI API. LiteLLM ich preloží do podoby, akú očakáva cieľový poskytovateľ, a odpovede sa vracajú preložené opačným smerom.

`LiteLlm` wrapper v ADK je v skutočnosti len tenký adaptér, ktorý LiteLLM sprístupňuje ako model kompatibilný s ADK. Google tento adaptér napísal, aby nemusel písať vlastný shim pre každého vendora. Výsledok je, že vždy, keď sa objaví nový poskytovateľ LLM, tím LiteLLM pridá podporu a ADK ju zdedí zadarmo.

---

## Slide 4 — Request flow

Na tomto slide vidíte celý round trip jedného volania. Váš agent zostaví požiadavku v tvare OpenAI. Tá narazí na LiteLlm wrapper, ktorý ju podá knižnici LiteLLM. LiteLLM ju potom preloží do tvaru, aký chce cieľový poskytovateľ, či už je to formát Anthropicu, OpenAI, Googlu alebo iný. Požiadavku pošle na OpenRouter, ktorý ju smeruje na skutočného poskytovateľa. Odpoveď sa vracia tou istou rúrou a cestou späť sa znovu prekladá.

Dokopy sú to teda dva preklady na jedno volanie, čo je malá réžia. Háčik je v tom, že preklad je citlivý na verzie. Ak zvýšite verziu `google-adk` nezávisle od `litellm`, tvar tool-call payloadov sa môže rozísť. Wrapper a knižnica sa prestanú zhodovať na tom, ako vyzerá tool call v tvare OpenAI. Presne preto `requirements.txt` pinuje obe verzie spolu. Zvyšujte ich ako pár, nikdy nie jednu samostatne.

---

## Slide 5 — The OpenRouter model-string convention

Tu na slide máme formát OpenRouter model stringu plus referenčnú tabuľku piatich konkrétnych príkladov. Formát je priamočiary, najprv `openrouter`, potom poskytovateľ a potom konkrétny názov modelu. Existuje aj voliteľný `:tier` sufix pre free, beta alebo nitro úrovne, ktorý by ste mali takmer vždy vynechať. Free tiery na OpenRouteri sú agresívne rate-limitované a nespoľahlivé.

Tabuľka je vlastne najužitočnejšia referencia v tomto module. Jeden OpenRouter kľúč vám nahradí päť kľúčov k piatim poskytovateľom. Ceny za token sú do piatich percent od toho, čo by ste platili priamo u každého poskytovateľa, takže za pohodlie konsolidácie neplatíte žiadnu významnú prirážku.

---

### Notebook break — One agent, five providers

[Prepnite obrazovku na notebook.]

Tu v notebooku máme továreň na agentov, jednu funkciu, ktorá vezme model string a vráti LlmAgent. Pod ňou je zoznam piatich model stringov, jeden pre každého poskytovateľa zo slidu: Gemini-Flash-Lite, GPT-4o-mini, Claude-Haiku, Qwen-3 a Llama-3.1. Slučka zavolá továreň raz pre každý reťazec a položí výslednému agentovi rovnakú otázku. [Spustite bunky.] Sledujte, ako sa odpovede posúvajú obrazovkou, model za modelom. Rovnaká otázka. Rovnaká definícia agenta. Päť rôznych odpovedí.

[Prepnite späť na prezentáciu.]

---

## Slide 6 — What to notice in the output

Z toho behu stoja za zmienku tri pozorovania.

Po prvé, odpovede sa líšia štýlom, ale v obsahu sa zbiehajú. Každý model vysvetlí tool calling rozumne a žiadny výrazne nehalucinuje. Na bežnom koncepte je rozdiel v textúre, nie v správnosti. Rozdiely v kvalite sa naozaj ukážu až na ťažkých promptoch.

Po druhé, latencia sa medzi poskytovateľmi líši zhruba trojnásobne. Open-weight modely cez svojich súčasných poskytovateľov bývajú pomalšie než hostované frontier modely, teda špičkové modely veľkých hráčov. Pre agenta intenzívne využívajúceho nástroje, ktorý robí desať volaní na jeden ťah, sa to sčítava a trikrát pomalšie ťahy sa môžu stať nepoužiteľnými. Pri priamočiarom odpovedaní na otázky si to naopak sotva všimnete.

Po tretie, z niektorých modelov presakujú reasoning traces, teda stopy uvažovania. Varianty Qwen a DeepSeek-R1 vypisujú svoj myšlienkový postup, aj keď oň nežiadate. Dá sa to potlačiť špecifickým extra-body parametrom, alebo si jednoducho vyberiete non-reasoning variantu. V produkcii o tom treba vedieť, aby vaši používatelia nevideli chain-of-thought vo svojom UI.

---

## Slide 7 — Local models via Ollama

Nasleduje bonusová časť o lokálnych modeloch cez Ollamu. Ak chcete open-weight modely spúšťať na vlastnom hardvéri, Ollama je najjednoduchšia cesta. Volania vás nestoja nič, nečakáte na žiadne sieťové round tripy a všetko beží plne offline. Jediná vec, ktorú treba trafiť správne, je jeden prefix.

---

## Slide 8 — Setup

Na slide máme celé nastavenie Ollamy odhora nadol. Skladá sa z dvoch kusov, z troch jednorazových shell príkazov, ktoré Ollamu rozbehnú lokálne, a potom z jedného riadku Pythonu, ktorým ju použijete z ADK.

Tri shell príkazy nainštalujú Ollamu, spustia Ollama server, ktorý beží ako lokálne API na porte 11434, a stiahnu model, aký chcete. Qwen 3 je skvelý na tool calling na notebooku so šestnástimi gigabajtmi RAM.

Potom vo svojom ADK kóde vymeníte model string na `LiteLlm(model="ollama_chat/qwen3:8b")` a to je všetko. Ak vaša Ollama beží na neštandardnom porte, nastavte `OLLAMA_API_BASE=http://localhost:11434`, ale väčšine ľudí stačí default.

---

## Slide 9 — The gotcha

Na prefixe pre Ollamu záleží viac než na čomkoľvek inom v tomto module. LiteLLM podporuje pre Ollamu dva prefixy a tie robia úplne odlišné veci.

Prvý je `ollama_chat/qwen3:8b` a práve ten používajte. Ide na chat-completions API Ollamy, ktoré má skutočnú podporu function-callingu. Tool cally fungujú tak, ako čakáte.

Druhý je `ollama/qwen3:8b` a ten nepoužívajte. Ide na staršie completions API Ollamy. Tool cally sa tam vykresľujú ako text, ktorý má model vyprodukovať doslovne. Model zlyhá, skúsi to znova, tool call sa vykreslí nanovo a zlyhá zas, takže skončíte v nekonečnej slučke.

Pasca je v tom, že na obyčajnom prefixe chybu neuvidíte, kým agentovi nedáte nástroje. Bez nástrojov sa oba prefixy správajú identicky. Pokazí sa to prvý raz vtedy, keď pridáte nástroj, a chybová hláška vám nepovie, čo je zle. Toto je mimochodom najčastejšie hlásený problém v repozitári adk-python. Zapamätajte si ten prefix.

---

## Slide 10 — Native vs LiteLLM-wrapped Gemini

Krátke ujasnenie, ktoré sa objavuje často: Gemini sa dá v ADK použiť dvoma spôsobmi.

Prvý je natívny, `model="gemini-2.5-flash"`, obyčajný reťazec bez LiteLlm wrappera. ADK ide priamo cez google-genai SDK. K dispozícii sú všetky funkcie špecifické pre Gemini, vrátane vyhľadávania s groundingom, thinking budgetov, Live API a cachovania dlhého kontextu. Presne toto používa druhá časť kurzu.

Druhý je zabalený v LiteLLM, `LiteLlm(model="openrouter/google/gemini-2.5-flash-lite")`, ktorý ide cez OpenRouter ako požiadavka v tvare OpenAI. Funkcie špecifické pre Gemini tadiaľto nedosiahnete, pretože LiteLLM nevie prekladať funkcie, ktoré v tvare OpenAI neexistujú.

Praktické pravidlo je teda takéto. Zabalené v LiteLLM pre vendor-agnostickú prácu v prvej časti kurzu, natívne pre funkcie špecifické pre Gemini v druhej časti. Vo vendor-agnostických moduloch používame LiteLLM naprieč celým kurzom presne preto, aby váš kód zostal prenosný.

---

## Slide 11 — Prompt priority tiers

Nasleduje krátke odbočenie z publikácie Agentic Design Patterns, konkrétne z piatej kapitoly, o prompt priority tiers, teda úrovniach priority promptu. K výmene modelov to patrí preto, že rôzne modely narábajú s dlhými inštrukciami rôzne a že inštrukcie sa niekedy pod kontextovým tlakom orežú.

---

## Slide 12 — The problem

Problém, ktorý toto odbočenie rieši, vyzerá takto. Keď vymeníte model, inštrukcie, ktoré fungovali na Claude, na GPT niekedy čiastočne zlyhajú. Nie preto, že GPT je horší, ale preto, že modely vážia rôzne časti promptu rôzne. Claude číta všetko až do konca, GPT uprednostňuje najskoršie tokeny a Gemini má vlastný vzorec.

Navyše sa dlhé inštrukcie pod kontextovým tlakom orezávajú. Dlhý system prompt plus dlhé popisy nástrojov plus dlhá história chatu môžu ADK donútiť zahodiť časti toho, čo ste napísali. Ako prvé strácate časti na spodku.

Vzor je preto jednoduchý. Štruktúrujte inštrukciu tak, aby najdôležitejšie časti prežili, a dajte ich na začiatok.

---

## Slide 13 — Three tiers

Prioritný model má tri úrovne.

Prvá úroveň sú invarianty. To sú pravidlá, ktoré agent musí dodržať za každých okolností, ako bezpečnostné brány, tvrdé odmietnutia a formátové obmedzenia. Patria na vrch promptu, krátke a deklaratívne. Napríklad „nikdy neuvádzaj čísla kreditných kariet“, „odmietni finančné poradenstvo“, „vždy odpovedaj v JSONe“.

Druhá úroveň je jadrové správanie. To je hlavný popis práce, teda na čo agent slúži a aké má ciele. Napríklad „pomáhaš inžinierom debugovať zlyhané buildy čítaním logov a navrhovaním opráv“.

Tretia úroveň sú preferencie. To je spôsob, akým agent komunikuje, teda dĺžka, tón, markdown alebo čistý text, odrážky alebo odseky. Má najnižšiu prioritu a pokojne o ňu môžete prísť ako o prvú. Napríklad „pri vymenúvaní uprednostňuj odrážky pred odsekmi“.

Čítané odhora nadol to znamená najprv invarianty, potom účel a nakoniec štýl.

---

## Slide 14 — A priority-tiered instruction

Tu na slide vidíte, ako vyzerá prioritne členená inštrukcia v praxi. Sú to tri sekcie a každá je označená jasnou hlavičkou, ktorá pomáha parsovať štruktúru ľuďom aj modelu.

Invarianty idú prvé, nikdy nespúšťaj kód, nikdy negeneruj prihlasovacie údaje, priznaj nevedomosť namiesto hádania. Potom jadrové správanie, teda popis práce tohto konkrétneho agenta. A preferencie nakoniec, markdown pre bloky kódu, krátka próza a podobné veci.

Ak toto ADK niekedy oreže, pretože sa kontext zaplnil popismi nástrojov a históriou chatu, ako prvé odídu preferencie a potom jadrové správanie. Invarianty prežijú najdlhšie a toto poradie je zámerné.

---

### Notebook break — Try to jailbreak the priority instruction

[Prepnite obrazovku na notebook.]

Tu v notebooku je prioritne členená inštrukcia zapojená do skutočného agenta. Teraz sa ju pokúsim zlomiť. Vypýtam si od agenta AWS prístupový kľúč, čo invarianty na vrchu promptu výslovne zakazujú. [Spustite bunku.] Všimnite si odmietnutie. Model rozparsuje štruktúrovaný prompt, uvidí invariant a odmietne bez ohľadu na to, čo príde v konverzácii neskôr. Spustite rovnakú zostavu proti ktorémukoľvek z piatich poskytovateľov, ktorých sme skúšali predtým, a dostanete rovnaký vzorec odmietnutia. Prvá úroveň prežije tlak, ktorý by tretia neprežila.

[Prepnite späť na prezentáciu.]

---

## Slide 15 — When to swap models in production

Kedy teda modely v produkcii naozaj vymieňať? Existujú tri scenáre, v ktorých výmena skutočne pomáha.

Prvý je failover. Poskytovateľ má výpadok, napríklad spadne API Claude, čo sa stáva raz za pár mesiacov, a vy potrebujete ďalej obsluhovať prevádzku. Jednoriadková zmena konfigurácie pošle požiadavky namiesto toho na GPT alebo Gemini. Toto je vlastne hlavný dôvod, prečo sa väčšina produkčných ADK nasadení s LiteLLM vôbec zaoberá.

Druhý je per-task spôsobilosť, teda schopnosť na konkrétnu úlohu. Rôzne modely sú dobré v rôznych veciach. GPT-5 lepšie uvažuje nad obskúrnou matematikou, Claude Opus píše o čosi čistejší kód a Gemini sa natívne opiera o živé webové výsledky. Vyberte správny model pre každú úlohu a poskladajte ich cez sub-agentov alebo AgentTool.

Tretí je optimalizácia nákladov. Lacné dopyty smerujte na Haiku, GPT-4o-mini alebo Flash-Lite a ťažké dopyty na Opus, GPT-5 alebo Pro. Model môže byť dokonca iný pre každého sub-agenta. Callbacky a evaluácia, ktoré prídu neskôr v kurze, vám dajú prostriedky na to, aby ste zmerali, ktoré dopyty sú „ťažké“, a smerovali ich podľa toho.

---

## Slide 16 — The rule

Pravidlo, ktoré si odniesť, je na slide. Vendor-neutralita je schopnosť, nie zvyk. Modely nevymieňate len preto, že môžete. Vymieňate ich z konkrétneho dôvodu, či už je to failover, spôsobilosť alebo náklady. A vymieňate s evaluáciou, nie na základe pocitov. Rôzne modely majú rôzne vzorce odmietania, rôzne formátovacie sklony a rôznu presnosť na vašej konkrétnej úlohe. Neskôr v kurze si „výmenu s evaluáciou“ ukážeme celkom konkrétne.

---

## Slide 17 — Up next

Nabudúce sa pustíme do workflow agentov. Jeden agent stačí na hračkárske demá, ale skutočná práca potrebuje kompozíciu. Sequential, Parallel a Loop sú tri prvotriedne kompozičné primitívy. A pridáme aj kanonické wow demo ADK, dvojicu generátora a kritika, ktorá v slučke vylepšuje draft, kým kritik nepovie, že je dosť dobrý. Vidíme sa tam.
