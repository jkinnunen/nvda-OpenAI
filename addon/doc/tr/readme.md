# AI Hub

Daha fazla ek iş akisi sunan ayri bir masaustu deneyimi isterseniz [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) projesine bakin (bagimsiz uygulama + minimal NVDA eklentisi). AI Hub ise NVDA icinde tam ozellikli bir secenektir.

**AI Hub**, ekran okuyucunuzu birden cok buyuk dil modeli (LLM) API'sine baglayan bir NVDA eklentisidir. Yazma, ozetleme, ceviri yardimi, goruntu betimleme (resimler ve ekran goruntuleri), sesli soru, transkripsiyon ve istege bagli araclar (TTS, OCR vb.) icin NVDA'dan cikmadan kullanabilirsiniz.

NVDA icindeki **paket adi** hala `openai`'dir (mevcut kurulumlarla uyumluluk icin). Menu ve ayarlarda gordugunuz **gosterim adi** ise **AI Hub**'dir.

## Ozellikler

- Sistem istemi, gecmis ve model/hesap secimi olan ayri bir ana pencerede **sohbet**.
- Dosyadan **gorsel ve belge** ekleri; secili saglayiciya uygun tur denetimiyle uzak dosya **URL** ekleme.
- Istem alaninda **akilli yapistirma**: panodan dosya, metinden yol veya tek URL (baglam menusu ile de). Odak istem alanindayken `Ctrl+V` ayni mantigi kullanir.
- **Konusma gecmisi**: kaydetme, yeniden adlandirma, silme ve tekrar acma.
- Her yerden **soru sor** ozelligi (varsayilan kisayol yok): **Girdi Hareketleri -> AI Hub** altindan hareket atayarak kaydetme, gonderme ve yaniti dinleme/okuma.
- **Global betimleme**: ekran goruntusu (`NVDA+E`) veya gezgin nesnesi bolgesi (`NVDA+O`) bir sohbet oturumuna gonderilir.
- **Araclar** alt menusu (NVDA -> AI Hub): saglayiciya ozel TTS, OCR, speech-to-text, Lyria audio ve Ollama model yonetimi gibi araclar.
- **Reasoning / web search** secenekleri yalnizca secili model destekliyorsa gorunur.

Bu eklentide dahili guncelleme denetleyicisi **yoktur**. **Guncellemeler**, eger eklentiyi oradan kurduysaniz, **resmi NVDA Eklenti Magazasi** uzerinden gelir. Elle kurulum yapiyorsaniz [surumler sayfasi](https://github.com/aaclause/nvda-OpenAI/releases) uzerinden yeni `.nvda-addon` paketlerini ayni sekilde yukleyin.

## Desteklenen saglayicilar

NVDA'da **Tercihler -> Ayarlar -> AI Hub** altindan bir veya daha fazla saglayici ayarlayabilirsiniz. Her saglayici icin birden cok adlandirilmis hesap (API anahtari, gerekirse organization/base URL) eklenebilir.

| Saglayici | Rol |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT ve ilgili modeller; resmi transkripsiyon ve TTS pencereleri |
| [DeepSeek](https://www.deepseek.com/) | DeepSeek API (OpenAI uyumlu) |
| **Custom OpenAI** | OpenAI uyumlu herhangi bir HTTP API (ozel base URL + anahtar) |
| **Ollama** | OpenAI uyumlu endpoint ile yerel modeller; model yoneticisi araci |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; Voxtral TTS, OCR ve speech-to-text araclari |
| [OpenRouter](https://openrouter.ai/) | Tek anahtarla cok sayida ucuncu taraf modele erisim |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro araci |

Eklenti, tanimliysa API anahtarlarini **ortam degiskenlerinden** de okuyabilir (ornegin `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` vb.). Yine de hesap yonetimi icin ana yer ayarlar ekranidir.

### Konusmadan yaziya (transkripsiyon) altyapilari

Ana akis icindeki mikrofon/dosya transkripsiyonu (ayri OpenAI transkripsiyon aracindan farkli olarak) icin **whisper_cpp** (yerel), **openai** (Whisper API) ve **mistral** secenekleri, AI Hub ayarlarindaki **Audio** bolumunde secilebilir.

## Kurulum

1. [Eklenti surumleri sayfasini](https://github.com/aaclause/nvda-OpenAI/releases) acin.
2. En guncel `.nvda-addon` paketini indirin.
3. NVDA'da **Araclar -> Eklenti yonetimi** uzerinden kurun (veya dosyayi Gezginden acip onaylayin).

## Ilk kurulum

1. **NVDA -> Tercihler -> Ayarlar** yolunu acin.
2. **AI Hub** kategorisini secin.
3. **API keys** altinda saglayici dugmelerini kullanarak (ornegin **OpenAI API keys...**) en az bir hesap ekleyin: gorunen ad, API anahtari ve saglayiciya gore opsiyonel alanlar.
4. Gerekirse **Audio**, **Chat feedback**, **Advanced** / temperature ve **Auto-save conversation** ayarlarini duzenleyin (varsayilan acik).

En az bir kullanilabilir saglayici hesabi olana kadar ana pencere acildiginda AI Hub ayarlarina yonlendirme yapilir.

## Eski "Open AI" surumlerinden gecis

Eski bir surum kullandiysaniz:

- **Ayarlar**, eski **`OpenAI`** bolumunden **`AIHub`** bolumune tasinir.
- **Veriler** (konusmalar, hesap dosyalari, ekler) NVDA kullanici yapilandirmasi altindaki **`openai`** klasorunden **`aihub`** klasorune tasinir.

Normalde dosyalari elle tasimaniz gerekmez.

## NVDA menusu: AI Hub

NVDA menusunde surum bilgisiyle birlikte **AI Hub** gorunur. Baslica girdiler:

- **Documentation** — kullanim kilavuzunu tarayicida acar (`doc\en\readme.html`). Dagitilan paketlerde bu dosya bulunmalidir; elle duzenlenmez, build surecinde `readme.md` dosyasindan uretilir.
- **Main dialog...** — sohbet penceresini acar (`NVDA+G` varsayilan).
- **Conversation history...** — kayitli sohbetleri yonetir.
- **Tools** — **OpenAI**, **Mistral**, **Google** ve **Ollama** araclarini gruplandirir.
- **API keys** / **API usage** / **GitHub repository** / **BasiliskLLM** — hizli baglantilar.

## Ana pencere

**`NVDA+G`** veya AI Hub menusu altindaki **Main dialog...** ile acilir.

### Neler yapabilirsiniz

- Secili modelle sohbet edin; **Messages** alaninda klavye ve baglam menuleriyle gezin (ornegin odak mesaj alanindayken **j** / **k**).
- **Yerel gorsel ve belgeleri** ekleyin, destekleniyorsa **dosya URL** ekleri kullanin.
- Istem baglam menusundeki **Paste (file or text)** veya **`Ctrl+V`** ile dosya ekleme/yol metni ekleme/tek URL'yi ek olarak algilama.
- **Ses kaydi** yapin, ses dosyasi ekleyin, model destekliyorsa istem metni icin **TTS** kullanin.
- **`Escape`** ana pencereyi kapatir (engelleyici modal acik degilse).
- **`Ctrl+R`** mikrofon kaydini baslatir/durdurur.
- **`F2`** mevcut kayitli konusmayi yeniden adlandirir.
- **`Ctrl+N`** yeni bir sohbet oturumu acar.

### Modele bagli secenekler

Bazi kontroller yalnizca belirli modellerde gorunur:

- **Reasoning** ("thinking") destegi olan modellerde.
- Saglayici destekliyorsa **reasoning effort** seviyeleri.
- Desteklenen modellerde **web search** secenegi.

Saglayicilar API'lerini guncelledikce kullanilabilirlik degisebilir; arayuz her zaman secili modele gore davranir.

### Sistem istemi

Sistem istemi model davranisini yonlendirir. Erisilebilirlik odakli varsayilan bir istem gelir; duzenleyebilir, baglam menusunden sifirlayabilir ve isterse son kullanilan istemi saklayabilirsiniz. Sistem istemi de token tuketir.

## Konusma gecmisi

AI Hub menusunden **Conversation history...** secenegini kullanin veya **Girdi Hareketleri -> AI Hub** altindan bir hareket atayin.

Konusmalari listeleyebilir, acabilir, yeniden adlandirabilir, silebilir ve yeni konusma olusturabilirsiniz. Ana pencerede **F2** ve **Ctrl+N** yardimci olur.

### Otomatik kaydetme

**Auto-save conversation** aciksa (varsayilan), her tamamlanan asistan yanitindan sonra konusma kaydedilir/guncellenir. Pencere kapanirken de gerekli durumda durum saklanabilir. Isterseniz **Messages** alaninin baglam menusunden elle kaydedebilirsiniz.

## Soru sor (sesli)

Bu komutun varsayilan hareketi **yoktur**. **Girdi Hareketleri -> AI Hub** altindan atayin.

- Ilk basin: kaydi baslat.
- Kayit sirasinda ikinci basin: durdur ve gonder.
- Yanit sesli oynatiliyorsa tekrar basin: oynatmayi durdur.

**Modlar:**

- **Direct audio** — secili model ses girdisini destekliyorsa kayit dogrudan gonderilir.
- **Transcribe then chat** — aksi halde kayit secili transkripsiyon altyapisiyla yaziya cevrilir, sonra modele gonderilir.

Ana pencere odaktaysa oradaki **mevcut model** kullanilir; degilse eklenti uygun bir modeli otomatik secer.

## Tools alt menusu

**Tools** girdisi, saglayiciya gore gruplanmis arac pencerelerini acar (her biri ilgili saglayici hesabi gerektirebilir):

| Menu alani | Arac |
|-----------|------|
| Mistral | **Voxtral TTS...**, **OCR...**, **Speech to Text...** |
| Google | **Lyria 3 Pro...** |
| OpenAI | **TTS...**, **Transcription / Translation...** |
| Ollama | **Model manager...** |

Aracin saglayicisi icin hesap yoksa AI Hub ayarlarindan hesap eklemeniz istenir.

## Global komutlar

Tum varsayilan kisayollar **NVDA -> Tercihler -> Girdi Hareketleri -> AI Hub** altindan degistirilebilir.

| Kisayol | Islem |
|---------|--------|
| `NVDA+G` | AI Hub ana penceresini goster |
| `NVDA+E` | Ekran goruntusu al ve betimle |
| `NVDA+O` | Mevcut gezgin nesnesi bolgesini betimle |
| *(varsayilan hareket yok)* | Konusma gecmisi |
| *(varsayilan hareket yok)* | Soru sor (kayit / gonder / ses durdur) |
| *(varsayilan hareket yok)* | Mikrofon kaydini ve transkripsiyonu ac/kapat |

## Veriler nerede tutulur

Calisma dosyalari, kayitli konusma indeksi, `accounts.json` ve ekler NVDA kullanici yapilandirmasindaki **`aihub`** klasorunde tutulur (`openai`'den tasinmis). Gecici dosyalar `tmp` altindadir ve uygun zamanlarda temizlenir.

## Gerekli bagimliliklar (build sirasinda otomatik indirilir)

Build islemi `scons` ile runtime kutuphanelerini su klasore yerlestirir:

`addon/globalPlugins/AIHub/libs/`

Gerekli kutuphane eksikse `scons`, sabitlenmis wheel paketlerini indirir ve yalnizca gerekli icerigi buraya cikarir. Guncel sabitlenmis bagimliliklar:

- **[markdown2](https://pypi.org/project/markdown2/)** `2.5.4` — sohbet Markdown goruntulemesi icin `libs/markdown2.py`.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1`:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

`libs` klasoru bilincli olarak git'e dahil edilmez; katkilayanlarin bu artefaktlari commit etmesi gerekmez.

## Kisa sorun giderme

- **"No account configured"** — secili saglayici icin **AI Hub** ayarlarindan API anahtari ekleyin.
- **Saglayici eki reddediyor** — dosya turu/boyutunu kontrol edin; gerekiyorsa farkli model veya saglayici deneyin.

Hata bildirimi ve katki icin AI Hub menusundeki **GitHub repository** baglantisini kullanin.
