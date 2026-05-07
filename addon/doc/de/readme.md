Wenn du ein dediziertes Desktop-Erlebnis mit zusätzlichen Workflows möchtest, sieh dir [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) an (eigenständige App plus ein minimales NVDA-Add-on). AI-Hub bleibt eine voll ausgestattete Option innerhalb von NVDA.

# AI-Hub

**AI-Hub** ist ein NVDA-Add-on, das deinen Screenreader mit mehreren APIs für große Sprachmodelle (LLM) verbindet. Du kannst es zum Schreiben, Zusammenfassen, für Übersetzungshilfe, Vision (Bilder und Screenshots), Sprachfragen, Transkription und optionale Werkzeugdialoge (TTS, OCR und mehr) nutzen - ohne NVDA zu verlassen.

Der **Paketname** des Add-ons in NVDA ist weiterhin `openai` (zur Kompatibilität mit bestehenden Installationen). Der **Anzeigename**, den du in Menüs und Einstellungen siehst, ist **AI-Hub**.

## Funktionen auf einen Blick

- **Chat** in einem eigenen Hauptdialog mit Verlauf, Systemprompt sowie Modell- und Kontenauswahl.
- **Bilder und Dokumente** als Anhänge aus Dateien; **URLs** zu entfernten Dateien mit Typprüfungen, abgestimmt auf den **ausgewählten Anbieter**.
- **Smart Paste** im Prompt-Feld: Dateien aus der Zwischenablage, Pfade aus Text oder eine einzelne URL einfügen (auch über das Kontextmenü des Prompts verfügbar). `Ctrl+V` verwendet dieselbe Logik, wenn der Fokus im Prompt liegt.
- **Konversationsspeicherung und Verlauf** mit Umbenennen, Löschen und Wiederöffnen.
- **Frage stellen** von überall (keine Standardtaste): Weise eine Geste in **Eingabegesten → AI-Hub** zu, um aufzuzeichnen, zu senden und die Antwort zu hören oder zu lesen.
- **Globale Beschreibung**: Screenshot (`NVDA+E`) oder Bereich des Navigatorobjekts (`NVDA+O`) wird in eine Chatsitzung gesendet.
- **Tools**-Untermenü (unter NVDA → AI-Hub): anbieterspezifische Hilfsfunktionen wie TTS, OCR, Speech-to-Text, Lyria-Audio und Ollama-Modellverwaltung.
- Optionen für **Reasoning / Web search** erscheinen nur, wenn das **aktuelle Modell** sie unterstützt (je nach Anbieter unterschiedlich).

Dieses Add-on enthält **keinen** eigenen Update-Checker. **Updates** werden über den offiziellen **NVDA Add-on Store** verwaltet, wenn du von dort installierst. Wenn du manuell von der [Releases-Seite](https://github.com/aaclause/nvda-OpenAI/releases) installierst, installiere neuere `.nvda-addon`-Builds auf dieselbe Weise.

## Unterstützte Anbieter

Konfiguriere **einen oder mehrere Anbieter** in NVDA unter **Einstellungen → AI-Hub**. Jeder Anbieter kann **mehrere benannte Konten** enthalten (API-Schlüssel, optional Organisation oder Base-URL, falls zutreffend).

| Anbieter | Rolle |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT und verwandte Modelle; offizielle Dialoge für Transkription und TTS |
| [DeepSeek](https://www.deepseek.com/) | DeepSeek-API (OpenAI-kompatibel) |
| **Custom OpenAI** | Beliebige OpenAI-kompatible HTTP-API (benutzerdefinierte Base-URL + Schlüssel) |
| **Ollama** | Lokale Modelle über OpenAI-kompatiblen Endpunkt; Werkzeug zur Modellverwaltung |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; Voxtral-TTS-, OCR- und Speech-to-Text-Werkzeuge |
| [OpenRouter](https://openrouter.ai/) | Viele Drittanbieter-Modelle hinter einem Schlüssel |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro-Werkzeug |

Das Add-on kann API-Schlüssel auch aus **Umgebungsvariablen** übernehmen, wenn sie gesetzt sind (zum Beispiel `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` und weitere). Die Einstellungsoberfläche bleibt der zentrale Ort zur Kontenverwaltung.

### Speech-to-Text-Backends (Transkription)

Für **Mikrofon-/Dateitranskription** im Hauptablauf (nicht das separate OpenAI-Transkriptionstool) kannst du unter dem Abschnitt **Audio** der AI-Hub-Einstellungen zwischen **whisper_cpp** (lokal), **openai** (Whisper-API) und **mistral** wählen.

## Installation

1. Öffne die [Add-on-Releases-Seite](https://github.com/aaclause/nvda-OpenAI/releases).
2. Lade das neueste `.nvda-addon`-Paket herunter.

## Ersteinrichtung

1. Öffne **NVDA → Einstellungen**.
2. Wähle die Kategorie **AI-Hub**.
3. In **API Accounts** wähle **Add account...**.
4. Im Kontodialog wähle einen Anbieter, gib einen Kontonamen ein und fülle die Pflichtfelder aus (API-Schlüssel für die meisten Anbieter; Base-URL für **Custom OpenAI** und **Ollama**, wobei Ollama bei leerem Feld standardmäßig http://127.0.0.1:11434/v1 verwendet).
5. Speichere und füge optional weitere Konten hinzu, bearbeite bestehende oder entferne ungenutzte Konten aus der Liste.
6. Passe optional **Audio**, **Chat-Feedback**, **Erweitert** / Temperatur sowie **Konversation automatisch speichern** (standardmäßig aktiviert) an.

Bis mindestens ein Anbieter-Konto bereit ist, fordert dich das Öffnen des Hauptdialogs auf, Schlüssel in den AI-Hub-Einstellungen hinzuzufügen.

## Upgrade von älteren „Open AI“-Builds

Wenn du eine ältere Version dieses Add-ons verwendet hast:

- **Einstellungen** werden vom alten Konfigurationsabschnitt **`OpenAI`** nach **`AIHub`** migriert. Deine Einstellungen sollten nicht verloren gehen.
- **Datendateien** (Konversationen, Schlüsselspeicher, Anhänge) werden aus dem Ordner **`openai`** in deinem NVDA-Benutzerkonfigurationsverzeichnis nach **`aihub`** migriert.

Du musst Dateien nicht manuell verschieben, außer du verwendest eine benutzerdefinierte Einrichtung.

## NVDA-Menü: AI-Hub

Im NVDA-Menü findest du **AI-Hub** (mit der installierten Version im Eintrag). Einträge umfassen:

- **Documentation** - öffnet das Benutzerhandbuch im Browser (`doc\en\readme.html`).
- **Main dialog…** - öffnet das Chatfenster (standardmäßig `NVDA+G`).
- **Conversation history…** - verwalte gespeicherte Chats.
- **Tools** - Untermenü, das Hilfsfunktionen von **OpenAI**, **Mistral**, **Google** und **Ollama** gruppiert (siehe unten).
- **GitHub repository** / **BasiliskLLM** - Schnelllinks.

## Hauptdialog

Öffne ihn mit **`NVDA+G`** oder **Main dialog…** aus dem AI-Hub-Menü.

### Was du tun kannst

- Mit dem ausgewählten Modell chatten; **Messages** per Tastatur und Kontextmenüs durchsehen (z. B. **j** / **k** zum Wechseln zwischen Nachrichten, wenn der Fokus im Nachrichtenbereich liegt - siehe Hinweise auf dem Bildschirm für das aktive Feld).
- **Lokale Bilder oder Dokumente** anhängen und **Datei-URLs** hinzufügen, sofern der Anbieter sie unterstützt. Nicht unterstützte Typen für den aktuellen Anbieter werden vor dem Senden ggf. gemeldet.
- **Paste (file or text)** aus dem Kontextmenü des Prompts oder **`Ctrl+V`** im Prompt: Das Add-on kann Dateien anhängen, Textpfade einfügen oder eine einzelne URL bei Bedarf als Anhang behandeln.
- **Audio**-Snippets aufnehmen, Audiodateien anhängen und **TTS** für Prompt-Text nutzen, sofern das Modell es unterstützt.
- **`Escape`** schließt den Hauptdialog (wenn kein blockierender modaler Dialog offen ist).
- **`Ctrl+R`** schaltet die Mikrofonaufnahme um (falls anwendbar).
- **`F2`** benennt die aktuell gespeicherte Konversation um (nachdem sie im Speicher existiert).
- **`Ctrl+N`** öffnet eine **neue** Hauptdialog-Instanz (Sitzung).

### Optionen, die vom Modell abhängen

Einige Steuerelemente erscheinen nur oder gelten nur für bestimmte Modelle:

- **Reasoning** ("thinking") für Modelle, die es bereitstellen; gestreamtes Reasoning wird von der sichtbaren Antwort getrennt gehalten, wenn die API diese Unterscheidung liefert.
- **Reasoning effort** und verwandte Steuerelemente, wo der Anbieter Stufen unterstützt.
- **Web search** nur für Modelle, die Websuche unterstützen.

Die genaue Verfügbarkeit ändert sich, wenn Anbieter ihre APIs aktualisieren; die UI spiegelt das **aktuell ausgewählte Modell** wider.

### Systemprompt

Der Systemprompt steuert das Modellverhalten. Ein Standard, der für Unterstützung bei Barrierefreiheit geeignet ist, wird bereitgestellt; du kannst ihn bearbeiten, über das Kontextmenü zurücksetzen und optional den zuletzt verwendeten Prompt beibehalten (in den Einstellungen konfigurierbar). Der Systemprompt verbraucht wie jede andere Eingabe Tokens.

## Konversationsverlauf

Nutze **Conversation history…** aus dem AI-Hub-Menü oder weise eine Geste unter **Eingabegesten → AI-Hub** zu.

Du kannst Konversationen auflisten, öffnen, umbenennen, löschen und neu erstellen. Im Hauptdialog helfen **F2** und **Ctrl+N** bei der Verwaltung der aktuellen Sitzung.

### Automatisches Speichern

Wenn **Konversation automatisch speichern** in den Einstellungen aktiviert ist (Standard), speichert (oder aktualisiert) das Add-on die gespeicherte Konversation **nach jeder abgeschlossenen Assistentenantwort** und kann beim Schließen des Dialogs den Zustand sichern, wenn etwas zu speichern ist. Du kannst auch über das Kontextmenü des Felds **Messages** speichern. Ist das automatische Speichern aus, nutze manuelles Speichern, wenn du Inhalte dauerhaft sichern willst.

## Frage stellen (Sprache)

Dieser Befehl hat **keine Standardtaste**. Weise eine unter **Eingabegesten → AI-Hub** zu.

- Erster Tastendruck: Aufnahme starten.
- Zweiter Tastendruck während der Aufnahme: stoppen und senden.
- Wenn die Antwort als Audio wiedergegeben wird, erneut drücken, um die Wiedergabe zu stoppen.

**Modi:**

- **Direktes Audio** - wenn das ausgewählte Modell Audioeingabe unterstützt, kann deine Aufnahme als Audio ohne separaten Transkriptionsschritt gesendet werden.
- **Zuerst transkribieren, dann chatten** - andernfalls verarbeitet das konfigurierte Transkriptions-Backend die Aufnahme, dann wird der Text an das Chatmodell gesendet.

Wenn der Hauptdialog fokussiert ist, wird dessen **aktuelles Modell** verwendet; andernfalls wählt das Add-on ein geeignetes Modell unter den konfigurierten Anbietern.

## Untermenü Tools

Der Eintrag **Tools** unter dem AI-Hub-Menü öffnet nach Anbietern gruppierte Dialoge (jeder kann das entsprechende API-Konto erfordern):

| Menübereich | Werkzeug |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Speech to Text…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Transcription / Translation…** |
| Ollama | **Model manager…** |

Wenn für den Anbieter eines Werkzeugs kein Konto konfiguriert ist, fordert dich das Add-on auf, eines in den AI-Hub-Einstellungen hinzuzufügen.

## Globale Befehle

Alle Standardgesten können unter **NVDA → Einstellungen → Eingabegesten → AI-Hub** geändert werden.

| Geste | Aktion |
|---------|--------|
| `NVDA+G` | AI-Hub-Hauptdialog anzeigen |
| `NVDA+E` | Screenshot erstellen und beschreiben (fügt Bild einer Sitzung hinzu) |
| `NVDA+O` | Aktuellen Bereich des Navigatorobjekts beschreiben |
| *(keine Standardgeste)* | Konversationsverlauf. In Eingabegesten → AI-Hub zuweisen. |
| *(keine Standardgeste)* | Frage stellen (aufnehmen / senden / Audio stoppen). In Eingabegesten → AI-Hub zuweisen. |
| *(keine Standardgeste)* | Mikrofonaufnahme und Transkription umschalten. In Eingabegesten → AI-Hub zuweisen. |

## Wo Daten gespeichert werden

Arbeitsdateien, Index gespeicherter Konversationen, einheitliche `accounts.json` und Anhänge liegen unter deinem NVDA-**Benutzerkonfigurations**verzeichnis im Ordner **`aihub`** (nach der Migration von `openai`). Temporäre Dateien nutzen den Unterordner `tmp` und werden sinnvoll bereinigt (z. B. beim Beenden des Add-ons oder Schließen des Dialogs).

## Erforderliche Abhängigkeiten (während des Builds automatisch abgerufen)

Builds verwenden `scons`, um Laufzeitbibliotheken unter folgendem Pfad bereitzustellen:

`addon/globalPlugins/AIHub/libs/`

Wenn eine erforderliche Bibliothek fehlt, lädt `scons` angeheftete Wheels herunter und extrahiert nur das Nötige in diesen Ordner. Aktuell angeheftete Abhängigkeiten sind:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` - extrahiert nach `libs/` für das Markdown-Rendering im Chat.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` für:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

Das Verzeichnis `libs` wird absichtlich in Git ignoriert; Mitwirkende müssen keine vendorten Artefakte committen.

## Fehlerbehebung (kurz)

- **„Kein Konto konfiguriert“** - Füge einen API-Schlüssel für den in den **AI-Hub**-Einstellungen ausgewählten Anbieter hinzu.
- **Anbieter lehnt einen Anhang ab** - Prüfe Dateityp und -größe; versuche ein anderes Modell oder einen anderen Anbieter, der das benötigte Medium unterstützt.

Für Probleme und Beiträge nutze den Link **GitHub repository** im AI-Hub-Menü.
