# M05 — Speaker notes (SK)

---

## Slide 1 — Title

Vitajte späť. Tento modul je o workflow agentoch. Dostanete v ňom tri spôsoby, ako skladať viacerých agentov bez toho, aby ste sami písali akýkoľvek orchestračný kód: Sequential, Parallel a Loop. Sú to pomenované workflow, vyjadrené ako triedy v Pythone. A postavíme si aj kanonické ADK wow demo, generátor plus kritik v slučke, teda presne to, pri čom ľudia zalapajú po dychu, keď vidia ADK prvýkrát. Poďme na to.

---

## Slide 2 — One agent / Real work

Rámec celého modulu máte na slide. Jeden agent stačí na hračkárske problémy, ale skutočná práca potrebuje kompozíciu. Presne preto venujeme workflow celý modul. Len čo prekročíte hranicu jedného agenta, potrebujete spôsob, ako ich niekoľko prepojiť bez toho, aby ste zakaždým nanovo vymýšľali orchestrátor.

---

## Slide 3 — Three first-class primitives

ADK prináša tri prvotriedne workflow primitívy a spolu pokrývajú väčšinu toho, čo kedy budete potrebovať.

Prvý je SequentialAgent. Spúšťa svoje deti v poradí, ako shell pipeline. Každé dieťa dobehne skôr, než sa spustí ďalšie.

Druhý je ParallelAgent. Spúšťa všetky deti súbežne, podobne ako `asyncio.gather`. Ktoré skončí prvé, to skončí prvé.

A tretí je LoopAgent. Spúšťa deti v cykle, kým niekto nezavolá nástroj `exit_loop`, alebo kým beh nenarazí na iteračný strop. Predstavte si while slučku s núdzovým východom.

Toto je vlastne najsilnejší pedagogický rozdiel ADK. LangGraph od vás chce, aby ste riadiaci tok nakreslili ako graf uzlov a hrán. CrewAI ho schováva za role-playing DSL. ADK vám naproti tomu jednoducho dovolí workflow pomenovať ako Sequential, Parallel alebo Loop. Ak vám to znie ako Python, presne o to ide.

---

## Slide 4 — Visual

Na tomto slide vidíte tri primitívy vedľa seba. Sequential vľavo, kde deti bežia zhora nadol. Parallel v strede, kde deti bežia súbežne. A Loop vpravo, kde deti cyklujú, kým sa slučka neukončí.

Rovnaký Runner, rovnaký event stream, rovnaký state dict. Mení sa iba kompozičná trieda. Všetko ostatné, čo ste sa v kurze doteraz naučili, funguje ďalej.

---

## Slide 5 — State is the pipe

Medzi deťmi je state rúra, ktorá prenáša dáta od jedného k druhému. Dajte dieťaťu `output_key="summary"` a jeho výsledok sa zapíše do `state["summary"]`. V inštrukcii neskoršieho dieťaťa potom použite `{summary}` so zloženými zátvorkami a ADK dosadí hodnotu zo state skôr, než prompt vôbec uvidí model.

Existuje aj voliteľná varianta, `{summary?}` s otáznikom na konci. Znamená „dosaď, ak existuje, a nechaj prázdne, ak chýba“. Hodí sa pri iteráciách slučky, kde skoré prechody kľúč ešte nezapísali.

Pravidlo je teda jednoduché. Zapisujte cez `output_key`, čítajte cez vkladanie premenných v zložených zátvorkách. To je v podstate celá orchestračná slovná zásoba workflow agentov.

---

## Slide 6 — SequentialAgent

Začnime prvým primitívom, ktorým je SequentialAgent. Je to usporiadaná pipeline, v ktorej state tečie po prúde.

---

## Slide 7 — A two-step pipeline

Tu na slide máme rozpísanú dvojkrokovú pipeline. Hore je agent summarizer, v strede agent translator a dole SequentialAgent, ktorý ich oboch balí do jednej kompozície.

Prejdime si, ako tečie state. Summarizer má `output_key="summary"`, takže jeho výsledok sa zapíše do `state["summary"]`. Inštrukcia translatora obsahuje `{summary}`, takže ADK dosadí hodnotu zo state skôr, než prompt uvidí model translatora. Translator teda pracuje so zhrnutím, nie s pôvodným vstupom používateľa.

Nepíšete for-slučku, ktorá by deti volala. Nepodávate state ručne z jedného do druhého. SequentialAgent je tá slučka a ADK podáva state implicitne cez session.

---

### Notebook break — Sequential pipeline in action

[Prepnite obrazovku na notebook.]

Tu je Sequential pipeline zapojená a pripravená na spustenie. Nakŕmim ju tromi vetami o hladnej mačke. [Spustite bunku.] Sledujte event stream. Najprv beží summarizer a zapíše jednovetové zhrnutie do `state["summary"]`. Potom nastupuje translator, prečíta si zhrnutie zo state cez vkladanie premenných a vyprodukuje slovenský preklad. Dve LLM volania, jedna kompozícia, žiadny spojovací kód medzi nimi.

[Prepnite späť na prezentáciu.]

---

## Slide 8 — ParallelAgent

Prejdime k druhému primitívu, ktorým je ParallelAgent. Ide o paralelný fan-out, čo znamená, že reálny čas behu je približne rovný najpomalšiemu dieťaťu, nie súčtu trvaní všetkých detí.

---

## Slide 9 — Three-way fan-out

Na slide máme trojcestný fan-out. Traja výskumní agenti, jeden pre Nemecko, jeden pre Slovensko a jeden pre Česko, každý s vlastnou inštrukciou a vlastným state kľúčom. ParallelAgent dole ich balí dokopy ako jednu kompozíciu.

Keď ParallelAgent beží, ADK pod kapotou použije asyncio a vystrelí všetky tri deti súbežne. Vzor je presne ako `asyncio.gather(task_a, task_b, task_c)`, len každá úloha je LLM agent a každý výsledok pristane vo vlastnom slote v state.

---

### Notebook break — Three researchers in parallel

[Prepnite obrazovku na notebook.]

Tu je paralelné trio výskumníkov, ktoré sme si práve definovali. Spustím stopky a nechám ich bežať. [Spustite bunku.] Sledujte, ako sa event stream odvíja. Všimnite si, že autori sa prelínajú v poradí, v akom dobiehajú, nie v poradí, v akom sme ich deklarovali. Niekedy pristane prvý `cz_researcher`, inokedy `de_researcher`. To je súbežnosť v praxi. A stopky dole ukazujú zhruba jednu sekundu reálneho času namiesto približne troch sekúnd, ktoré by ste videli, keby bežali jeden po druhom.

[Prepnite späť na prezentáciu.]

---

## Slide 10 — What to notice

Z toho behu stoja za zmienku tri pozorovania.

Po prvé, autori sa prelínajú v poradí dobehnutia, nie v poradí deklarácie. Keď teda čítate eventy z paralelného behu, nepredpokladajte žiadne konkrétne poradie.

Po druhé, reálny čas behu zodpovedá trvaniu jedného dieťaťa, nie súčtu. Ak každé LLM volanie trvá sekundu, sekvenčný beh zaberie tri sekundy, kým paralelný niečo cez sekundu. Úspora rastie so šírkou fan-outu.

A po tretie, každé dieťa zapisuje do vlastného state kľúča, takže sa nezrážajú. Keby sa dve deti pokúsili zapísať do rovnakého kľúča, vyhralo by to, ktoré zapíše posledné. To nerobte.

Bežný produkčný vzor je rozvetviť nezávislý výskum alebo vyhľadávania paralelne a nazbieraný state potom podať sekvenčnému syntetizátorovi. Presne ten si o chvíľu postavíme.

---

## Slide 11 — LoopAgent

Tretí primitív je LoopAgent, kanonické ADK wow demo. Generátor plus kritik, ktorí výsledok vylepšujú dovtedy, kým nie je kritik spokojný.

---

## Slide 12 — The pattern

Prejdime si vzor na slide. LoopAgent má dve deti. Generátor zapíše návrh do state. Kritik si potom návrh prečíta a rozhodne, či je dosť dobrý. Ak nie je, zapíše kritiku späť do state a slučka pokračuje, takže generátor si v ďalšom prechode kritiku prečíta a návrh prepracuje. Ak je kritik spokojný, zavolá `exit_loop`, ADK to volanie zachytí a slučku ukončí.

Tento vzor má v literatúre veľa mien: self-correction čiže sebakorekcia, critic-driven refinement, Reflexion, draft-and-review. Nech ho nazvete akokoľvek, v ADK je to jednoducho LoopAgent s dvomi deťmi.

Bez LoopAgenta by ste v Pythone písali `while True` s podmienkou na ukončenie. S LoopAgentom sa naproti tomu ADK postará o slučkovanie, podávanie state, počítanie iterácií aj mechanizmus ukončovacieho signálu. Vy deklarujete dve deti a maximum iterácií a ADK vzor spustí.

---

## Slide 13 — The generator

Tu na slide je kód generátora. Je to LlmAgent s jedinou úlohou, vytvoriť alebo prepracovať slogan. Jeho inštrukcia číta predchádzajúci návrh a predchádzajúcu kritiku zo state cez `{draft?}` a `{critique?}` s otáznikom, pretože v prvej iterácii ešte ani jeden z kľúčov neexistuje. Inštrukcia hovorí zhruba toto: ak existujú oba, prepracuj návrh podľa kritiky, inak napíš návrh od nuly. Výstup ide do `state["draft"]`.

Pridám jedno nenápadné, ale dôležité dizajnové pravidlo. Výstup generátora je text, takže v inštrukcii naozaj jasne povedzte, že výstupom má byť iba samotný slogan. Žiadny úvod, žiadne vysvetlenie, žiadny markdown. Vo workflow kompozíciách sa odchýlky vo formátovaní výstupu reťazia ďalej. Ak generátor pridá prefix „Here's my draft:“, kritik ho uvidí ako súčasť návrhu a bude kritizovať aj ten. Buďte preto prísni.

---

## Slide 14 — The critic

Na slide je kritik a k nemu LoopAgent, ktorý ho balí dokopy s generátorom. Inštrukcia kritika číta aktuálny návrh zo state a hodnotí ho podľa pomenovaných kritérií. Ak niektoré kritérium zlyhá, zapíše jednovetovú kritiku späť do state. Ak prejdú všetky, zavolá nástroj `exit_loop`.

`exit_loop` sa importuje z `google.adk.tools`. Je to built-in tool, teda vstavaný nástroj, ktorý rodičovskému LoopAgentu signalizuje, že sme hotoví. Kritik ho dostane vo svojom zozname `tools=`. Keď teda model kritika vyšle volanie `exit_loop`, ADK ho zachytí a slučku ukončí. Je to čistý signál bez akejkoľvek mágie.

A napokon je dole na slide samotný LoopAgent. Dve deti a max_iterations nastavené na päť. Ten strop je dôležitý a nasledujúci slide rozoberá prečo.

---

### Notebook break — Generator and Critic refining a draft

[Prepnite obrazovku na notebook.]

Teraz spustím slučku generátora s kritikom. Používateľ žiada slogan. [Spustite bunku.] Sledujte, ako sa odvíjajú iterácie. Generátor vyprodukuje prvý návrh, ktorý obsahuje slovo „Master“, čím porušuje jedno z pravidiel kritika o klišé. Kritik to označí v jednovetovej kritike. Generátor si kritiku v ďalšom prechode prečíta a návrh prepracuje. Tentokrát kritik súhlasí a priamo v event streame vidíte volanie nástroja `exit_loop` s prázdnymi argumentmi. To je signál, ktorý slučku ukončí.

[Prepnite späť na prezentáciu.]

---

## Slide 15 — What to always do

S LoopAgentom vždy dodržte tri pravidlá.

Po prvé, vždy nastavte max_iterations. Ak sa kritik nedá uspokojiť, agent beží donekonečna a váš účet za API s ním. Päť zvyčajne stačí. Pre predstavu, videl som produkčné LoopAgenty s max_iterations na desiatke, ale nikdy som nevidel hodnotu vyššiu než dvadsať.

Po druhé, `exit_loop` spárujte s dieťaťom, ktoré nesie podmienku ukončenia, zvyčajne s kritikom, recenzentom alebo strážcom brány. Nerozhadzujte `exit_loop` medzi viacero detí, pokiaľ na to nemáte konkrétny dôvod, pretože podmienka ukončenia sa potom veľmi ťažko číta.

A po tretie, pre state kľúče, ktoré ešte nemusia existovať, používajte syntax s otáznikom. `{draft?}` znamená „dosaď, ak existuje, inak prázdny reťazec“. Prvá iterácia žiadny predchádzajúci návrh nemá, takže práve otáznik vás zachráni pred výnimkou KeyError.

---

## Slide 16 — Composing workflows

A teraz to celé poskladajme. Workflow agenti sú sami osebe agenti, čo znamená, že ich môžete vnárať do iných workflow agentov.

---

## Slide 17 — Parallel inside Sequential

Tu na slide je klasická kompozícia. SequentialAgent, ktorého prvým dieťaťom je ParallelAgent. Nezávislý výskum teda v prvom kroku rozvetvíte paralelne a v druhom kroku sekvenčne syntetizujete.

Dokopy je to päť LLM volaní, traja paralelní výskumníci bežiaci súbežne a potom jeden syntetizátor, ktorý si všetky tri výsledky prečíta zo state. Reálny čas behu vychádza zhruba na dve volania, nie na päť. Inštrukcia syntetizátora používa `{germany_fact}`, `{slovakia_fact}` a `{czech_fact}`, aby si všetky tri paralelné výsledky vytiahla zo state.

Presne tento tvar má väčšina produkčných agentov. Nie je to jeden monolitický agent a nie je to ani päť detí v plochom zozname, ale pipeline fáz, kde niektoré bežia paralelne vo vnútri fázy a iné sekvenčne naprieč fázami.

---

### Notebook break — Composition: parallel inside sequential

[Prepnite obrazovku na notebook.]

Tu je kompozícia, ktorú sme si práve definovali, ParallelAgent vo vnútri SequentialAgenta. Spustím stopky a nechám ju bežať. [Spustite bunku.] Sledujte, čo sa deje. Traja výskumníci vystrelia súbežne a každý zapisuje do vlastného slotu v state. Len čo všetci traja skončia, nastupuje syntetizátor, prečíta si `{germany_fact}`, `{slovakia_fact}` a `{czech_fact}` zo state a napíše záverečnú správu, ktorá všetky tri prepája. Celkový reálny čas vychádza zhruba na dve volania, hoci LLM volaní je päť. Fan-out sa oplatil.

[Prepnite späť na prezentáciu.]

---

## Slide 18 — Workflow agent vs. LLM-driven flow

Veľkou alternatívou k workflow agentom je nechať rozhodovať LLM. Postavíte jedného agenta so všetkými sub-agentmi v zozname `sub_agents=` a model na vrchole si vyberá, ktorého zavolať. O tom bude ďalší modul.

Oba štýly fungujú, ale nie sú zameniteľné.

Workflow agenta použite vtedy, keď je riadiaci tok pevný, napríklad vždy najprv zhrnúť a potom preložiť. Keď potrebujete determinizmus pre testy alebo evaluácie. Keď záleží na latencii, pretože paralelný beh sa rozvetví bez rozhodovacieho kola navyše. A keď má byť workflow auditovateľný priamo z diagramu.

LLM-driven flow, teda tok riadený modelom, naproti tomu použite vtedy, keď riadiaci tok závisí od vstupu používateľa. Keď je celou pointou flexibilita. Keď skutočnú hodnotu pridáva práve úsudok modelu. A keď sa konverzácie môžu vydať kamkoľvek a vopred pripravený tok by produkt zväzoval.

---

## Slide 19 — The rule of thumb

Orientačné pravidlo máte na slide. Ak viete workflow pomenovať, použite workflow agenta. Ak neviete, nechajte rozhodovať LLM.

Sequential, Parallel a Loop čisto pokrývajú prípady s pomenovaným workflow. Na čokoľvek zložitejšie ich začnite skladať do seba. A ak sa kompozícia stane neprehľadnou, je to signál, že workflow sa v skutočnosti pomenovať nedá a riadenie má prevziať LLM.

Ešte jedna vec, ktorú sa oplatí vedieť, a vidíte ju v drobnom písme na slide. Vydanie ADK 2.0 pridalo grafový workflow runtime, v ktorom sa agenti a nástroje stávajú uzlami explicitného grafu s hranami medzi nimi. Mieri presne na tie neprehľadné prípady, teda podmienené vetvenia a cyklické toky, ktoré kompozícii prerastú cez hlavu. Na všetko v tomto kurze však zostávajú správnym nástrojom tri šablónové agenty, a tak staviame práve s nimi.

---

## Slide 20 — Up next

Nabudúce nás čakajú multi-agent hierarchie. To je LLM-driven alternatíva k workflow agentom. Sub-agenti pre transfer a AgentTool pre consultant pattern, teda vzor konzultanta. AgentTool sme letmo zahliadli už pri nástrojoch. Teraz ho postavíme do kontextu oproti sub-agentom a uvidíme, kedy je ktorý prístup ten správny. Vidíme sa tam.
