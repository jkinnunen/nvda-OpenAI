Jeśli potrzebujesz osobnej aplikacji desktopowej z dodatkowymi przepływami pracy, zobacz [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (samodzielna aplikacja oraz minimalny dodatek do NVDA). AI Hub nadal pozostaje w pełni funkcjonalną opcją działającą bezpośrednio w NVDA.

# AI Hub

**AI Hub** to dodatek do NVDA, który łączy czytnik ekranu z wieloma interfejsami API dużych modeli językowych (LLM). Możesz używać go do pisania, streszczania, wsparcia tłumaczeń, analizy obrazu (zdjęć i zrzutów ekranu), zadawania pytań głosowych, transkrypcji oraz opcjonalnych okien narzędziowych (TTS, OCR i innych) — bez wychodzenia z NVDA.

**Nazwa pakietu** dodatku w NVDA nadal brzmi `openai` (dla zgodności z istniejącymi instalacjami). **Nazwa wyświetlana** w menu i ustawieniach to **AI Hub**.

## Funkcje w skrócie

- **Czat** w dedykowanym głównym oknie dialogowym z historią, promptem systemowym oraz wyborem modelu i konta.
- **Obrazy i dokumenty** jako załączniki z plików; **adresy URL** do plików zdalnych ze sprawdzaniem typu zgodnym z **wybranym dostawcą**.
- **Inteligentne wklejanie** w polu promptu: wklejanie plików ze schowka, ścieżek z tekstu albo pojedynczego adresu URL (dostępne także z menu kontekstowego promptu). `Ctrl+V` używa tej samej logiki, gdy fokus znajduje się w polu promptu.
- **Zapisywanie rozmów i historia** z możliwością zmiany nazwy, usuwania i ponownego otwierania.
- **Zadaj pytanie** z dowolnego miejsca (bez domyślnego skrótu): przypisz gest w **Gesty wprowadzania → AI Hub**, aby nagrać i wysłać pytanie, a następnie odsłuchać lub odczytać odpowiedź.
- **Globalny opis**: zrzut ekranu (`NVDA+E`) albo obszar obiektu nawigatora (`NVDA+O`) wysyłany do sesji czatu.
- Podmenu **Narzędzia** (w NVDA → AI Hub): narzędzia specyficzne dla dostawcy, takie jak TTS, OCR, mowa na tekst, dźwięk Lyria i zarządzanie modelami Ollama.
- Opcje **Reasoning / Web search** pojawiają się tylko wtedy, gdy obsługuje je **bieżący model** (zależy to od dostawcy).

Ten dodatek **nie** ma własnego mechanizmu sprawdzania aktualizacji. Jeśli instalujesz go ze **Sklepu dodatków NVDA**, **aktualizacje** obsługuje oficjalny sklep. Jeśli instalujesz ręcznie ze [strony wydań](https://github.com/aaclause/nvda-OpenAI/releases), nowsze pakiety `.nvda-addon` instaluj w ten sam sposób.

## Obsługiwani dostawcy

Skonfiguruj **jednego lub więcej dostawców** w NVDA: **Preferencje → Ustawienia → AI Hub**. Każdy dostawca może mieć **wiele nazwanych kont** (klucze API oraz, tam gdzie to dotyczy, opcjonalną organizację lub bazowy adres URL).

| Dostawca | Rola |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT i pokrewne modele; oficjalne okna narzędziowe transkrypcji i TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek (zgodne z OpenAI) |
| **Custom OpenAI** | Dowolne API HTTP zgodne z OpenAI (własny bazowy adres URL + klucz) |
| **Ollama** | Modele lokalne przez punkt końcowy zgodny z OpenAI; narzędzie menedżera modeli |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; narzędzia Voxtral TTS, OCR i mowa na tekst |
| [OpenRouter](https://openrouter.ai/) | Wiele modeli firm trzecich pod jednym kluczem |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; narzędzie Lyria 3 Pro |

Dodatek może pobierać klucze API ze **zmiennych środowiskowych**, jeśli są ustawione (na przykład `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` i inne). Głównym miejscem zarządzania kontami nadal pozostaje interfejs ustawień.

### Mechanizmy mowy na tekst (transkrypcja)

W przypadku **transkrypcji z mikrofonu lub pliku** w głównym przepływie (nie w oddzielnym narzędziu transkrypcji OpenAI) możesz wybrać **whisper_cpp** (lokalnie), **openai** (API Whisper) albo **mistral** w sekcji **Audio** ustawień AI Hub.

## Instalacja

1. Otwórz [stronę wydań dodatku](https://github.com/aaclause/nvda-OpenAI/releases).
2. Pobierz najnowszy pakiet `.nvda-addon`.

## Konfiguracja przy pierwszym uruchomieniu

1. Otwórz **NVDA → Preferencje → Ustawienia**.
2. Wybierz kategorię **AI Hub**.
3. W sekcji **API Accounts** wybierz **Add account...**.
4. W oknie konta wybierz dostawcę, wpisz nazwę konta i uzupełnij wymagane pola (klucz API dla większości dostawców; base URL dla **Custom OpenAI** i **Ollama**, a Ollama domyślnie używa lokalnego http://127.0.0.1:11434/v1, gdy pole jest puste).
5. Zapisz, a następnie opcjonalnie dodaj kolejne konta, edytuj istniejące lub usuń nieużywane z listy.
6. Opcjonalnie dostosuj **Audio**, **Chat feedback**, **Advanced** / temperaturę oraz **Auto-save conversation** (domyślnie włączone).

Dopóki nie skonfigurujesz co najmniej jednego konta dostawcy, przy otwarciu głównego okna dialogowego zobaczysz prośbę o dodanie kluczy w ustawieniach AI Hub.

## Aktualizacja ze starszych wersji „Open AI”

Jeśli używałeś starszej wersji tego dodatku:

- **Ustawienia** są migrowane ze starszej sekcji konfiguracji **`OpenAI`** do **`AIHub`**. Preferencje powinny zostać zachowane.
- **Pliki danych** (rozmowy, magazyn kluczy, załączniki) są migrowane z folderu **`openai`** w katalogu konfiguracji użytkownika NVDA do folderu **`aihub`**.

Nie musisz przenosić plików ręcznie, chyba że korzystasz z niestandardowej konfiguracji.

## Menu NVDA: AI Hub

W menu NVDA znajdziesz pozycję **AI Hub** (z numerem zainstalowanej wersji w etykiecie). Zawiera ona m.in.:

- **Documentation** — otwiera przewodnik użytkownika w przeglądarce (`doc\en\readme.html`).
- **Main dialog…** — otwiera okno czatu (domyślnie `NVDA+G`).
- **Conversation history…** — pozwala zarządzać zapisanymi czatami.
- **Tools** — podmenu grupujące narzędzia **OpenAI**, **Mistral**, **Google** i **Ollama** (patrz poniżej).
- **GitHub repository** / **BasiliskLLM** - szybkie linki.

## Główne okno dialogowe

Otwórz je skrótem **`NVDA+G`** albo przez **Main dialog…** z menu AI Hub.

### Co możesz zrobić

- Czatuj z wybranym modelem; przeglądaj **Messages** za pomocą klawiatury i menu kontekstowych (np. **j** / **k**, aby przechodzić między wiadomościami, gdy fokus jest w obszarze wiadomości — zobacz podpowiedzi ekranowe dla aktywnego pola).
- Dołączaj **lokalne obrazy lub dokumenty** i dodawaj **adresy URL plików**, gdy dostawca je obsługuje. Przed wysłaniem może pojawić się ostrzeżenie o typach nieobsługiwanych przez aktualnego dostawcę.
- Używaj **Paste (file or text)** z menu kontekstowego promptu albo **`Ctrl+V`** w polu promptu: dodatek może dołączać pliki, wstawiać ścieżki tekstowe albo traktować pojedynczy adres URL jako załącznik, gdy jest to właściwe.
- Nagrywaj fragmenty **audio**, dołączaj pliki audio i używaj **TTS** dla tekstu promptu tam, gdzie obsługuje to model.
- **`Escape`** zamyka główne okno dialogowe (gdy nie jest otwarte blokujące okno modalne).
- **`Ctrl+R`** przełącza nagrywanie mikrofonu (gdy ma zastosowanie).
- **`F2`** zmienia nazwę bieżącej zapisanej rozmowy (po jej zapisaniu w magazynie).
- **`Ctrl+N`** otwiera **nową** instancję głównego okna dialogowego (sesję).

### Opcje zależne od modelu

Niektóre kontrolki pojawiają się lub działają tylko dla wybranych modeli:

- **Reasoning** („thinking”) dla modeli, które udostępniają tę funkcję; strumieniowane rozumowanie jest oddzielone od widocznej odpowiedzi, gdy API udostępnia takie rozróżnienie.
- **Reasoning effort** i powiązane kontrolki tam, gdzie dostawca obsługuje poziomy wysiłku rozumowania.
- **Web search** tylko dla modeli, które deklarują obsługę wyszukiwania w sieci.

Dokładna dostępność zmienia się wraz z aktualizacjami API dostawców; interfejs zawsze odzwierciedla **aktualnie wybrany model**.

### Prompt systemowy

Prompt systemowy steruje zachowaniem modelu. Domyślnie dostępny jest prompt dostosowany do wsparcia dostępności; możesz go edytować, przywrócić z menu kontekstowego oraz opcjonalnie zapisywać ostatnio użyty prompt (konfigurowalne w ustawieniach). Prompt systemowy zużywa tokeny tak jak każde inne wejście.

## Historia rozmów

Użyj **Conversation history…** z menu AI Hub albo przypisz gest w **Gesty wprowadzania → AI Hub**.

Możesz wyświetlać listę rozmów, otwierać je, zmieniać ich nazwy, usuwać i tworzyć nowe. W głównym oknie skróty **F2** i **Ctrl+N** pomagają zarządzać bieżącą sesją.

### Auto-save

Jeśli w ustawieniach włączone jest **Auto-save conversation** (domyślnie), dodatek zapisuje (lub aktualizuje) przechowywaną rozmowę **po każdej ukończonej odpowiedzi asystenta** i może zapisać stan podczas zamykania okna dialogowego, jeśli jest co zapisać. Możesz też zapisać rozmowę z menu kontekstowego pola **Messages**. Jeśli autozapis jest wyłączony, użyj zapisu ręcznego, gdy chcesz coś zachować.

## Zadaj pytanie (głos)

To polecenie **nie ma domyślnego skrótu**. Przypisz go w **Gesty wprowadzania → AI Hub**.

- Pierwsze naciśnięcie: rozpocznij nagrywanie.
- Drugie naciśnięcie podczas nagrywania: zatrzymaj i wyślij.
- Jeśli odpowiedź jest odtwarzana jako audio, naciśnij ponownie, aby zatrzymać odtwarzanie.

**Tryby:**

- **Direct audio** — jeśli wybrany model obsługuje wejście audio, nagranie może zostać wysłane jako audio bez osobnego etapu transkrypcji.
- **Transcribe then chat** — w przeciwnym razie skonfigurowany backend transkrypcji przetwarza nagranie, a następnie tekst jest wysyłany do modelu czatu.

Jeśli fokus znajduje się w głównym oknie dialogowym, używany jest jego **bieżący model**; w przeciwnym razie dodatek wybiera odpowiedni model spośród skonfigurowanych dostawców.

## Podmenu Narzędzia

Pozycja **Tools** w menu AI Hub otwiera okna dialogowe pogrupowane według dostawców (każde z nich może wymagać odpowiedniego konta API):

| Obszar menu | Narzędzie |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Speech to Text…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Transcription / Translation…** |
| Ollama | **Model manager…** |

Jeśli konto dostawcy wymaganego przez narzędzie nie jest skonfigurowane, dodatek poinformuje o konieczności dodania go w ustawieniach AI Hub.

## Polecenia globalne

Wszystkie domyślne gesty można zmienić w **NVDA → Preferencje → Gesty wprowadzania → AI Hub**.

| Gest | Działanie |
|---------|--------|
| `NVDA+G` | Pokaż główne okno dialogowe AI Hub |
| `NVDA+E` | Zrzut ekranu i opis (dodaje obraz do sesji) |
| `NVDA+O` | Opisz bieżący obszar obiektu nawigatora |
| *(brak domyślnego gestu)* | Historia rozmów. Przypisz w Gesty wprowadzania → AI Hub. |
| *(brak domyślnego gestu)* | Zadaj pytanie (nagraj / wyślij / zatrzymaj audio). Przypisz w Gesty wprowadzania → AI Hub. |
| *(brak domyślnego gestu)* | Przełącz nagrywanie mikrofonu i transkrypcję. Przypisz w Gesty wprowadzania → AI Hub. |

## Gdzie przechowywane są dane

Pliki robocze, indeks zapisanych rozmów, ujednolicony `accounts.json` i załączniki są przechowywane w katalogu **konfiguracji użytkownika** NVDA, w folderze **`aihub`** (po migracji z `openai`). Pliki tymczasowe używają podfolderu `tmp` i są czyszczone, gdy ma to uzasadnienie (np. podczas zamykania dodatku lub okna dialogowego).

## Wymagane zależności (automatycznie pobierane podczas budowania)

Kompilacje używają `scons` do uzupełniania bibliotek uruchomieniowych w:

`addon/globalPlugins/AIHub/libs/`

Gdy brakuje wymaganej biblioteki, `scons` pobiera przypięte pakiety wheel i wyodrębnia do tego folderu tylko to, co potrzebne. Obecnie przypięte zależności to:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — wyodrębniany do `libs/` do renderowania Markdownu czatu.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` dla:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

Katalog `libs` jest celowo ignorowany przez git; współtwórcy nie muszą commitować do repozytorium zewnętrznych artefaktów.

## Rozwiązywanie problemów (krótko)

- **„Brak skonfigurowanego konta”** — Dodaj klucz API dla wybranego dostawcy w ustawieniach **AI Hub**.
- **Dostawca odrzuca załącznik** — Sprawdź typ i rozmiar pliku; wypróbuj inny model lub dostawcę, który obsługuje potrzebne media.

Do zgłaszania problemów i przesyłania wkładu użyj łącza **GitHub repository** z menu AI Hub.
