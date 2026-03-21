# AI Hub

Se vuoi un'esperienza desktop dedicata con flussi aggiuntivi, vedi [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (app standalone e add-on NVDA minimale). AI Hub resta una soluzione completa dentro NVDA.

**AI Hub** e un componente aggiuntivo per NVDA che collega lo screen reader a piu API di modelli linguistici (LLM). Permette scrittura, riassunti, traduzione, descrizione immagini, domande vocali, trascrizione e strumenti opzionali (TTS, OCR, ecc.) senza uscire da NVDA.

Il **nome pacchetto** in NVDA resta `openai` (compatibilita). Il **nome visualizzato** in menu e impostazioni e **AI Hub**.

## Funzionalita principali

- Chat in una finestra principale con cronologia, prompt di sistema e selezione modello/account.
- Allegati di immagini/documenti da file e URL remoti in base al provider selezionato.
- Incolla intelligente nel prompt (`Ctrl+V`) per file, percorsi e URL.
- Cronologia conversazioni (salva, rinomina, elimina, riapri).
- Comando "fai una domanda" via voce (nessun gesto predefinito; assegnabile in Gesti di immissione -> AI Hub).
- Descrizione globale: screenshot (`NVDA+E`) e regione oggetto navigatore (`NVDA+O`).
- Sottomenu strumenti per provider (TTS, OCR, speech-to-text, Lyria, gestione Ollama).

## Provider supportati

Configura uno o piu provider in **Preferenze -> Impostazioni -> AI Hub**.

| Provider | Ruolo |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT e correlati; strumenti ufficiali trascrizione/TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek compatibile OpenAI |
| Custom OpenAI | Endpoint HTTP compatibili OpenAI |
| Ollama | Modelli locali via endpoint compatibile |
| [Mistral AI](https://mistral.ai/) | Mistral/Pixtral; Voxtral TTS, OCR, speech-to-text |
| [OpenRouter](https://openrouter.ai/) | Accesso unificato a molti modelli |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; strumento Lyria 3 Pro |

Sono supportate anche chiavi da variabili d'ambiente (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, ecc.).

## Installazione

1. Apri la [pagina release](https://github.com/aaclause/nvda-OpenAI/releases).
2. Scarica l'ultimo `.nvda-addon`.
3. Installa da **Strumenti -> Gestione componenti aggiuntivi** in NVDA.

## Build e librerie

La build con `scons` prepara automaticamente le librerie in:

`addon/globalPlugins/AIHub/libs/`

Se mancanti, `scons` scarica versioni fissate ed estrae il necessario:

- `markdown2` `2.5.4` -> `libs/markdown2.py`
- `Pillow` `12.1.1`:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

La cartella `libs` e ignorata da git.
