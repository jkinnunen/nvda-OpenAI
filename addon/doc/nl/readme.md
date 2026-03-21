# AI Hub

Als je een aparte desktopervaring met extra workflows wilt, bekijk dan [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (standalone app plus minimale NVDA-add-on). AI Hub blijft een volledige oplossing binnen NVDA.

**AI Hub** is een NVDA-add-on die je schermlezer verbindt met meerdere LLM-API's. Je kunt ermee schrijven, samenvatten, vertalen, afbeeldingen beschrijven, vragen stellen met je stem, transcriberen en extra tools gebruiken (TTS, OCR, enz.) zonder NVDA te verlaten.

De **pakketnaam** in NVDA blijft `openai` (compatibiliteit). De **weergavenaam** in menu's en instellingen is **AI Hub**.

## Belangrijkste functies

- Chat in een hoofdvenster met geschiedenis, systeemprompt en model/account-keuze.
- Bijlagen met afbeeldingen/documenten vanuit bestanden, plus externe URL's afhankelijk van providerondersteuning.
- Slim plakken in het promptveld (`Ctrl+V`) voor bestanden, paden en enkele URL's.
- Gespreksgeschiedenis (opslaan, hernoemen, verwijderen, opnieuw openen).
- "Stel een vraag" via stem (geen standaardgebaar; toewijzen via Invoergebaren -> AI Hub).
- Globale beschrijving: screenshot (`NVDA+E`) en navigatorobjectregio (`NVDA+O`).
- Tools-submenu met provider-specifieke functies (TTS, OCR, speech-to-text, Lyria, Ollama-beheer).

## Ondersteunde providers

Configureer een of meer providers in **Voorkeuren -> Instellingen -> AI Hub**.

| Provider | Rol |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT en verwante modellen; officiele transcriptie- en TTS-tools |
| [DeepSeek](https://www.deepseek.com/) | OpenAI-compatibele DeepSeek API |
| Custom OpenAI | Elke OpenAI-compatibele HTTP-endpoint |
| Ollama | Lokale modellen via compatibele endpoint |
| [Mistral AI](https://mistral.ai/) | Mistral/Pixtral; Voxtral TTS, OCR, speech-to-text |
| [OpenRouter](https://openrouter.ai/) | Toegang tot veel modellen met een sleutel |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro |

API-sleutels kunnen ook uit omgevingsvariabelen worden gelezen (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, enz.).

## Installatie

1. Open de [releases-pagina](https://github.com/aaclause/nvda-OpenAI/releases).
2. Download de nieuwste `.nvda-addon`.
3. Installeer via **Extra -> Add-ons beheren** in NVDA.

## Build en bibliotheken

Tijdens build met `scons` worden runtime-bibliotheken automatisch geplaatst in:

`addon/globalPlugins/AIHub/libs/`

Als er iets ontbreekt, downloadt `scons` vastgepinde versies en pakt alleen het benodigde uit:

- `markdown2` `2.5.4` -> `libs/markdown2.py`
- `Pillow` `12.1.1`:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

De map `libs` staat bewust in `.gitignore`.
