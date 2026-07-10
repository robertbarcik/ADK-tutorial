# M12 — Speaker notes (SK)

---

## Slide 1 — Title

Thinking budgety, teda tokenové rozpočty na uvažovanie, sú najjednoduchšou z troch Gemini funkcií, ktoré si v tejto časti kurzu odomykáme. Jeden gombík, jedno číslo a jasný efekt na úlohy náročné na uvažovanie. V tomto module si ukážeme, čo ten gombík robí, ako ho nastaviť vo vnútri ADK agenta a kedy sa ním vôbec oplatí zaoberať.

---

## Slide 2 — What thinking is

Gemini 2.5 a novšie modely robia pred napísaním finálnej odpovede interný reasoning pass, teda kolo uvažovania. Toto uvažovanie je neviditeľné. V samotnom výstupe sa neobjaví, ale nájdete ho v usage metadata ako `thoughts_token_count` a stojí reálny čas.

Vy modelu nastavíte budget, čiže strop na počet reasoning tokenov, ktoré smie minúť. Gemini premýšľa najviac do tejto výšky a až potom napíše odpoveď. Diagram ukazuje celý tok. Dnu ide prompt, spotrebuje sa až N neviditeľných reasoning tokenov a von vyjde finálna odpoveď. Uvažovanie sa pritom účtuje osobitne.

---

## Slide 3 — The knob

API je `ThinkingConfig(thinking_budget=N)`. Keď ho nastavíte na nulu, uvažovanie vypnete. Hodnota 2048 a vyššia zapína zmysluplné uvažovanie. A argument `include_thoughts=True` sprístupní reasoning tokeny vo výstupe, čo sa hodí, keď chcete debugovať, čím si model prechádzal.

Gemini 3 a novšie ponúkajú aj `thinking_level` so štyrmi predvoľbami MINIMAL, LOW, MEDIUM a HIGH. Na verzii 2.5 používajte číselný budget, na trojke a novších funguje oboje.

---

### Notebook break — Budget comparison

[Prepnite obrazovku na notebook.]

Bunka sedem spúšťa tú istú viacstupňovú úlohu o ziskovej marži dvakrát, raz s `thinking_budget=0` a raz s `thinking_budget=4096`. Rovnaký prompt, rovnaký model.

Sledujte tri veci: latenciu, `thoughts_token_count` v usage metadata a kvalitu odpovede. Čísla sa medzi oboma behmi líšia.

[Prepnite späť na prezentáciu.]

---

## Slide 4 — Direct comparison

Čísla ten kompromis potvrdzujú. Vstup bol v oboch behoch rovnaký, 158 tokenov, a rovnaká bola aj dĺžka výstupu, 702 tokenov.

S budgetom nula prišla odpoveď za menej než sekundu a model nespotreboval žiadne thought tokeny. S budgetom 4096 to trvalo jedenásť sekúnd a padlo na to 1109 thought tokenov. Tých 1109 tokenov je uvažovanie, ktoré model urobil interne a používateľovi ho nikdy neukázal.

Rovnaký prompt, rovnaký model a rovnako dlhý výstup, ale iná hĺbka uvažovania, iná latencia a iná cena.

---

## Slide 5 — The even-better demo

Úloha so súčtom prvočísel ukazuje rozdiel v kvalite úplne hmatateľne. Otázka znie, aký je súčet všetkých prvočísel medzi 20 a 50.

Rýchly agent s thinkingom nastaveným na nulu odpovie za menej než sekundu a povie 255, čo je nesprávne.

Uvažujúci agent s thinkingom nastaveným na 2048 potrebuje desať sekúnd. Vymenuje si 23, 29, 31, 37, 41, 43 a 47, sčíta ich a dostane 251, čo je správne.

Rovnaká otázka, rovnaký model, len iný budget a iná odpoveď. Rozdiel v kvalite je viditeľný, nie iba teoretický.

---

## Slide 6 — BuiltInPlanner code

Na slide vidíte `BuiltInPlanner(thinking_config=...)`, čo je ADK wrapper na thinking budgety. Podáte ho ako argument `planner` ktorémukoľvek LlmAgentu. Všetko ostatné zostáva rovnaké, meno, model, inštrukcia aj nástroje sa nemenia.

Argument `planner` je spôsob, akým ADK sprístupňuje funkcie ovplyvňujúce to, ako model uvažuje, bez toho, aby nafukoval konštruktor agenta.

---

## Slide 7 — When to use thinking

Budget zvýšte vtedy, keď problém vyžaduje krok-za-krokom postup, teda viacstupňové výpočty, logické hádanky, plánovanie, debugovanie kódu, analýzu závislostí alebo ťažkú matematiku.

Pri faktových vyhľadaniach uvažovanie preskočte. Hlavné mesto Francúzska model pozná aj tak a uvažovanie by pridalo iba latenciu. Preskočte ho aj pri textových transformáciách, ako je sumarizácia, preklad alebo prepis štýlu, a rovnako pri klasifikačných úlohách.

Heuristika je jednoduchá. Musí model niečo vypracovať, alebo len vytiahnuť niečo, čo už vie? Keď treba vypracovať, budget zvýšte. Keď stačí vytiahnuť, uvažovanie vynechajte.

---

## Slide 8 — Production pattern

Praktický produkčný vzor routuje podľa typu otázky.

Lacný router agent s `thinking_budget=0` sa na otázku pozrie a deleguje ju ďalej. Ťažké problémy pošle špecialistovi s vysokým thinking budgetom, ľahké zas rýchlemu špecialistovi.

Je to ten istý vzor koordinátora a špecialistov, ktorý poznáte zo skoršej časti kurzu. Použite `AgentTool`, aby koordinátor zostal pánom konverzácie, kým každý špecialista rieši jednu triedu problémov.

Dostanete tak kvalitné uvažovanie tam, kde ho potrebujete, a rýchle odpovede tam, kde nie.

---

## Slide 9 — Gemini 3+ levels

Gemini 3 a novšie ponúkajú popri číselnom budgete aj API s predvoľbami. MINIMAL znamená prakticky vypnuté uvažovanie. LOW je zhruba tisíc thought tokenov, MEDIUM okolo štyroch tisíc a HIGH je bez limitu, kde si model sám rozhodne, koľko bude premýšľať.

Po `thinking_level` siahnite, keď vám stačí hrubé nastavenie a na presnom čísle vám nezáleží. Keď chcete presnú kontrolu, použite `thinking_budget`. Na trojke a novších fungujú obe API.

---

## Slide 10 — Thought signature persistence

Thought signatures, teda podpisy myšlienok, prežívajú v Geminim naprieč multi-turn tool callmi, čiže viackolovými tool callmi. Ak model v prvom kole prešiel uvažovaním cez nejaký problém a druhé kolo je nadväzujúca otázka na ten istý problém, Gemini si kontext uvažovania prenesie ďalej a nemusí premýšľať odznova. Thinking budget sa druhýkrát neminie.

Parameter `reasoning_effort` od OpenAI začína každé kolo odznova a extended thinking u Clauda sa medzi kolami tiež resetuje. K máju 2026 nič také žiadny iný frontier model neponúka.

Pri viackolových konverzáciách nad ťažkými problémami, ako sú kódovací asistenti alebo výskumní agenti, je to podstatný rozdiel. Cenu za uvažovanie platíte raz za session, nie raz za každé kolo.

---

## Slide 11 — LiteLLM parity

Podobné ovládacie prvky ponúkajú aj iní poskytovatelia, len s iným slovníkom.

OpenAI pri GPT-5 a o3 používa `reasoning_effort`, predvoľbu low, medium alebo high. Cez LiteLLM prechádza čisto.

Anthropic pri Claude 4.5 a novších používa extended thinking cez `thinking={"type": "enabled", "budget_tokens": N}`. Pri základných volaniach cez LiteLLM funguje, ale láme sa na kolách s tool callmi. Ak potrebujete thinking na Claudovi spolu s nástrojmi, pozrite si pred nasadením issue tracker LiteLLM.

Qwen a DeepSeek ponúkajú reasoning varianty modelov, kde je uvažovanie zapnuté v predvolenom stave, a niektoré prijímajú parameter `reasoning.effort`.

Spoľahlivosti `ThinkingConfig` od Gemini sa pri agentoch náročných na nástroje nevyrovná nič z toho. Ak je kontrola uvažovania prvoradou požiadavkou, najkonzistentnejšie API nájdete na natívnom Gemini.

---

## Slide 12 — Carry forward

Thinking je gombík, nie predvolený stav. Pri ťažkých problémoch ho zvýšte, pri ľahkých ho nechajte na nule. A podľa typu otázky routujte cez vzor koordinátora a špecialistov, ktorý poznáte zo skoršej časti kurzu.

---

## Slide 13 — Next

Nabudúce nás čaká Live API, teda obojsmerný audio streaming, hlas dnu aj hlas von, s voice activity detection a interruption handlingom, čiže spracovaním prerušení. K máju 2026 je to najvýraznejšie odlíšená schopnosť Gemini na trhu. Jedno férové varovanie na záver: Live API je najkrehkejšia z trojice funkcií, ktoré tu odomykáme. Ak vám demo vo vašom prostredí nepobeží, pozrite si `DEMOS_BROKEN.md`, kde nájdete náhradnú cestu.
