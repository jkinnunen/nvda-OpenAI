Als je een aparte desktopervaring met extra workflows wilt, kijk dan naar [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (een zelfstandige app met een minimale NVDA-add-on). AI-Hub blijft een volwaardige optie binnen NVDA.

# AI-Hub

**AI-Hub** is een NVDA-add-on die je schermlezer verbindt met meerdere API's voor grote taalmodellen (LLM's). Je kunt hem gebruiken voor schrijven, samenvatten, vertaalhulp, beeldanalyse (afbeeldingen en schermafbeeldingen), gesproken vragen, transcriptie en optionele tooldialogen (TTS, OCR en meer) - zonder NVDA te verlaten.

De **pakketnaam** van de add-on in NVDA is nog steeds `openai` (voor compatibiliteit met bestaande installaties). De **weergavenaam** die je in menu's en instellingen ziet, is **AI-Hub**.

## Functies in een oogopslag

- **Chatten** in een apart hoofdvenster met geschiedenis, systeemprompt en model-/accountselectie.
- **Afbeeldingen en documenten** als bijlagen uit bestanden; **URL's** naar externe bestanden met typecontroles afgestemd op de **geselecteerde provider**.
- **Slim plakken** in het promptveld: plak bestanden vanaf het klembord, paden uit tekst of een enkele URL (ook beschikbaar via het contextmenu van de prompt). `Ctrl+V` gebruikt dezelfde logica wanneer de prompt focus heeft.
- **Gespreksopslag en geschiedenis** met hernoemen, verwijderen en opnieuw openen.
- **Stel een vraag** vanaf elke plek (geen standaardtoets): wijs een gebaar toe in **Invoergebaren → AI-Hub** om op te nemen, te verzenden en het antwoord te horen of te lezen.
- **Globaal beschrijven**: schermafbeelding (`NVDA+E`) of regio van het navigatorobject (`NVDA+O`) wordt naar een chatsessie gestuurd.
- **Tools**-submenu (onder NVDA → AI-Hub): providerspecifieke hulpmiddelen zoals TTS, OCR, spraak-naar-tekst, Lyria-audio en Ollama-modelbeheer.
- **Reasoning / Web search**-opties verschijnen alleen wanneer het **huidige model** deze ondersteunt (verschilt per provider).

Deze add-on heeft **geen** eigen updatecontrole. **Updates** verlopen via de **officiële Add-on Store van NVDA** wanneer je daarvandaan installeert. Als je handmatig installeert via de [releases-pagina](https://github.com/aaclause/nvda-OpenAI/releases), installeer je nieuwere `.nvda-addon`-builds op dezelfde manier.

## Ondersteunde providers

Configureer **één of meer providers** in NVDA via **Voorkeuren → Instellingen → AI-Hub**. Elke provider kan **meerdere benoemde accounts** bevatten (API-sleutels en, waar van toepassing, een optionele organisatie of basis-URL).

| Provider | Rol |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT en verwante modellen; officiële transcriptie- en TTS-tooldialogen |
| [DeepSeek](https://www.deepseek.com/) | DeepSeek API (OpenAI-compatibel) |
| **Custom OpenAI** | Elke OpenAI-compatibele HTTP API (aangepaste basis-URL + sleutel) |
| **Ollama** | Lokale modellen via een OpenAI-compatibel eindpunt; tool voor modelbeheer |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; Voxtral TTS-, OCR- en spraak-naar-teksttools |
| [OpenRouter](https://openrouter.ai/) | Veel modellen van derden achter één sleutel |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro-tool |

De add-on kan API-sleutels ophalen uit **omgevingsvariabelen** wanneer die zijn ingesteld (bijvoorbeeld `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` en andere). De instellingeninterface blijft de belangrijkste plek om accounts te beheren.

### Backends voor spraak-naar-tekst (transcriptie)

Voor **microfoon-/bestandstranscriptie** binnen de hoofdworkflow (niet de aparte OpenAI-transcriptietool) kun je in de sectie **Audio** van de AI-Hub-instellingen kiezen uit **whisper_cpp** (lokaal), **openai** (Whisper API) en **mistral**.

## Installatie

1. Open de [releases-pagina van de add-on](https://github.com/aaclause/nvda-OpenAI/releases).
2. Download het nieuwste `.nvda-addon`-pakket.

## Eerste configuratie

1. Open **NVDA → Voorkeuren → Instellingen**.
2. Selecteer de categorie **AI-Hub**.
3. Kies bij **API Accounts** voor **Add account...**.
4. Kies in het accountvenster een provider, voer een accountnaam in en vul de verplichte velden in (API-sleutel voor de meeste providers; basis-URL voor **Custom OpenAI** en **Ollama**, waarbij Ollama standaard http://127.0.0.1:11434/v1 gebruikt als dit veld leeg is).
5. Sla op en voeg optioneel meer accounts toe, bewerk bestaande accounts of verwijder ongebruikte accounts uit de lijst.
6. Pas optioneel **Audio**, **Chat feedback**, **Advanced** / temperatuur en **Auto-save conversation** (standaard ingeschakeld) aan.

Totdat minstens één provideraccount is ingesteld, vraagt het hoofdvenster je om sleutels toe te voegen in de AI-Hub-instellingen.

## Upgraden vanaf oudere "Open AI"-builds

Als je een oudere versie van deze add-on gebruikte:

- **Instellingen** worden gemigreerd van de oude configuratiesectie **`OpenAI`** naar **`AIHub`**. Je voorkeuren zouden behouden moeten blijven.
- **Gegevensbestanden** (gesprekken, sleutelopslag, bijlagen) worden gemigreerd van de map **`openai`** in je NVDA-gebruikersconfiguratiemap naar **`aihub`**.

Je hoeft bestanden niet handmatig te verplaatsen, tenzij je een aangepaste configuratie gebruikt.

## NVDA-menu: AI-Hub

In het NVDA-menu vind je **AI-Hub** (met de geïnstalleerde versie in het label). De items zijn onder andere:

- **Documentatie** — opent de gebruikershandleiding in je browser (`doc\en\readme.html`).
- **Hoofdvenster…** — opent het chatvenster (standaard `NVDA+G`).
- **Gespreksgeschiedenis…** — beheer opgeslagen chats.
- **Tools** — submenu dat hulpmiddelen voor **OpenAI**, **Mistral**, **Google** en **Ollama** groepeert (zie hieronder).
- **GitHub repository** / **BasiliskLLM** - snelle links.

## Hoofdvenster

Open met **`NVDA+G`** of **Hoofdvenster…** vanuit het AI-Hub-menu.

### Wat je kunt doen

- Chat met het geselecteerde model; bekijk **Berichten** met toetsenbordnavigatie en contextmenu's (bijv. **j** / **k** om tussen berichten te bewegen wanneer de focus in het berichtengebied staat - zie hints op het scherm voor het actieve veld).
- Voeg **lokale afbeeldingen of documenten** toe en voeg **bestands-URL's** toe waar de provider dit ondersteunt. Niet-ondersteunde typen voor de huidige provider kunnen vóór verzending worden gemeld.
- **Plakken (bestand of tekst)** vanuit het contextmenu van de prompt, of **`Ctrl+V`** in de prompt: de add-on kan bestanden als bijlage toevoegen, tekstpaden invoegen of één URL als bijlage behandelen waar dat passend is.
- Neem **audiofragmenten** op, voeg audiobestanden toe en gebruik **TTS** voor prompttekst waar het model dat ondersteunt.
- **`Escape`** sluit het hoofdvenster (wanneer er geen blokkerend modaal venster open is).
- **`Ctrl+R`** schakelt microfoonopname in/uit (waar van toepassing).
- **`F2`** hernoemt het huidige opgeslagen gesprek (nadat het in opslag bestaat).
- **`Ctrl+N`** opent een **nieuwe** instantie van het hoofdvenster (sessie).

### Opties die afhankelijk zijn van het model

Sommige bedieningselementen verschijnen alleen bij bepaalde modellen of zijn alleen daarop van toepassing:

- **Reasoning** ("nadenken") voor modellen die dit bieden; gestreamde reasoning blijft gescheiden van het zichtbare antwoord wanneer de API dat onderscheid ondersteunt.
- **Reasoning effort** en verwante instellingen waar de provider niveaus ondersteunt.
- **Web search** alleen voor modellen die ondersteuning voor web search aangeven.

De exacte beschikbaarheid verandert wanneer providers hun API's bijwerken; de interface weerspiegelt het **momenteel geselecteerde model**.

### Systeemprompt

De systeemprompt stuurt het gedrag van het model. Er is een standaardprompt meegeleverd die geschikt is voor toegankelijkheidsondersteuning; je kunt deze bewerken, via het contextmenu herstellen en optioneel de laatst gebruikte prompt bewaren (instelbaar in de instellingen). De systeemprompt verbruikt tokens zoals elke andere invoer.

## Gespreksgeschiedenis

Gebruik **Gespreksgeschiedenis…** vanuit het AI-Hub-menu, of wijs een gebaar toe onder **Invoergebaren → AI-Hub**.

Je kunt gesprekken bekijken, openen, hernoemen, verwijderen en aanmaken. Vanuit het hoofdvenster helpen **F2** en **Ctrl+N** je bij het beheren van de huidige sessie.

### Automatisch opslaan

Als **Gesprek automatisch opslaan** is ingeschakeld in de instellingen (standaard), slaat de add-on het opgeslagen gesprek op (of werkt het bij) **na elk voltooid antwoord van de assistent**, en kan de status worden opgeslagen wanneer je het venster sluit als er iets op te slaan is. Je kunt ook opslaan via het contextmenu van het veld **Berichten**. Als automatisch opslaan uit staat, gebruik dan handmatig opslaan wanneer je iets blijvend wilt bewaren.

## Stel een vraag (spraak)

Deze opdracht heeft **geen standaardtoets**. Wijs er een toe onder **Invoergebaren → AI-Hub**.

- Eerste keer indrukken: opname starten.
- Tweede keer indrukken tijdens opname: stoppen en verzenden.
- Als het antwoord als audio wordt afgespeeld, druk dan opnieuw om het afspelen te stoppen.

**Modi:**

- **Directe audio** — als het geselecteerde model audio-invoer ondersteunt, kan je opname als audio worden verzonden zonder aparte transcriptiestap.
- **Eerst transcriberen, daarna chatten** — anders verwerkt de geconfigureerde transcriptie-backend de opname en wordt daarna de tekst naar het chatmodel gestuurd.

Als het hoofdvenster focus heeft, wordt het **huidige model** daarvan gebruikt; anders kiest de add-on een geschikt model uit de geconfigureerde providers.

## Tools-submenu

Het item **Tools** onder het AI-Hub-menu opent per provider gegroepeerde dialogen (elk kan het bijbehorende API-account vereisen):

| Menugebied | Tool |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Spraak naar tekst…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Transcriptie / Vertaling…** |
| Ollama | **Modelbeheer…** |

Als er geen account is geconfigureerd voor de provider van een tool, meldt de add-on dat je er een moet toevoegen in de AI-Hub-instellingen.

## Globale opdrachten

Alle standaardgebaren kunnen worden aangepast in **NVDA → Voorkeuren → Invoergebaren → AI-Hub**.

| Gebaar | Actie |
|---------|--------|
| `NVDA+G` | Het AI-Hub-hoofdvenster tonen |
| `NVDA+E` | Schermafbeelding maken en beschrijven (voegt afbeelding toe aan een sessie) |
| `NVDA+O` | De huidige navigatorobjectregio beschrijven |
| *(geen standaardgebaar)* | Gespreksgeschiedenis. Toewijzen in Invoergebaren → AI-Hub. |
| *(geen standaardgebaar)* | Stel een vraag (opnemen / verzenden / audio stoppen). Toewijzen in Invoergebaren → AI-Hub. |
| *(geen standaardgebaar)* | Microfoonopname en transcriptie in-/uitschakelen. Toewijzen in Invoergebaren → AI-Hub. |

## Waar gegevens worden opgeslagen

Werkbestanden, de index van opgeslagen gesprekken, het uniforme `accounts.json` en bijlagen staan in je NVDA-map voor **gebruikersconfiguratie**, in de map **`aihub`** (na migratie vanaf `openai`). Tijdelijke bestanden gebruiken een submap `tmp` en worden waar mogelijk opgeruimd (bijv. bij het beëindigen van de add-on of het sluiten van het venster).

## Vereiste afhankelijkheden (automatisch opgehaald tijdens de build)

Builds gebruiken `scons` om runtimebibliotheken te vullen onder:

`addon/globalPlugins/AIHub/libs/`

Wanneer een vereiste bibliotheek ontbreekt, downloadt `scons` vastgepinde wheels en pakt alleen uit wat nodig is in die map. De huidige vastgepinde afhankelijkheden zijn:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — uitgepakt in `libs/` voor Markdown-weergave in de chat.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` voor:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

De map `libs` staat bewust in `.gitignore`; bijdragers hoeven meegeleverde artefacten niet te committen.

## Probleemoplossing (kort)

- **"Geen account geconfigureerd"** - voeg een API-sleutel toe voor de provider die je hebt geselecteerd in de **AI-Hub**-instellingen.
- **Provider weigert een bijlage** - controleer bestandstype en -grootte; probeer een ander model of een andere provider die de media ondersteunt die je nodig hebt.

Gebruik voor problemen en bijdragen de koppeling naar de **GitHub-repository** vanuit het AI-Hub-menu.
