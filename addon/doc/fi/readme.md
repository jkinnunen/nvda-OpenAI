# AI Hub

Jos haluat erillisen työpöytäsovelluksen lisätyönkulkuihin, katso [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (itsenäinen sovellus ja kevyt NVDA-lisäosa). AI Hub on edelleen täysiverinen vaihtoehto NVDA:ssa.

**AI Hub** on NVDA-lisäosa, joka yhdistää ruudunlukijan useisiin LLM-rajapintoihin. Sillä voi kirjoittaa, tiivistää, kääntää, kuvata kuvia, kysyä äänellä, litteroida ja käyttää lisätyökaluja (TTS, OCR jne.) poistumatta NVDA:sta.

Paketin **sisäinen nimi** NVDA:ssa on edelleen `openai` (yhteensopivuus). Näkyvä nimi valikoissa ja asetuksissa on **AI Hub**.

## Keskeiset ominaisuudet

- Keskustelu erillisessä pääikkunassa: historia, järjestelmäkehote ja malli/tili-valinta.
- Kuvien ja dokumenttien liitteet tiedostoista sekä etä-URL:t valitun palveluntarjoajan tuen mukaan.
- Älykäs liittäminen kehotekenttään (`Ctrl+V`) tiedostoille, poluille ja yksittäiselle URL:lle.
- Keskusteluhistoria (tallenna, nimeä uudelleen, poista, avaa uudelleen).
- "Kysy kysymys" -äänikomento (ei oletuselettä; määritetään syöte-eleissä).
- Yleiskuvaus: kuvakaappaus (`NVDA+E`) ja navigaattoriobjektin alue (`NVDA+O`).
- Työkalut-alivalikko palveluntarjoajakohtaisille toiminnoille (TTS, OCR, speech-to-text, Lyria, Ollama).

## Tuetut palveluntarjoajat

Määritä yksi tai useampi palveluntarjoaja kohdassa **Asetukset -> AI Hub**.

| Palveluntarjoaja | Rooli |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT ja muut mallit; viralliset litterointi- ja TTS-työkalut |
| [DeepSeek](https://www.deepseek.com/) | OpenAI-yhteensopiva DeepSeek API |
| Custom OpenAI | mikä tahansa OpenAI-yhteensopiva HTTP-pääte |
| Ollama | paikalliset mallit yhteensopivan päätepisteen kautta |
| [Mistral AI](https://mistral.ai/) | Mistral/Pixtral; Voxtral TTS, OCR, speech-to-text |
| [OpenRouter](https://openrouter.ai/) | useita malleja yhdellä avaimella |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro |

API-avaimia voidaan lukea myös ympäristömuuttujista (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY` jne.).

## Asennus

1. Avaa [julkaisusivu](https://github.com/aaclause/nvda-OpenAI/releases).
2. Lataa uusin `.nvda-addon`.
3. Asenna NVDA:ssa kohdasta **Työkalut -> Lisäosien hallinta**.

## Build ja kirjastot

`scons` hakee ajonaikaiset kirjastot automaattisesti kansioon:

`addon/globalPlugins/AIHub/libs/`

Jos kirjasto puuttuu, `scons` lataa kiinnitetyt versiot ja purkaa tarvittavat tiedostot:

- `markdown2` `2.5.4` -> `libs/markdown2.py`
- `Pillow` `12.1.1`:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

`libs`-kansio on tarkoituksella git-ignorettu.
