Se desideri un'esperienza desktop dedicata con flussi di lavoro aggiuntivi, consulta [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (app standalone con un componente aggiuntivo NVDA essenziale). AI Hub rimane un'opzione completa direttamente in NVDA.

# AI Hub

**AI Hub** è un componente aggiuntivo per NVDA che collega lo screen reader a più API di modelli linguistici di grandi dimensioni (LLM). Puoi usarlo per scrivere, riassumere, ottenere aiuto nelle traduzioni, analizzare immagini (immagini e screenshot), porre domande vocali, trascrivere e usare finestre strumenti opzionali (TTS, OCR e altro), senza uscire da NVDA.

Il **nome del pacchetto** in NVDA è ancora `openai` (per compatibilità con le installazioni esistenti). Il **nome visualizzato** che vedi nei menu e nelle impostazioni è **AI Hub**.

## Funzionalità in breve

- **Chat** in una finestra principale dedicata, con cronologia, prompt di sistema e selezione di modello e account.
- **Immagini e documenti** come allegati da file; **URL** a file remoti con controlli sul tipo allineati al **provider selezionato**.
- **Incolla intelligente** nel campo prompt: incolla file dagli appunti, percorsi dal testo o un singolo URL (disponibile anche dal menu contestuale del prompt). `Ctrl+V` usa la stessa logica quando il focus è sul prompt.
- **Salvataggio delle conversazioni e cronologia** con rinomina, eliminazione e riapertura.
- **Fai una domanda** da qualsiasi punto (nessun tasto predefinito): assegna un gesto in **Gesti di immissione → AI Hub** per registrare, inviare e ascoltare o leggere la risposta.
- **Descrizione globale**: screenshot (`NVDA+E`) o regione dell'oggetto navigatore (`NVDA+O`) inviati in una sessione di chat.
- Sottomenu **Tools** (in NVDA → AI Hub): utilità specifiche del provider come TTS, OCR, speech-to-text, audio Lyria e gestione modelli Ollama.
- Le opzioni **ragionamento / ricerca web** compaiono solo quando il **modello corrente** le supporta (variano in base al provider).

Questo add-on **non** include un proprio controllo degli aggiornamenti. Gli **aggiornamenti** sono gestiti tramite lo **Store ufficiale dei componenti aggiuntivi di NVDA** quando installi da lì. Se installi manualmente dalla [pagina delle release](https://github.com/aaclause/nvda-OpenAI/releases), installa le versioni `.nvda-addon` più recenti allo stesso modo.

## Provider supportati

Configura **uno o più provider** in NVDA **Preferenze → Impostazioni → AI Hub**. Ogni provider può contenere **più account con nome** (chiavi API, organizzazione facoltativa o URL base dove applicabile).

| Provider | Ruolo |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT e modelli correlati; finestre strumenti ufficiali per trascrizione e TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek (compatibile OpenAI) |
| **Custom OpenAI** | Qualsiasi API HTTP compatibile OpenAI (URL base personalizzato + chiave) |
| **Ollama** | Modelli locali tramite endpoint compatibile OpenAI; strumento gestione modelli |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; strumenti Voxtral TTS, OCR e speech-to-text |
| [OpenRouter](https://openrouter.ai/) | Molti modelli di terze parti dietro un'unica chiave |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; strumento Lyria 3 Pro |

L'add-on può rilevare le chiavi API da **variabili d'ambiente** quando sono impostate (ad esempio `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` e altre). L'interfaccia delle impostazioni rimane comunque il punto principale per gestire gli account.

### Backend speech-to-text (trascrizione)

Per la **trascrizione da microfono/file** nel flusso principale (non nello strumento separato di trascrizione OpenAI), puoi scegliere tra **whisper_cpp** (locale), **openai** (API Whisper) e **mistral** nella sezione **Audio** delle impostazioni di AI Hub.

## Installazione

1. Apri la [pagina release dell'add-on](https://github.com/aaclause/nvda-OpenAI/releases).
2. Scarica l'ultimo pacchetto `.nvda-addon`.

## Configurazione iniziale

1. Apri **NVDA → Preferenze → Impostazioni**.
2. Seleziona la categoria **AI Hub**.
3. In **API Accounts**, scegli **Add account...**.
4. Nella finestra dell'account, scegli un provider, inserisci un nome account e compila i campi obbligatori (chiave API per la maggior parte dei provider; URL base per **Custom OpenAI** e **Ollama**, con Ollama che usa come predefinito http://127.0.0.1:11434/v1 se vuoto).
5. Salva, poi facoltativamente aggiungi altri account, modifica quelli esistenti o rimuovi quelli non usati dall'elenco.
6. Facoltativamente, regola **Audio**, **Chat feedback**, **Advanced** / temperatura e **Auto-save conversation** (attivo per impostazione predefinita).

Finché almeno un account provider non è pronto, aprendo la finestra principale ti verrà chiesto di aggiungere le chiavi nelle impostazioni di AI Hub.

## Aggiornamento da vecchie versioni “Open AI”

Se hai usato una versione precedente di questo add-on:

- Le **impostazioni** sono migrate dalla sezione legacy **`OpenAI`** a **`AIHub`**. Non dovresti perdere le preferenze.
- I **file dati** (conversazioni, archivio chiavi, allegati) sono migrati dalla cartella **`openai`** nella directory di configurazione utente di NVDA a **`aihub`**.

Non devi spostare i file manualmente, a meno che tu non usi una configurazione personalizzata.

## Menu NVDA: AI Hub

Nel menu NVDA trovi **AI Hub** (con la versione installata nell'etichetta). Le voci includono:

- **Documentazione** — apre la guida utente nel browser (`doc\en\readme.html`).
- **Finestra principale…** — apre la finestra di chat (`NVDA+G` predefinito).
- **Cronologia conversazioni…** — gestisce le chat salvate.
- **Strumenti** — sottomenu che raggruppa utilità **OpenAI**, **Mistral**, **Google** e **Ollama** (vedi sotto).
- **GitHub repository** / **BasiliskLLM** - collegamenti rapidi.

## Finestra principale

Aprila con **`NVDA+G`** oppure con **Finestra principale…** dal menu AI Hub.

### Cosa puoi fare

- Chattare con il modello selezionato; rivedere i **Messaggi** con navigazione da tastiera e menu contestuali (ad esempio **j** / **k** per passare tra i messaggi quando il focus è nell'area dei messaggi: vedi i suggerimenti a schermo per il campo attivo).
- Allegare **immagini o documenti locali** e aggiungere **URL di file** dove il provider li supporta. I tipi non supportati dal provider corrente possono essere segnalati prima dell'invio.
- **Incolla (file o testo)** dal menu contestuale del prompt, o **`Ctrl+V`** nel prompt: l'add-on può allegare file, inserire percorsi testuali o trattare un singolo URL come allegato quando opportuno.
- Registrare frammenti **audio**, allegare file audio e usare **TTS** per il testo del prompt quando il modello lo supporta.
- **`Esc`** chiude la finestra principale (quando non è aperta una finestra modale bloccante).
- **`Ctrl+R`** attiva/disattiva la registrazione del microfono (quando applicabile).
- **`F2`** rinomina la conversazione salvata corrente (dopo che esiste nell'archivio).
- **`Ctrl+N`** apre una **nuova** istanza della finestra principale (sessione).

### Opzioni che dipendono dal modello

Alcuni controlli compaiono o si applicano solo a determinati modelli:

- **Ragionamento** ("thinking") per i modelli che lo espongono; il ragionamento in streaming viene mantenuto separato dalla risposta visibile quando l'API fornisce questa distinzione.
- **Intensità del ragionamento** e controlli correlati dove il provider supporta livelli.
- **Ricerca web** solo per i modelli che dichiarano il supporto alla ricerca web.

La disponibilità esatta cambia man mano che i provider aggiornano le API; l'interfaccia riflette il **modello attualmente selezionato**.

### Prompt di sistema

Il prompt di sistema orienta il comportamento del modello. È fornito un valore predefinito adatto all'assistenza per l'accessibilità; puoi modificarlo, ripristinarlo dal menu contestuale e, facoltativamente, mantenere l'ultimo prompt usato (configurabile nelle impostazioni). Il prompt di sistema consuma token come qualsiasi altro input.

## Cronologia conversazioni

Usa **Cronologia conversazioni…** dal menu AI Hub, oppure assegna un gesto in **Gesti di immissione → AI Hub**.

Puoi elencare, aprire, rinominare, eliminare e creare conversazioni. Dalla finestra principale, **F2** e **Ctrl+N** aiutano a gestire la sessione corrente.

### Salvataggio automatico

Se **Salvataggio automatico conversazione** è attivo nelle impostazioni (predefinito), l'add-on salva (o aggiorna) la conversazione archiviata **dopo ogni risposta completata dell'assistente** e può salvare lo stato quando chiudi la finestra, se c'è qualcosa da salvare. Puoi anche salvare dal menu contestuale del campo **Messaggi**. Se il salvataggio automatico è disattivato, usa il salvataggio manuale quando vuoi mantenere la conversazione.

## Fai una domanda (voce)

Questo comando **non ha un tasto predefinito**. Assegnane uno in **Gesti di immissione → AI Hub**.

- Prima pressione: avvia la registrazione.
- Seconda pressione durante la registrazione: interrompe e invia.
- Se la risposta viene riprodotta come audio, premi di nuovo per fermare la riproduzione.

**Modalità:**

- **Audio diretto** — se il modello selezionato supporta input audio, la registrazione può essere inviata come audio senza un passaggio di trascrizione separato.
- **Trascrivi e poi chatta** — altrimenti il backend di trascrizione configurato elabora la registrazione e poi il testo viene inviato al modello di chat.

Se la finestra principale ha il focus, viene usato il suo **modello corrente**; altrimenti l'add-on sceglie un modello adatto tra i provider configurati.

## Sottomenu Strumenti

La voce **Strumenti** nel menu AI Hub apre finestre raggruppate per provider (ognuna può richiedere il relativo account API):

| Area menu | Strumento |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Speech to Text…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Trascrizione / Traduzione…** |
| Ollama | **Gestione modelli…** |

Se non è configurato alcun account per il provider di uno strumento, l'add-on ti chiederà di aggiungerlo nelle impostazioni di AI Hub.

## Comandi globali

Tutti i gesti predefiniti possono essere modificati in **NVDA → Preferenze → Gesti di immissione → AI Hub**.

| Gesto | Azione |
|---------|--------|
| `NVDA+G` | Mostra la finestra principale di AI Hub |
| `NVDA+E` | Screenshot e descrizione (aggiunge l'immagine a una sessione) |
| `NVDA+O` | Descrivi la regione dell'oggetto navigatore corrente |
| *(nessun gesto predefinito)* | Cronologia conversazioni. Assegnalo in Gesti di immissione → AI Hub. |
| *(nessun gesto predefinito)* | Fai una domanda (registra / invia / ferma audio). Assegnalo in Gesti di immissione → AI Hub. |
| *(nessun gesto predefinito)* | Attiva/disattiva registrazione microfono e trascrizione. Assegnalo in Gesti di immissione → AI Hub. |

## Dove sono archiviati i dati

I file di lavoro, l'indice delle conversazioni salvate, il file unificato `accounts.json` e gli allegati si trovano nella directory di **configurazione utente** di NVDA, nella cartella **`aihub`** (dopo la migrazione da `openai`). I file temporanei usano una sottocartella `tmp` e vengono eliminati quando possibile (ad esempio alla chiusura dell'add-on o della finestra principale).

## Dipendenze richieste (recuperate automaticamente durante la build)

Le build usano `scons` per popolare le librerie runtime in:

`addon/globalPlugins/AIHub/libs/`

Quando manca una libreria richiesta, `scons` scarica wheel con versione fissata ed estrae solo ciò che serve in quella cartella. Le dipendenze fissate attuali sono:

- **[markdown2](https://pypi.org/project/markdown2/)** `2.5.4` — estratto come `libs/markdown2.py` per il rendering Markdown della chat.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` per:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

La directory `libs` è intenzionalmente ignorata da git; chi contribuisce non deve versionare artefatti forniti tramite vendoring.

## Risoluzione problemi (breve)

- **"Nessun account configurato"** — aggiungi una chiave API per il provider selezionato nelle impostazioni **AI Hub**.
- **Il provider rifiuta un allegato** — controlla tipo e dimensione del file; prova un altro modello o provider che supporti il contenuto multimediale necessario.

Per problemi e contributi, usa il link al **repository GitHub** dal menu AI Hub.
