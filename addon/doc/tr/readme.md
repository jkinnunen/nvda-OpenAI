Ek iş akışları sunan ayrı bir masaüstü deneyimi arıyorsanız [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) projesine bakabilirsiniz (bağımsız uygulama ve minimal NVDA eklentisi). AI Hub, NVDA içinde tam özellikli bir seçenek olarak kalmaya devam eder.

# AI Hub

**AI Hub**, ekran okuyucunuzu birden fazla büyük dil modeli (LLM) API’sine bağlayan bir NVDA eklentisidir. NVDA’dan çıkmadan yazma, özetleme, çeviri desteği, görsel işlemler (görseller ve ekran görüntüleri), sesli soru sorma, transkripsiyon ve isteğe bağlı araç iletişim kutuları (TTS, OCR ve ötesi) için kullanabilirsiniz.

Eklentinin NVDA’daki **paket adı**, mevcut kurulumlarla uyumluluk için hâlâ `openai` olarak kalır. Menü ve ayarlarda gördüğünüz **görünen ad** ise **AI Hub**’dır.

## Bir bakışta özellikler

- Geçmiş, sistem istemi ve model/hesap seçimi sunan özel ana iletişim kutusunda **sohbet**.
- Dosyalardan **görsel ve belge** ekleme; **seçilen sağlayıcıya** uygun tür denetimleriyle uzak dosyalar için **URL** kullanma.
- İstem alanında **akıllı yapıştırma**: panodan dosya yapıştırma, metinden yol veya tek bir URL (istemin bağlam menüsünden de erişilebilir). Odak istem alanındayken `Ctrl+V` aynı mantıkla çalışır.
- Yeniden adlandırma, silme ve yeniden açma özellikleriyle **konuşma kaydı ve geçmişi**.
- Her yerden **soru sor** (varsayılan kısayol yok): **Girdi Hareketleri → AI Hub** altından bir hareket atayarak kayıt alma, gönderme ve yanıtı dinleme veya okuma.
- **Genel betimleme**: ekran görüntüsü (`NVDA+E`) veya gezgin nesnesi bölgesi (`NVDA+O`) bir sohbet oturumuna gönderilir.
- **Tools** alt menüsü (NVDA → AI Hub altında): TTS, OCR, konuşmayı metne çevirme, Lyria ses ve Ollama model yönetimi gibi sağlayıcıya özel yardımcılar.
- **Akıl yürütme / web araması** seçenekleri yalnızca **geçerli model** bunları desteklediğinde görünür (sağlayıcıya göre değişir).

Bu eklentinin kendi güncelleme denetleyicisi **yoktur**. Eklentiyi **NVDA’nın resmî Eklenti Mağazası**’ndan kurduysanız **güncellemeler** oradan yönetilir. [Sürümler sayfasından](https://github.com/aaclause/nvda-OpenAI/releases) elle kuruyorsanız, yeni `.nvda-addon` paketlerini aynı yolla yükleyin.

## Desteklenen sağlayıcılar

NVDA’da **Tercihler → Ayarlar → AI Hub** bölümünden **bir veya daha fazla sağlayıcı** yapılandırın. Her sağlayıcı, **birden fazla adlandırılmış hesap** (API anahtarları; gerektiğinde isteğe bağlı kuruluş veya temel URL) tutabilir.

| Sağlayıcı | Rol |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT ve ilgili modeller; resmî transkripsiyon ve TTS araç iletişim kutuları |
| [DeepSeek](https://www.deepseek.com/) | DeepSeek API (OpenAI uyumlu) |
| **Custom OpenAI** | OpenAI uyumlu herhangi bir HTTP API (özel temel URL + anahtar) |
| **Ollama** | OpenAI uyumlu uç nokta üzerinden yerel modeller; model yöneticisi aracı |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; Voxtral TTS, OCR ve konuşmayı metne çevirme araçları |
| [OpenRouter](https://openrouter.ai/) | Tek anahtar arkasında çok sayıda üçüncü taraf model |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro aracı |

Tanımlandıklarında eklenti API anahtarlarını **ortam değişkenlerinden** okuyabilir (örneğin `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` ve diğerleri). Hesapları yönetmek için asıl yer yine ayarlar arayüzüdür.

### Konuşmayı metne çevirme (transkripsiyon) altyapıları

Ana akıştaki **mikrofon / dosya transkripsiyonu** için (OpenAI’nın ayrı transkripsiyon aracı dışında), AI Hub ayarlarındaki **Ses** bölümünden **whisper_cpp** (yerel), **openai** (Whisper API) ve **mistral** arasında seçim yapabilirsiniz.

## Kurulum

1. [Eklenti sürümleri sayfasını](https://github.com/aaclause/nvda-OpenAI/releases) açın.
2. En son `.nvda-addon` paketini indirin.

## İlk yapılandırma

1. **NVDA → Tercihler → Ayarlar**’ı açın.
2. **AI Hub** kategorisini seçin.
3. **API Accounts** bölümünde **Add account...** seçeneğini kullanın.
4. Hesap iletişim kutusunda bir sağlayıcı seçin, hesap adı girin ve gerekli alanları doldurun (çoğu sağlayıcı için API anahtarı; **Custom OpenAI** ve **Ollama** için base URL, Ollama alan boşsa varsayılan olarak yerel http://127.0.0.1:11434/v1 adresini kullanır).
5. Kaydedin; ardından isteğe bağlı olarak daha fazla hesap ekleyebilir, mevcut hesapları düzenleyebilir veya kullanılmayan hesapları listeden kaldırabilirsiniz.
6. İsteğe bağlı olarak **Audio**, **Chat feedback**, **Advanced** / sıcaklık ve **Auto-save conversation** ayarlarını düzenleyin (varsayılan olarak açıktır).

En az bir sağlayıcı hesabı hazır olmadan ana iletişim kutusunu açtığınızda, AI Hub ayarlarına anahtar eklemeniz istenir.

## Eski "Open AI" sürümlerinden yükseltme

Bu eklentinin daha eski bir sürümünü kullandıysanız:

- **Ayarlar**, eski **`OpenAI`** yapılandırma bölümünden **`AIHub`** bölümüne taşınır; tercihlerinizi kaybetmemeniz gerekir.
- **Veri dosyaları** (konuşmalar, anahtar deposu, ekler), NVDA kullanıcı yapılandırma dizininizdeki **`openai`** klasöründen **`aihub`** klasörüne taşınır.

Özel bir kurulum kullanmıyorsanız dosyaları elle taşımanız gerekmez.

## NVDA menüsü: AI Hub

NVDA menüsünde **AI Hub**’ı (etikette kurulu sürümle birlikte) bulursunuz. Menü öğeleri şunlardır:

- **Documentation** — kullanıcı kılavuzunu tarayıcıda açar (`doc\en\readme.html`).
- **Main dialog…** — sohbet penceresini açar (varsayılan `NVDA+G`).
- **Conversation history…** — kayıtlı sohbetleri yönetir.
- **Tools** — **OpenAI**, **Mistral**, **Google** ve **Ollama** yardımcılarını gruplayan alt menü (aşağıya bakın).
- **GitHub repository** / **BasiliskLLM** - hızlı bağlantılar.

## Ana iletişim kutusu

**`NVDA+G`** veya menüden **Main dialog…** ile açın.

### Yapabilecekleriniz

- Seçilen modelle sohbet edin; **Messages** alanında klavye ile gezinin ve bağlam menülerini kullanın (ör. odak mesaj alanındayken iletiler arasında **j** / **k** — etkin alan için ekrandaki ipuçlarına bakın).
- Sağlayıcı destekliyorsa **yerel görsel veya belge** ekleyin ve **dosya URL’leri** girin. Geçerli sağlayıcı için desteklenmeyen türler, göndermeden önce uyarılabilir.
- İstemin bağlam menüsünden **Paste (file or text)** kullanın veya istemde **`Ctrl+V`**: eklenti uygun olduğunda dosya ekleyebilir, metin yolları ekleyebilir veya tek bir URL’yi ek olarak işleyebilir.
- **Ses** kaydı alın, ses dosyası ekleyin ve model izin veriyorsa istem metni için **TTS** kullanın.
- **`Escape`**, engelleyici bir iletişim kutusu açık değilken ana pencereyi kapatır.
- **`Ctrl+R`**, uygunsa mikrofon kaydını açıp kapatır.
- **`F2`**, depoda zaten varsa geçerli kayıtlı konuşmayı yeniden adlandırır.
- **`Ctrl+N`**, yeni bir ana iletişim kutusu örneği (oturum) açar.

### Modele bağlı seçenekler

Bazı denetimler yalnızca belirli modellerde görünür veya geçerlidir:

- Bunu sunan modeller için **Akıl yürütme** ("thinking"); API bu ayrımı verdiğinde akış hâlindeki akıl yürütme, görünür yanıttan ayrı tutulur.
- Sağlayıcı düzeyleri destekliyorsa **Akıl yürütme çabası** ve ilgili denetimler.
- Yalnızca web araması desteğini duyuran modellerde **Web araması**.

Sağlayıcılar API’lerini güncelledikçe kullanılabilirlik değişir; arayüz her zaman **o anda seçili modeli** yansıtır.

### Sistem istemi

Sistem istemi model davranışını yönlendirir. Erişilebilirlik yardımına uygun bir varsayılan vardır; düzenleyebilir, bağlam menüsünden sıfırlayabilir ve son kullandığınız istemi kalıcı tutmayı ayarlardan isteğe bağlı açabilirsiniz. Sistem istemi de diğer girdiler gibi token harcar.

## Konuşma geçmişi

AI Hub menüsünden **Conversation history…**’yi kullanın veya **Girdi Hareketleri → AI Hub** altından bir hareket atayın.

Konuşmaları listeleyebilir, açabilir, yeniden adlandırabilir, silebilir ve yeni konuşma oluşturabilirsiniz. Ana iletişim kutusunda **F2** ve **Ctrl+N**, geçerli oturumu yönetmeye yardımcı olur.

### Otomatik kaydetme

Ayarlarda **Konuşmayı otomatik kaydet** açıksa (varsayılan), eklenti depolanan konuşmayı **her tamamlanan asistan yanıtından sonra** kaydeder veya günceller; kaydedilecek bir şey varsa iletişim kutusunu kapatırken durumu da kalıcı hâle getirebilir. **Messages** alanının bağlam menüsünden de kaydedebilirsiniz. Otomatik kayıt kapalıysa, kalıcı tutmak istediğinizde elle kaydedin.

## Soru sor (ses)

Bu komutun **varsayılan tuşu yoktur**. Bir tuş atamak için **Girdi Hareketleri → AI Hub**’a gidin.

- İlk basış: kaydı başlatır.
- Kayıt sürerken ikinci basış: durdurur ve gönderir.
- Yanıt ses olarak çalıyorsa, tekrar basış oynatmayı durdurur.

**Modlar:**

- **Doğrudan ses** — seçili model ses girişini destekliyorsa kaydınız ayrı bir transkripsiyon adımı olmadan ses olarak gönderilebilir.
- **Önce metne çevir, sonra sohbet et** — aksi hâlde yapılandırdığınız transkripsiyon altyapısı kaydı işler, ardından metin sohbet modeline gider.

Ana iletişim kutusu odaktaysa onun **geçerli modeli** kullanılır; değilse eklenti, yapılandırılmış sağlayıcılar arasından uygun bir model seçer.

## Araçlar alt menüsü

AI Hub menüsündeki **Tools** öğesi, sağlayıcıya göre gruplanmış iletişim kutularını açar (her biri ilgili API hesabını gerektirebilir):

| Menü alanı | Araç |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Speech to Text…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Transcription / Translation…** |
| Ollama | **Model manager…** |

Aracın sağlayıcısı için hesap tanımlı değilse eklenti, AI Hub ayarlarından hesap eklemenizi söyler.

## Genel komutlar

Varsayılan tüm hareketler **NVDA → Tercihler → Girdi Hareketleri → AI Hub** altından değiştirilebilir.

| Hareket | Eylem |
|---------|--------|
| `NVDA+G` | AI Hub ana iletişim kutusunu gösterir |
| `NVDA+E` | Ekran görüntüsü alır ve betimler (oturuma görsel ekler) |
| `NVDA+O` | Geçerli gezgin nesnesi bölgesini betimler |
| *(varsayılan hareket yok)* | Konuşma geçmişi. Girdi Hareketleri → AI Hub altından atayın. |
| *(varsayılan hareket yok)* | Soru sor (kaydet / gönder / sesi durdur). Girdi Hareketleri → AI Hub altından atayın. |
| *(varsayılan hareket yok)* | Mikrofon kaydı ve transkripsiyonu aç/kapat. Girdi Hareketleri → AI Hub altından atayın. |

## Veriler nerede saklanır

Çalışma dosyaları, kaydedilmiş konuşmalar indeksi, birleşik `accounts.json` ve ekler; `openai`’den taşındıktan sonra NVDA **kullanıcı yapılandırması** dizininizdeki **`aihub`** klasöründedir. Geçici dosyalar `tmp` alt klasörünü kullanır; uygun olduğunda temizlenir (ör. eklenti kapanırken veya iletişim kutusu kapanırken).

## Gerekli bağımlılıklar (derleme sırasında otomatik alınır)

Derlemeler, çalışma zamanı kitaplıklarını şu konuma yerleştirmek için `scons` kullanır:

`addon/globalPlugins/AIHub/libs/`

Gerekli bir kitaplık eksikse `scons`, sabitlenmiş wheel paketlerini indirir ve yalnızca gereken parçaları bu klasöre çıkarır. Güncel sabitlenmiş bağımlılıklar şunlardır:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — sohbet Markdown işlemesi için `libs/` içine çıkarılır.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1`:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

`libs` dizini bilerek `.gitignore`’dadır; katkı verenlerin derlemeyle eklenen ikili dosyaları depoya eklemesi gerekmez.

## Sorun giderme (kısa)

- **"No account configured"** — **AI Hub** ayarlarında, kullandığınız sağlayıcı için bir API anahtarı ekleyin.
- **Sağlayıcı eki reddediyor** — dosya türünü ve boyutunu kontrol edin; ihtiyaç duyduğunuz ortamı destekleyen başka bir model veya sağlayıcı deneyin.

Sorun bildirimi ve katkılar için AI Hub menüsündeki **GitHub repository** bağlantısını kullanın.
