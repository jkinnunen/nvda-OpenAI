Če želite namensko namizno izkušnjo z dodatnimi delovnimi poteki, si oglejte [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (samostojna aplikacija in minimalen dodatek za NVDA). AI Hub ostaja polno funkcionalna možnost znotraj NVDA.

# AI Hub

**AI Hub** je dodatek za NVDA, ki vaš bralnik zaslona poveže z več API-ji velikih jezikovnih modelov (LLM). Uporabljate ga lahko za pisanje, povzemanje, pomoč pri prevajanju, vid (slike in posnetke zaslona), glasovna vprašanja, prepisovanje in izbirna pogovorna okna z orodji (TTS, OCR in drugo) — brez zapuščanja NVDA.

**Ime paketa** dodatka v NVDA je še vedno `openai` (zaradi združljivosti z obstoječimi namestitvami). **Prikazno ime**, ki ga vidite v menijih in nastavitvah, je **AI Hub**.

## Funkcije na prvi pogled

- **Klepet** v namenskem glavnem pogovornem oknu z zgodovino, sistemskim pozivom in izbiro modela/računa.
- **Slike in dokumenti** kot priloge iz datotek; **URL-ji** do oddaljenih datotek s preverjanji vrste, usklajenimi z **izbranim ponudnikom**.
- **Pametno lepljenje** v polju poziva: lepljenje datotek iz odložišča, poti iz besedila ali enega URL-ja (na voljo tudi v kontekstnem meniju poziva). `Ctrl+V` uporablja isto logiko, ko je fokus v pozivu.
- **Shranjevanje pogovora in zgodovina** s preimenovanjem, brisanjem in ponovnim odpiranjem.
- **Postavi vprašanje** od koder koli (brez privzete tipke): dodelite gesto v **Vhodne geste → AI Hub** za snemanje, pošiljanje ter poslušanje ali branje odgovora.
- **Globalni opis**: posnetek zaslona (`NVDA+E`) ali območje navigatorskega predmeta (`NVDA+O`) poslano v sejo klepeta.
- Podmeni **Orodja** (pod NVDA → AI Hub): pripomočki, specifični za ponudnika, kot so TTS, OCR, govor-v-besedilo, zvok Lyria in upravljanje modelov Ollama.
- Možnosti **sklepanja / spletnega iskanja** se prikažejo le, ko jih **trenutni model** podpira (različno glede na ponudnika).

Ta dodatek **ne** vključuje lastnega preverjanja posodobitev. **Posodobitve** se obravnavajo prek **uradne trgovine dodatkov NVDA**, ko ga namestite od tam. Če nameščate ročno s [strani izdaj](https://github.com/aaclause/nvda-OpenAI/releases), na enak način namestite novejše gradnje `.nvda-addon`.

## Podprti ponudniki

V NVDA nastavite **enega ali več ponudnikov** v **Nastavitve → Nastavitve → AI Hub**. Vsak ponudnik lahko vsebuje **več poimenovanih računov** (ključi API, po potrebi tudi organizacija ali osnovni URL).

| Ponudnik | Vloga |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT in sorodni modeli; uradna orodna pogovorna okna za prepisovanje in TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek (združljiv z OpenAI) |
| **Custom OpenAI** | Kateri koli HTTP API, združljiv z OpenAI (osnovni URL po meri + ključ) |
| **Ollama** | Lokalni modeli prek končne točke, združljive z OpenAI; orodje za upravljanje modelov |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; orodja Voxtral TTS, OCR in govor-v-besedilo |
| [OpenRouter](https://openrouter.ai/) | Veliko modelov tretjih ponudnikov za enim ključem |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; orodje Lyria 3 Pro |

Dodatek lahko prevzame ključe API iz **okoljskih spremenljivk**, ko so nastavljene (na primer `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` in druge). Uporabniški vmesnik nastavitev ostaja glavno mesto za upravljanje računov.

### Zaledja za govor-v-besedilo (prepisovanje)

Za **prepisovanje mikrofona/datoteke** znotraj glavnega poteka (ne ločenega orodja OpenAI za prepisovanje) lahko v razdelku **Zvok** v nastavitvah AI Hub izbirate med **whisper_cpp** (lokalno), **openai** (API Whisper) in **mistral**.

## Namestitev

1. Odprite [stran izdaj dodatka](https://github.com/aaclause/nvda-OpenAI/releases).
2. Prenesite najnovejši paket `.nvda-addon`.

## Prva konfiguracija

1. Odprite **NVDA → Nastavitve → Nastavitve**.
2. Izberite kategorijo **AI Hub**.
3. V razdelku **API Accounts** izberite **Add account...**.
4. V pogovornem oknu računa izberite ponudnika, vnesite ime računa in izpolnite obvezna polja (API ključ za večino ponudnikov; base URL za **Custom OpenAI** in **Ollama**, pri čemer Ollama privzeto uporabi lokalni http://127.0.0.1:11434/v1, če je polje prazno).
5. Shranite, nato pa po želji dodajte več računov, uredite obstoječe ali odstranite neuporabljene s seznama.
6. Po želji prilagodite **Audio**, **Chat feedback**, **Advanced** / temperaturo in **Auto-save conversation** (privzeto omogočeno).

Dokler ni pripravljen vsaj en račun ponudnika, vas bo odpiranje glavnega pogovornega okna pozvalo, da dodate ključe v nastavitvah AI Hub.

## Nadgradnja s starejših gradenj »Open AI«

Če ste uporabljali starejšo različico tega dodatka:

- **Nastavitve** se preselijo iz starega razdelka konfiguracije **`OpenAI`** v **`AIHub`**. Vaše nastavitve se ne bi smele izgubiti.
- **Podatkovne datoteke** (pogovori, shramba ključev, priloge) se preselijo iz mape **`openai`** v vaši uporabniški konfiguracijski mapi NVDA v **`aihub`**.

Datotek vam ni treba premikati ročno, razen če uporabljate prilagojeno nastavitev.

## Meni NVDA: AI Hub

V meniju NVDA boste našli **AI Hub** (z nameščeno različico v oznaki). Vnosi vključujejo:

- **Dokumentacija** — odpre uporabniški vodnik v vašem brskalniku (`doc\en\readme.html`).
- **Glavno pogovorno okno…** — odpre okno klepeta (privzeto `NVDA+G`).
- **Zgodovina pogovorov…** — upravljanje shranjenih klepetov.
- **Orodja** — podmeni, ki združuje pripomočke **OpenAI**, **Mistral**, **Google** in **Ollama** (glejte spodaj).
- **GitHub repository** / **BasiliskLLM** - hitre povezave.

## Glavno pogovorno okno

Odprite z **`NVDA+G`** ali **Glavno pogovorno okno…** v meniju AI Hub.

### Kaj lahko naredite

- Klepetate z izbranim modelom; pregledujete **Sporočila** s tipkovnično navigacijo in kontekstnimi meniji (npr. **j** / **k** za premik med sporočili, ko je fokus v območju sporočil — glejte namige na zaslonu za aktivno polje).
- Priložite **lokalne slike ali dokumente** in dodate **URL-je datotek**, kjer jih ponudnik podpira. Nepodprte vrste za trenutnega ponudnika lahko dobite opozorilo pred pošiljanjem.
- **Lepljenje (datoteke ali besedila)** iz kontekstnega menija poziva ali **`Ctrl+V`** v pozivu: dodatek lahko priloži datoteke, vstavi besedilne poti ali en sam URL po potrebi obravnava kot prilogo.
- Posnamete zvočne izrezke, priložite zvočne datoteke in uporabite **TTS** za besedilo poziva, kjer model to podpira.
- **`Escape`** zapre glavno pogovorno okno (ko ni odprtega blokirajočega modalnega okna).
- **`Ctrl+R`** preklopi snemanje mikrofona (kjer je podprto).
- **`F2`** preimenuje trenutno shranjen pogovor (ko že obstaja v shrambi).
- **`Ctrl+N`** odpre **novo** instanco glavnega pogovornega okna (sejo).

### Možnosti, odvisne od modela

Nekateri kontrolniki se prikažejo ali veljajo le za določene modele:

- **Sklepanje** (»razmišljanje«) za modele, ki ga podpirajo; pretočno sklepanje je ločeno od vidnega odgovora, ko API podpira to razlikovanje.
- **Intenzivnost sklepanja** in sorodni kontrolniki, kjer ponudnik podpira ravni.
- **Spletno iskanje** samo za modele, ki oglašujejo podporo spletnemu iskanju.

Natančna razpoložljivost se spreminja, ko ponudniki posodabljajo svoje API-je; uporabniški vmesnik odraža **trenutno izbran model**.

### Sistemski poziv

Sistemski poziv usmerja vedenje modela. Privzeto je na voljo nastavitev, primerna za pomoč pri dostopnosti; lahko jo uredite, ponastavite iz kontekstnega menija in po želji ohranite zadnji uporabljeni poziv (to nastavite v nastavitvah). Sistemski poziv porablja žetone enako kot kateri koli drug vnos.

## Zgodovina pogovorov

Uporabite **Zgodovina pogovorov…** v meniju AI Hub ali dodelite gesto v **Vhodne geste → AI Hub**.

Lahko prikažete seznam pogovorov, jih odprete, preimenujete, izbrišete in ustvarite nove. V glavnem pogovornem oknu pri upravljanju trenutne seje pomagata **F2** in **Ctrl+N**.

### Samodejno shranjevanje

Če je v nastavitvah omogočeno **Samodejno shrani pogovor** (privzeto), dodatek shrani (ali posodobi) shranjeni pogovor **po vsakem dokončanem odgovoru pomočnika** in lahko stanje shrani tudi, ko zaprete pogovorno okno, če je kaj za shraniti. Shranite lahko tudi iz kontekstnega menija polja **Sporočila**. Če je samodejno shranjevanje izklopljeno, uporabite ročno shranjevanje, ko želite ohraniti podatke.

## Postavi vprašanje (glas)

Ta ukaz ima **brez privzete tipke**. Dodelite ga v **Vhodne geste → AI Hub**.

- Prvi pritisk: začni snemanje.
- Drugi pritisk med snemanjem: ustavi in pošlji.
- Če se odgovor predvaja kot zvok, ponovno pritisnite za ustavitev predvajanja.

**Načini:**

- **Neposreden zvok** — če izbrani model podpira zvočni vnos, je vaše snemanje lahko poslano kot zvok brez ločenega koraka prepisovanja.
- **Najprej prepiši, nato klepet** — v nasprotnem primeru konfigurirano zaledje za prepisovanje obdela snemanje, nato pa se besedilo pošlje modelu klepeta.

Če je glavno pogovorno okno v fokusu, se uporabi njegov **trenutni model**; sicer dodatek med konfiguriranimi ponudniki izbere primeren model.

## Podmeni Orodja

Vnos **Orodja** pod menijem AI Hub odpre pogovorna okna, združena po ponudnikih (vsako lahko zahteva ustrezen račun API):

| Območje menija | Orodje |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Govor v besedilo…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Prepisovanje / Prevajanje…** |
| Ollama | **Upravitelj modelov…** |

Če za ponudnika orodja ni konfiguriran račun, vam bo dodatek povedal, da ga dodate v nastavitvah AI Hub.

## Globalni ukazi

Vse privzete geste je mogoče spremeniti v **NVDA → Nastavitve → Vhodne geste → AI Hub**.

| Gesta | Dejanje |
|---------|--------|
| `NVDA+G` | Prikaži glavno pogovorno okno AI Hub |
| `NVDA+E` | Posnemi zaslon in opiši (doda sliko v sejo) |
| `NVDA+O` | Opiši trenutno območje navigatorskega predmeta |
| *(brez privzete geste)* | Zgodovina pogovorov. Dodelite v Vhodne geste → AI Hub. |
| *(brez privzete geste)* | Postavi vprašanje (snemaj / pošlji / ustavi zvok). Dodelite v Vhodne geste → AI Hub. |
| *(brez privzete geste)* | Preklopi snemanje mikrofona in prepisovanje. Dodelite v Vhodne geste → AI Hub. |

## Kje so podatki shranjeni

Delovne datoteke, indeks shranjenih pogovorov, poenoten `accounts.json` in priloge so v uporabniški konfiguracijski mapi NVDA, v mapi **`aihub`** (po preselitvi iz `openai`). Začasne datoteke uporabljajo podmapo `tmp` in se počistijo, ko je to smiselno (npr. ob zaustavitvi dodatka ali zaprtju pogovornega okna).

## Zahtevane odvisnosti (samodejno pridobljene med gradnjo)

Gradnje uporabljajo `scons` za zapolnitev izvajalnih knjižnic v:

`addon/globalPlugins/AIHub/libs/`

Ko zahtevana knjižnica manjka, `scons` prenese pripete wheel pakete in razširi le potrebne dele v to mapo. Trenutno pripete odvisnosti so:

- **[markdown2](https://pypi.org/project/markdown2/)** `2.5.4` — izvlečeno kot `libs/markdown2.py` za upodabljanje Markdowna v klepetu.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` za:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

Mapa `libs` je namenoma ignorirana v gitu; sodelavcem ni treba potrjevati vendoranih artefaktov.

## Odpravljanje težav (na kratko)

- **»Ni konfiguriranega računa«** — Dodajte ključ API za ponudnika, ki ste ga izbrali v nastavitvah **AI Hub**.
- **Ponudnik zavrne prilogo** — Preverite vrsto in velikost datoteke; poskusite drug model ali ponudnika, ki podpira medij, ki ga potrebujete.

Za težave in prispevke uporabite povezavo **GitHub repository** v meniju AI Hub.
