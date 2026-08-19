# Course intro — Speaker notes (SK)

---

## Slide 1 — Title

Ahojte, vitajte v kurze o Agent Development Kite od Googlu, skrátene ADK. AI agenti sú dnes všade: v pracovných inzerátoch, v produktových plánoch aj v prezentáciách startupov. Medzi jedným zavolaním LLM API a systémom, ktorý beží v produkcii, číta databázu, volá ďalšie služby a drží si pamäť naprieč týždňami, je ale priepasť. A na konci tohto kurzu ju budete mať za sebou.

---

## Slide 2 — What you'll build

Na konci kurzu budete mať postavených agentov vo všetkých piatich kategóriách, ktoré vidíte na slide. Dve z nich stoja za zvýraznenie: perzistentná pamäť, ktorá prežije reštart servera, a hlasová konverzácia cez Live API od Gemini. Zvyšné tri dopĺňajú to, čo produkčný agent potrebuje, teda nástroje, orchestráciu viacerých agentov a nasadenie ako HTTP služby. Všetko v Pythone, všetko v spustiteľných notebookoch s vaším vlastným API kľúčom.

---

## Slide 3 — Three parts

Kurz sa odvíja v troch častiach. Prvá časť je základ a tvorí väčšinu práce. Kód agenta, ktorý v nej napíšete, beží na Claude, GPT, Gemini, Qwene alebo aj na lokálnej Llame, a to cez tenkú abstrakčnú vrstvu menom LiteLLM. Postupne dáte agentom nástroje, perzistentnú pamäť, orchestráciu viacerých agentov, evaluáciu a nasadenie cez HTTP. Druhá časť patrí výhradne Gemini. Je to ponor do schopností, ktoré na inom poskytovateľovi jednoducho nezreplikujete: vyhľadávanie s citáciami priamo z modelu, cachovanie dlhého kontextu, vďaka ktorému sú prompty s miliónom tokenov lacné, thinking budgety, ktoré si viete pridať alebo ubrať, a Live API pre hlasový rozhovor v reálnom čase. A záverečný modul je krátka odbočka k A2A, novému protokolu pod Linux Foundation, cez ktorý sa váš agent rozpráva s cudzím agentom, aj keď každý z nich vznikol v úplne inom frameworku.

---

## Slide 4 — Why this course

Kurzov o agentoch je vonku neúrekom, takže si povedzme, prečo stojí za váš čas práve tento. Po prvé, každý jeden modul má spustiteľný notebook, takže od prvej minúty pracujete rukami a nie ste len diváci prezentácie. Po druhé, všetko, čo napíšete, zostáva prenosné: poskytovateľa si vyberáte vy, a keď chcete vymeniť Gemini za Claude alebo za model bežiaci na vašom notebooku, meníte jeden riadok. A po tretie, nič tu nekončí pri demu. Preberieme pamäť, evaluáciu, nasadenie aj ochranné mechanizmy, takže to, čo postavíte, môže naozaj ísť do produkcie. Ak píšete v Pythone a s agentmi to myslíte vážne, poďme na to.
