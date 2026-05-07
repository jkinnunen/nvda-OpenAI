Ako želite namjensko desktop iskustvo s dodatnim radnim tokovima, pogledajte [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (samostalnu aplikaciju i minimalistički NVDA dodatak). AI-Hub i dalje ostaje opcija s punim skupom značajki unutar NVDA-a.

# AI-Hub

**AI-Hub** je NVDA dodatak koji povezuje vaš čitač zaslona s više API-ja velikih jezičnih modela (LLM). Koristite ga za pisanje, sažimanje, pomoć pri prevođenju, vid (slike i snimke zaslona), glasovna pitanja, transkripciju i neobavezne dijaloške alate (TTS, OCR i drugo) — bez napuštanja NVDA-a.

**Naziv paketa** dodatka u NVDA-u i dalje je `openai` (radi kompatibilnosti s postojećim instalacijama). **Prikazni naziv** koji vidite u izbornicima i postavkama je **AI-Hub**.

## Značajke na prvi pogled

- **Chat** u namjenskom glavnom dijalogu s poviješću, sistemskom uputom te odabirom modela i računa.
- **Slike i dokumenti** kao privici iz datoteka; **URL-ovi** do udaljenih datoteka uz provjere tipa usklađene s **odabranim pružateljem**.
- **Pametno lijepljenje** u polje upita: zalijepite datoteke iz međuspremnika, putanje iz teksta ili jedan URL (dostupno i iz kontekstnog izbornika upita). `Ctrl+V` koristi istu logiku kada je fokus na upitu.
- **Spremanje razgovora i povijest** uz preimenovanje, brisanje i ponovno otvaranje.
- **Postavi pitanje** s bilo kojeg mjesta (bez zadane tipke): dodijelite gestu u **Ulazne geste → AI-Hub** za snimanje, slanje te slušanje ili čitanje odgovora.
- **Globalni opis**: snimka zaslona (`NVDA+E`) ili područje objekta navigatora (`NVDA+O`) šalje se u sesiju razgovora.
- Podizbornik **Alati** (pod NVDA → AI-Hub): pomoćni alati specifični za pružatelja, poput TTS-a, OCR-a, govora u tekst, Lyria zvuka i upravljanja Ollama modelima.
- Opcije **Zaključivanje / web pretraga** pojavljuju se samo kada ih **trenutni model** podržava (ovisno o pružatelju).

Ovaj dodatak **nema** vlastiti alat za provjeru ažuriranja. **Ažuriranja** se obrađuju kroz **službeni NVDA Add-on Store** kada instalirate odande. Ako instalirate ručno sa [stranice izdanja](https://github.com/aaclause/nvda-OpenAI/releases), novije `.nvda-addon` verzije instalirajte na isti način.

## Podržani pružatelji

Konfigurirajte **jednog ili više pružatelja** u NVDA-u pod **Postavke → Postavke → AI-Hub**. Svaki pružatelj može imati **više imenovanih računa** (API ključeve, opcionalnu organizaciju ili osnovni URL gdje je primjenjivo).

| Pružatelj | Uloga |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT i povezani modeli; službeni dijaloški alati za transkripciju i TTS |
| [DeepSeek](https://www.deepseek.com/) | DeepSeek API (OpenAI-kompatibilan) |
| **Prilagođeni OpenAI** | Bilo koji OpenAI-kompatibilan HTTP API (prilagođeni osnovni URL + ključ) |
| **Ollama** | Lokalni modeli preko OpenAI-kompatibilne krajnje točke; alat za upravljanje modelima |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; Voxtral TTS, OCR i alati govor-u-tekst |
| [OpenRouter](https://openrouter.ai/) | Mnogi modeli trećih strana iza jednog ključa |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; alat Lyria 3 Pro |

Dodatak može preuzeti API ključeve iz **varijabli okruženja** kada su postavljeni (na primjer `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` i drugi). Sučelje postavki ostaje glavno mjesto za upravljanje računima.

### Mehanizmi za govor u tekst (transkripcija)

Za **transkripciju mikrofona/datoteke** unutar glavnog tijeka rada (ne zasebni OpenAI alat za transkripciju), možete birati između **whisper_cpp** (lokalno), **openai** (Whisper API) i **mistral**, u odjeljku **Audio** postavki AI-Huba.

## Instalacija

1. Otvorite [stranicu izdanja dodatka](https://github.com/aaclause/nvda-OpenAI/releases).
2. Preuzmite najnoviji `.nvda-addon` paket.

## Početna konfiguracija

1. Otvorite **NVDA → Postavke → Postavke**.
2. Odaberite kategoriju **AI-Hub**.
3. U odjeljku **API Accounts** odaberite **Add account...**.
4. U dijalogu računa odaberite pružatelja, unesite naziv računa i ispunite obavezna polja (API ključ za većinu pružatelja; base URL za **Custom OpenAI** i **Ollama**, a Ollama po zadanom koristi lokalni http://127.0.0.1:11434/v1 ako je polje prazno).
5. Spremite, pa po želji dodajte još računa, uredite postojeće ili uklonite nekorištene račune s popisa.
6. Po želji prilagodite **Audio**, **Chat feedback**, **Advanced** / temperaturu i **Auto-save conversation** (zadano uključeno).

Dok barem jedan račun pružatelja nije spreman, pri otvaranju glavnog dijaloga bit ćete upućeni da dodate ključeve u postavkama AI-Huba.

## Nadogradnja sa starijih "Open AI" izdanja

Ako ste koristili stariju verziju ovog dodatka:

- **Postavke** se migriraju iz starog konfiguracijskog odjeljka **`OpenAI`** u **`AIHub`**. Ne biste trebali izgubiti svoje postavke.
- **Datoteke podataka** (razgovori, spremište ključeva, privici) migriraju se iz mape **`openai`** u vašem direktoriju korisničke konfiguracije NVDA-a u **`aihub`**.

Datoteke nije potrebno ručno premještati, osim ako koristite prilagođenu postavu.

## NVDA izbornik: AI-Hub

U NVDA izborniku pronaći ćete **AI-Hub** (s instaliranom verzijom u oznaci). Stavke uključuju:

- **Dokumentacija** — otvara korisnički vodič u pregledniku (`doc\en\readme.html`).
- **Glavni dijalog…** — otvara prozor razgovora (`NVDA+G` prema zadanim postavkama).
- **Povijest razgovora…** — upravljanje spremljenim razgovorima.
- **Alati** — podizbornik koji grupira alate **OpenAI**, **Mistral**, **Google** i **Ollama** (vidi dolje).
- **GitHub repository** / **BasiliskLLM** - brze poveznice.

## Glavni dijalog

Otvorite ga s **`NVDA+G`** ili kroz **Glavni dijalog…** iz AI-Hub izbornika.

### Što možete raditi

- Razgovarajte s odabranim modelom; pregledavajte **Poruke** navigacijom tipkovnicom i kontekstnim izbornicima (npr. **j** / **k** za pomak između poruka kada je fokus u području poruka — pogledajte natuknice na zaslonu za aktivno polje).
- Dodajte **lokalne slike ili dokumente** i **URL-ove datoteka** gdje ih pružatelj podržava. Na nepodržane vrste za trenutačnog pružatelja možete dobiti upozorenje prije slanja.
- **Zalijepi (datoteku ili tekst)** iz kontekstnog izbornika upita ili **`Ctrl+V`** u upitu: dodatak može priložiti datoteke, umetnuti tekstualne putanje ili tretirati jedan URL kao privitak kada je primjereno.
- Snimajte **audio isječke**, priložite audio datoteke i koristite **TTS** za tekst upita gdje model to podržava.
- **`Escape`** zatvara glavni dijalog (kada nema blokirajućeg modalnog prozora).
- **`Ctrl+R`** uključuje/isključuje snimanje mikrofona (kada je primjenjivo).
- **`F2`** preimenuje trenutni spremljeni razgovor (nakon što postoji u pohrani).
- **`Ctrl+N`** otvara **novu** instancu glavnog dijaloga (sesiju).

### Opcije koje ovise o modelu

Neke kontrole pojavljuju se ili vrijede samo za određene modele:

- **Zaključivanje** ("thinking") za modele koji ga podržavaju; strujano zaključivanje drži se odvojeno od vidljivog odgovora kada API pruža tu razliku.
- **Razina napora zaključivanja** i povezane kontrole gdje pružatelj podržava te razine.
- **Web pretraga** samo za modele koji oglašavaju podršku za web pretragu.

Točna dostupnost mijenja se kako pružatelji ažuriraju svoje API-je; sučelje odražava **trenutačno odabrani model**.

### Sistemska uputa

Sistemska uputa usmjerava ponašanje modela. Zadano je postavljena uputa prikladna za pomoć pri pristupačnosti; možete je urediti, vratiti iz kontekstnog izbornika i po želji trajno spremiti posljednju korištenu uputu (podesivo u postavkama). Sistemska uputa troši tokene kao i svaki drugi unos.

## Povijest razgovora

Koristite **Povijest razgovora…** iz AI-Hub izbornika ili dodijelite gestu pod **Ulazne geste → AI-Hub**.

Možete popisati, otvoriti, preimenovati, obrisati i stvoriti razgovore. U glavnom dijalogu, **F2** i **Ctrl+N** pomažu u upravljanju trenutačnom sesijom.

### Automatsko spremanje

Ako je u postavkama uključeno **Automatski spremi razgovor** (zadano), dodatak sprema (ili ažurira) pohranjeni razgovor **nakon svakog dovršenog odgovora asistenta** i može trajno spremiti stanje pri zatvaranju dijaloga ako postoji nešto za spremiti. Također možete spremiti iz kontekstnog izbornika polja **Poruke**. Ako je automatsko spremanje isključeno, koristite ručno spremanje kada želite trajno spremiti.

## Postavi pitanje (glas)

Ova naredba **nema zadanu tipku**. Dodijelite je pod **Ulazne geste → AI-Hub**.

- Prvi pritisak: počinje snimanje.
- Drugi pritisak tijekom snimanja: zaustavlja snimanje i šalje.
- Ako se odgovor reproducira kao audio, pritisnite ponovno za zaustavljanje reprodukcije.

**Načini rada:**

- **Izravni audio** — ako odabrani model podržava audio ulaz, vaša snimka može se poslati kao audio bez zasebnog koraka transkripcije.
- **Prvo transkribiraj pa razgovaraj** — inače konfigurirana pozadina transkripcije obrađuje snimku, a zatim se tekst šalje modelu za razgovor.

Ako je fokus na glavnom dijalogu, koristi se njegov **trenutni model**; inače dodatak bira prikladan model među konfiguriranim pružateljima.

## Podizbornik Alati

Stavka **Alati** u AI-Hub izborniku otvara dijaloge grupirane po pružatelju (svaki može zahtijevati odgovarajući API račun):

| Područje izbornika | Alat |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Govor u tekst…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Transkripcija / Prijevod…** |
| Ollama | **Upravitelj modela…** |

Ako nijedan račun nije konfiguriran za pružatelja alata, dodatak će vas uputiti da ga dodate u postavkama AI-Huba.

## Globalne naredbe

Sve zadane geste mogu se promijeniti u **NVDA → Postavke → Ulazne geste → AI-Hub**.

| Gesta | Radnja |
|---------|--------|
| `NVDA+G` | Prikaži glavni dijalog AI-Huba |
| `NVDA+E` | Snimi zaslon i opiši (dodaje sliku u sesiju) |
| `NVDA+O` | Opiši trenutačnu regiju objekta navigatora |
| *(nema zadane geste)* | Povijest razgovora. Dodijelite u Ulazne geste → AI-Hub. |
| *(nema zadane geste)* | Postavi pitanje (snimi / pošalji / zaustavi audio). Dodijelite u Ulazne geste → AI-Hub. |
| *(nema zadane geste)* | Uključi/isključi snimanje mikrofona i transkripciju. Dodijelite u Ulazne geste → AI-Hub. |

## Gdje se podaci pohranjuju

Radne datoteke, indeks spremljenih razgovora, objedinjeni `accounts.json` i privici nalaze se u korisničkom **konfiguracijskom** direktoriju NVDA-a, u mapi **`aihub`** (nakon migracije iz `openai`). Privremene datoteke koriste podmapu `tmp` i čiste se kada je to razumno (npr. pri gašenju dodatka ili zatvaranju dijaloga).

## Potrebne ovisnosti (automatski dohvat tijekom izgradnje)

Izgradnje koriste `scons` za popunjavanje biblioteka za izvođenje pod:

`addon/globalPlugins/AIHub/libs/`

Kada nedostaje potrebna biblioteka, `scons` preuzima zaključane wheel pakete i izdvaja samo ono što je potrebno u tu mapu. Trenutačno zaključane ovisnosti su:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — izdvojeno u `libs/` za prikaz Markdowna u razgovoru.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` za:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

Direktorij `libs` namjerno je ignoriran u gitu; suradnici ne trebaju commitati preuzete artefakte.

## Rješavanje problema (kratko)

- **"Nijedan račun nije konfiguriran"** — dodajte API ključ za pružatelja kojeg ste odabrali u postavkama **AI-Huba**.
- **Pružatelj odbija privitak** — provjerite vrstu i veličinu datoteke; pokušajte drugi model ili pružatelja koji podržava medij koji vam treba.

Za prijave problema i doprinose koristite poveznicu **GitHub repozitorij** iz AI-Hub izbornika.
