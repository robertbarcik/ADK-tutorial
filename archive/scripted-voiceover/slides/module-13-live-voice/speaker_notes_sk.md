# M13 — Speaker notes (SK)

---

## Slide 1 — Title

Témou tohto modulu je Live API: obojsmerný audio streaming, voice activity detection a interruption handling, čiže spracovanie prerušení, to všetko cez jediný WebSocket. Je to tretia z troch schopností, ktoré odomyká len Gemini, a zároveň tá najvýraznejšia, pretože žiadny iný poskytovateľ túto schopnosť k máju 2026 v čistej podobe neponúka.

---

## Slide 2 — The most differentiated capability

Gemini Live je jediná schopnosť Gemini, ktorá nemá čistú alternatívu u konkurencie. Najbližšie k nej má Realtime API od OpenAI, ale s inou sémantikou, inou cenotvorbou a inými spôsobmi zlyhania. Anthropic nemá žiadny priamy ekvivalent. Ak je real-time hlas váš produkt, staviate na Gemini.

---

## Slide 3 — What Live does

Live robí štyri veci. Obojsmerné audio, teda hlas dnu a hlas von cez jediné WebSocket spojenie. Voice Activity Detection, kde Gemini samo rozhodne, že ste dohovorili, a začne odpovedať bez vyzvania. Prerušenie, čiže keď začnete hovoriť, kým je Gemini uprostred odpovede, okamžite stíchne a počúva. A latenciu pod jednu sekundu, keď všetko ide hladko.

Práve prerušenie je to, vďaka čomu to pôsobí ako skutočný rozhovor, a nie ako telefónne menu.

---

## Slide 4 — Live vs run_async

`run_async` je request/response. Podáte správu, eventy prúdia späť a ťah sa skončí. Každý ťah je pritom nezávislý od ostatných.

`run_live` funguje inak. Agent drží otvorený obojsmerný WebSocket na Gemini. Namiesto jednej správy streamujete kúsky audia alebo textu do fronty a kúsky odpovede prúdia paralelne späť. Session zostáva otvorená tak dlho, ako potrebujete, bez akejkoľvek štruktúry po ťahoch.

Textovým agentom sedí `run_async`, hlasoví agenti potrebujú `run_live`.

---

## Slide 5 — Three primitives

Kontrakt Live API tvoria tri primitívy.

`LiveRequestQueue` je fronta na strane klienta, do ktorej tlačíte vstup používateľa. Metóda `send_content` slúži na text, `send_realtime` na raw audio bytes, teda surové audio bajty.

`Runner.run_live` je async generátor, ktorý vydáva serverové eventy. Beží, kým sa fronta nezavrie alebo kým nepríde turn-complete event.

`RunConfig` s `response_modalities` riadi tvar výstupu. `TEXT` vám dá bežné textové kúsky. `AUDIO` vám dá raw PCM bytes v poli `inline_data`. Pri vývoji používajte `TEXT`, v produkčných hlasových agentoch `AUDIO`.

---

## Slide 6 — Code shape

Každý Live agent sleduje rovnaký päťkrokový vzor. Definujete `LlmAgent` s modelom, ktorý Live API podporuje. Vytvoríte `LiveRequestQueue`. Vytvoríte `RunConfig` so zvolenou modalitou. Cez `send_content` zatlačíte do fronty obsah od používateľa. A napokon iterujete cez async generátor `run_live` a konzumujete eventy, kým frontu nezavriete.

Kľúčová vlastnosť tohto tvaru je, že fronta zostáva otvorená naprieč ťahmi. Pri viacťahovej konverzácii jednoducho ďalej tlačíte obsah a ďalej konzumujete eventy. WebSocket sa medzi otázkami nikdy nezatvára.

---

## Slide 7 — VAD + interruption

Voice Activity Detection aj prerušenia sa riešia na strane servera a v predvolenom stave sú zapnuté. Ladíte ich cez `RealtimeInputConfig` vnútri `RunConfig`.

`silence_duration_ms` určuje, ako dlho Gemini čaká, kým pauzu vyhodnotí ako koniec ťahu. Predvolená hodnota je okolo 800 milisekúnd. Nižšia hodnota reaguje svižnejšie, ale je náchylnejšia na falošné spustenia pri krátkych pauzách. Vyššia pôsobí prirodzenejšie, ale pridáva citeľné oneskorenie. Rozumný konverzačný štandard je 1000 milisekúnd.

`prefix_padding_ms` zachytáva krátke audio okno tesne pred detegovanou rečou, aby Gemini neprišlo o prvú slabiku.

Prerušenie funguje úplne automaticky. Pošlite audio do fronty, kým Gemini produkuje výstup, a ono sa zastaví a počúva. Nepotrebujete na to žiadny kód na strane klienta.

---

## Slide 8 — Production architecture

Produkčný Live-voice stack má tri vrstvy. Prehliadač zachytáva audio z mikrofónu cez Web Audio API a streamuje ho cez WebSocket na váš backend. Backend tlačí tieto audio kúsky do `LiveRequestQueue`. A ADK agent s `run_live` drží WebSocket na Gemini a prenáša audio oboma smermi.

Nič z toho nebeží v notebooku. Notebook učí kontrakt na strane ADK, teda čo agent vidí, ako tlačiť vstup a ako konzumovať eventy. Pre plný stack s prehliadačom a backendom nájdete v repe `adk-samples` príklad hlasového agenta.

---

### Notebook break — One Live audio turn

[Prepnite obrazovku na notebook.]

Demo bunka spustí jeden Live audio ťah od začiatku do konca. Zatlačí napísanú správu do fronty, iteruje cez `run_live` a naraz sa vrátia dva prúdy. Samotné audio prichádza ako inline data parts a my počítame bajty. Slová prichádzajú popri ňom cez output transcription, čiže prepis výstupného audia, najprv ako čiastkové kúsky, kým model hovorí, a potom ako jedna skonsolidovaná veta označená ako finished.

Jednu vec v konfigurácii treba vypichnúť. Aktuálne live modely sú audio-natívne, takže žiadosť o čisto textový výstup skončí odmietnutím session s errorom 1007. Preto si demo pýta audio a slová číta z transkripcie. Ak bunka narazí na prechodnú chybu servera, spustite ju znova. Endpoint je preview-tier a občasné zaškrtanie je na strane Googlu, nie vo vašom kóde.

[Prepnite späť na prezentáciu.]

---

## Slide 9 — Fair warning

Férové varovanie si zaslúži vlastný slide. Live API je preview-tier. Ešte počas jari dvetisícdvadsaťšesť hádzalo na free kľúčoch prechodné serverové chyby a Google endpoint opravil až v júli. Sessions sa dnes pripájajú spoľahlivo, ale občasný výpadok spojenia alebo timeout je stále na strane Googlu, nie vo vašom kóde. Aktuálny stav je zaznamenaný v `DEMOS_BROKEN.md`.

Koncepty, ktoré sa tu učíte, sú trvalé tak či tak. Ak by ste niekedy narazili na pretrvávajúce zlyhania, prepnite na paid tier alebo to spustite cez Vertex AI, ktorý pod kapotou používa inú infraštruktúru.

---

## Slide 10 — Pricing

Live sa účtuje za minútu, nie za token. Model `gemini-3.1-flash-live-preview` je do výšky kvóty zadarmo. Model `gemini-2.5-flash-native-audio-latest` je platený, zhruba 1,2 centa za minútu audia dnu aj von dokopy. Pri konverzačnom agentovi s priemerom jednej minúty na session je to menej než dolár na sto sessions.

Mená modelov sa priebežne menia. Pri stavaní pre produkciu si aktuálny katalóg overte v dokumentácii Google AI pre vývojárov.

---

## Slide 11 — When to use Live

Pre real-time konverzačný hlas je Live ten správny nástroj, najmä keď potrebujete spracovanie prerušení, latenciu pod sekundu alebo otvorenú session s nepretržitým dialógom.

Nie je to nástroj na transkripciu, tam použite dedikovanú speech-to-text službu a text podajte bežnému agentovi. Nie je to nástroj na TTS prehrávanie vopred pripravených odpovedí, na to slúži dedikovaná TTS služba. A nie je to nástroj na neinteraktívny hlas, pretože scenár narácie živé spojenie nepotrebuje.

Na všetko ostatné je `run_async` s textom plus samostatné STT a TTS jednoduchšie, lacnejšie a lepšie kontrolovateľné.

---

## Slide 12 — Carry forward

Live je pre real-time konverzačný hlas. API tvorí `run_live` plus `LiveRequestQueue` plus `RunConfig` s response modalities. Mená modelov sa priebežne menia. Krehkosť preview-tieru je dnes reálna, no tvar API je trvalý.

---

## Slide 13 — Next

Finále kurzu je A2A, protokol medzi agentmi. Celý kurz ste stavali agentov, ktorí volajú nástroje. Ďalší modul je o agentoch, ktorí volajú iných agentov, naprieč procesmi, frameworkami aj organizáciami. Čakajú vás štyri podstatné mená, jedno živé demo a chytáky, ktoré sa oplatí poznať skôr, než niečo nasadíte.
