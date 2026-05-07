Jos haluat erillisen työpöytäkokemuksen ja lisätyönkulkuja, tutustu [BasiliskLLM:ään](https://github.com/SigmaNight/basiliskLLM/) (itsenäinen sovellus ja kevyt NVDA-lisäosa). AI-Hub on edelleen täysiverinen vaihtoehto NVDA:n sisällä.

# AI-Hub

**AI-Hub** on NVDA-lisäosa, joka yhdistää ruudunlukijasi useisiin suurten kielimallien (LLM) rajapintoihin. Voit käyttää sitä kirjoittamiseen, tiivistämiseen, käännösapuun, kuvien tulkintaan (kuvat ja kuvakaappaukset), äänikysymyksiin, litterointiin ja valinnaisiin työkaluikkunoihin (TTS, OCR ja muuta) poistumatta NVDA:sta.

Lisäosan **pakettinimi** NVDA:ssa on yhä `openai` (yhteensopivuus olemassa olevien asennusten kanssa). Valikoissa ja asetuksissa näkyvä **näyttönimi** on **AI-Hub**.

## Ominaisuudet yhdellä silmäyksellä

- **Keskustelu** erillisessä pääikkunassa, jossa on historia, järjestelmäkehote sekä mallin/tilin valinta.
- **Kuvat ja dokumentit** tiedostoliitteinä; lisäksi **URL-osoitteet** etätiedostoihin tyyppitarkistuksilla, jotka vastaavat **valittua palveluntarjoajaa**.
- **Älykäs liittäminen** kehotekentässä: liitä tiedostoja leikepöydältä, polkuja tekstistä tai yksittäinen URL (saatavilla myös kehotteen kontekstivalikosta). `Ctrl+V` käyttää samaa logiikkaa, kun kohdistus on kehotteessa.
- **Keskustelujen tallennus ja historia** uudelleennimeämisellä, poistolla ja uudelleenavaamisella.
- **Kysy kysymys** mistä tahansa (ei oletusnäppäintä): määritä ele kohdassa **Syöte-eleet -> AI-Hub**, jotta voit nauhoittaa, lähettää sekä kuunnella tai lukea vastauksen.
- **Yleiskuvaus**: kuvakaappaus (`NVDA+E`) tai navigaattoriobjektin alue (`NVDA+O`) lähetetään keskusteluistuntoon.
- **Työkalut**-alivalikko (NVDA -> AI-Hub): palveluntarjoajakohtaisia toimintoja, kuten TTS, OCR, puheesta tekstiksi, Lyria-audio ja Ollama-mallinhallinta.
- **Päättely-/verkkohaku**-asetukset näkyvät vain, kun **nykyinen malli** tukee niitä (tuki vaihtelee palveluntarjoajan mukaan).

Tämä lisäosa **ei** sisällä omaa päivitystarkistinta. **Päivitykset** hoidetaan **NVDA:n virallisen lisäosakaupan** kautta, kun asennat lisäosan sieltä. Jos asennat manuaalisesti [julkaisusivulta](https://github.com/aaclause/nvda-OpenAI/releases), asenna uudemmat `.nvda-addon`-versiot samalla tavalla.

## Tuetut palveluntarjoajat

Määritä **yksi tai useampi palveluntarjoaja** NVDA:ssa kohdassa **Asetukset -> Asetukset -> AI-Hub**. Jokaisella palveluntarjoajalla voi olla **useita nimettyjä tilejä** (API-avaimet sekä palveluntarjoajasta riippuen valinnainen organisaatio tai perus-URL).

| Palveluntarjoaja | Rooli |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT ja siihen liittyvät mallit; viralliset litterointi- ja TTS-työkaludialogit |
| [DeepSeek](https://www.deepseek.com/) | DeepSeek API (OpenAI-yhteensopiva) |
| **Mukautettu OpenAI** | Mikä tahansa OpenAI-yhteensopiva HTTP API (mukautettu perus-URL + avain) |
| **Ollama** | Paikalliset mallit OpenAI-yhteensopivan päätepisteen kautta; mallinhallintatyökalu |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; Voxtral TTS-, OCR- ja puheesta tekstiksi -työkalut |
| [OpenRouter](https://openrouter.ai/) | Monia kolmannen osapuolen malleja yhden avaimen takana |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; Lyria 3 Pro -työkalu |

Lisäosa voi lukea API-avaimia **ympäristömuuttujista**, jos ne on asetettu (esimerkiksi `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY` ja muut). Asetusten käyttöliittymä on silti ensisijainen paikka tilien hallintaan.

### Puheesta tekstiksi (litterointi) -taustat

**Mikrofoni-/tiedostolitterointia** varten päätyönkulussa (ei erillisessä OpenAI-litterointityökalussa) voit valita asetusten **AI-Hub -> Audio** -osiosta vaihtoehdot **whisper_cpp** (paikallinen), **openai** (Whisper API) ja **mistral**.

## Asennus

1. Avaa [lisäosan julkaisusivu](https://github.com/aaclause/nvda-OpenAI/releases).
2. Lataa uusin `.nvda-addon`-paketti.

## Ensiasetukset

1. Avaa **NVDA -> Asetukset -> Asetukset**.
2. Valitse **AI-Hub** -kategoria.
3. Valitse **API Accounts** -kohdassa **Add account...**.
4. Valitse tili-ikkunassa palveluntarjoaja, anna tilin nimi ja täytä pakolliset kentät (API-avain useimmille palveluille; base URL **Custom OpenAI**- ja **Ollama**-palveluille, ja Ollama käyttää oletuksena paikallista http://127.0.0.1:11434/v1-osoitetta, jos kenttä on tyhjä).
5. Tallenna ja lisää halutessasi lisää tilejä, muokkaa olemassa olevia tai poista käyttämättömiä tilejä listasta.
6. Säädä halutessasi **Audio**, **Chat feedback**, **Advanced** / lämpötila sekä **Auto-save conversation** (oletuksena käytössä).

Kunnes vähintään yksi palveluntarjoajan tili on valmis, päädialogin avaaminen kehottaa lisäämään avaimia AI-Hub -asetuksissa.

## Päivittäminen vanhemmista “Open AI” -versioista

Jos olet käyttänyt lisäosan vanhempaa versiota:

- **Asetukset** siirretään vanhasta **`OpenAI`**-määritysosiosta kohtaan **`AIHub`**. Asetusten ei pitäisi kadota.
- **Datatiedostot** (keskustelut, avainsäilö, liitteet) siirretään NVDA:n käyttäjäasetushakemistossa olevasta **`openai`**-kansiosta **`aihub`**-kansioon.

Sinun ei tarvitse siirtää tiedostoja käsin, ellei käytössäsi ole mukautettu asennus.

## NVDA-valikko: AI-Hub

NVDA-valikossa näkyy **AI-Hub** (nimessä myös asennettu versio). Merkinnät sisältävät:

- **Dokumentaatio** — avaa käyttöoppaan selaimessa (`doc\en\readme.html`).
- **Päädialogi...** — avaa keskusteluikkunan (`NVDA+G` oletuksena).
- **Keskusteluhistoria...** — hallitse tallennettuja keskusteluja.
- **Työkalut** — alivalikko, joka ryhmittelee **OpenAI**-, **Mistral**-, **Google**- ja **Ollama**-toiminnot (katso alla).
- **GitHub repository** / **BasiliskLLM** - pikalinkit.

## Päädialogi

Avaa komennolla **`NVDA+G`** tai AI-Hub -valikon **Päädialogi...**-kohdasta.

### Mitä voit tehdä

- Keskustele valitulla mallilla; tarkastele **Viestit**-aluetta näppäimistönavigoinnilla ja kontekstivalikoilla (esim. **j** / **k** siirtymiseen viestien välillä, kun kohdistus on viestialueella — katso aktiivisen kentän ohjeet näytöltä).
- Liitä **paikallisia kuvia tai dokumentteja** ja lisää **tiedosto-URL-osoitteita**, kun palveluntarjoaja tukee niitä. Nykyisen palveluntarjoajan tukemattomista tyypeistä voidaan varoittaa ennen lähetystä.
- Käytä kehotteen kontekstivalikon **Liitä (tiedosto tai teksti)** -toimintoa tai **`Ctrl+V`** kehotteessa: lisäosa voi liittää tiedostoja, lisätä tekstissä olevia polkuja tai käsitellä yksittäisen URL:n liitteenä tilanteen mukaan.
- Nauhoita **äänikatkelmia**, liitä äänitiedostoja ja käytä kehotetekstin **TTS**-toimintoa, kun malli tukee sitä.
- **`Escape`** sulkee päädialogin (kun estävää modaalista ikkunaa ei ole auki).
- **`Ctrl+R`** vaihtaa mikrofoniäänityksen tilaa (kun käytettävissä).
- **`F2`** nimeää nykyisen tallennetun keskustelun uudelleen (kun se on jo olemassa tallennuksessa).
- **`Ctrl+N`** avaa **uuden** päädialogi-instanssin (istunnon).

### Mallista riippuvat asetukset

Jotkin ohjaimet näkyvät tai toimivat vain tietyillä malleilla:

- **Päättely** (“thinking”) malleille, jotka tarjoavat sen; suoratoistettu päättely pidetään erillään näkyvästä vastauksesta, kun API erottaa nämä.
- **Päättelyteho** ja siihen liittyvät ohjaimet siellä, missä palveluntarjoaja tukee eri tasoja.
- **Verkkohaku** vain malleille, jotka ilmoittavat tukevansa verkkohakua.

Tarkka saatavuus muuttuu, kun palveluntarjoajat päivittävät rajapintojaan; käyttöliittymä heijastaa **kulloinkin valittua mallia**.

### Järjestelmäkehote

Järjestelmäkehote ohjaa mallin toimintaa. Oletuksena on saavutettavuusavustamiseen soveltuva kehote; voit muokata sitä, palauttaa sen kontekstivalikosta ja halutessasi tallentaa viimeksi käytetyn kehotteen pysyvästi (asetettavissa asetuksissa). Järjestelmäkehote kuluttaa tokeneita kuten mikä tahansa muukin syöte.

## Keskusteluhistoria

Käytä AI-Hub -valikon **Keskusteluhistoria...**-toimintoa tai määritä ele kohdassa **Syöte-eleet -> AI-Hub**.

Voit listata, avata, nimetä uudelleen, poistaa ja luoda keskusteluja. Päädialogissa **F2** ja **Ctrl+N** auttavat nykyisen istunnon hallinnassa.

### Automaattitallennus

Jos asetuksissa **Tallenna keskustelu automaattisesti** on käytössä (oletus), lisäosa tallentaa (tai päivittää) tallennetun keskustelun **jokaisen valmistuneen avustajavastauksen jälkeen**, ja voi tallentaa tilan myös dialogin sulkemisen yhteydessä, jos tallennettavaa on. Voit tallentaa myös **Viestit**-kentän kontekstivalikosta. Jos automaattitallennus on pois päältä, käytä manuaalista tallennusta silloin, kun haluat säilyttää keskustelun.

## Kysy kysymys (ääni)

Tällä komennolla **ei ole oletusnäppäintä**. Määritä se kohdassa **Syöte-eleet -> AI-Hub**.

- Ensimmäinen painallus: aloita äänitys.
- Toinen painallus äänityksen aikana: lopeta ja lähetä.
- Jos vastaus toistetaan äänenä, paina uudelleen lopettaaksesi toiston.

**Tilat:**

- **Suora audio** — jos valittu malli tukee audiosyötettä, äänitys voidaan lähettää audiona ilman erillistä litterointivaihetta.
- **Litteroi ja keskustele** — muussa tapauksessa määritetty litterointitausta käsittelee äänityksen ensin, minkä jälkeen teksti lähetetään keskustelumallille.

Jos päädialogi on kohdistettuna, käytetään sen **nykyistä mallia**; muuten lisäosa valitsee sopivan mallin määritettyjen palveluntarjoajien joukosta.

## Työkalut-alivalikko

AI-Hub -valikon **Työkalut**-kohta avaa palveluntarjoajittain ryhmitellyt dialogit (jokainen voi vaatia vastaavan API-tilin):

| Valikkoalue | Työkalu |
|-----------|------|
| Mistral | **Voxtral TTS...**, **OCR...**, **Speech to Text...** |
| Google | **Lyria 3 Pro...** |
| OpenAI | **TTS...**, **Transcription / Translation...** |
| Ollama | **Model manager...** |

Jos työkalun palveluntarjoajalle ei ole määritetty tiliä, lisäosa ilmoittaa lisäämään sellaisen AI-Hub -asetuksissa.

## Yleiskomennot

Kaikkia oletuseleitä voi muuttaa kohdassa **NVDA -> Asetukset -> Syöte-eleet -> AI-Hub**.

| Ele | Toiminto |
|---------|--------|
| `NVDA+G` | Näytä AI-Hub -päädialogi |
| `NVDA+E` | Ota kuvakaappaus ja kuvaile (lisää kuvan istuntoon) |
| `NVDA+O` | Kuvaile nykyisen navigaattoriobjektin alue |
| *(ei oletuselettä)* | Keskusteluhistoria. Määritä kohdassa Syöte-eleet -> AI-Hub. |
| *(ei oletuselettä)* | Kysy kysymys (äänitä / lähetä / pysäytä ääni). Määritä kohdassa Syöte-eleet -> AI-Hub. |
| *(ei oletuselettä)* | Vaihda mikrofoniäänityksen ja litteroinnin tila. Määritä kohdassa Syöte-eleet -> AI-Hub. |

## Missä tiedot säilytetään

Työtiedostot, tallennettujen keskustelujen indeksi, yhtenäinen `accounts.json` ja liitteet sijaitsevat NVDA:n **käyttäjäasetushakemistossa**, **`aihub`**-kansiossa (kun siirto `openai`-kansiosta on tehty). Väliaikaistiedostot käyttävät `tmp`-alikansiota, ja ne siivotaan tarpeen mukaan (esim. lisäosan sulkeutuessa tai dialogin sulkemisen yhteydessä).

## Vaaditut riippuvuudet (haetaan automaattisesti buildin aikana)

Build käyttää `scons`:ia ajonaikaisten kirjastojen täyttämiseen seuraavaan sijaintiin:

`addon/globalPlugins/AIHub/libs/`

Kun vaadittu kirjasto puuttuu, `scons` lataa kiinnitetyt wheel-paketit ja purkaa vain tarvittavat osat tähän kansioon. Nykyiset kiinnitetyt riippuvuudet ovat:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — puretaan kansioon `libs/` keskustelun Markdown-renderöintiä varten.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` seuraaville:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

`libs`-hakemisto on tarkoituksella gitignoressa; kontribuuttorien ei tarvitse commitoida vendoroituja artefakteja.

## Vianmääritys (lyhyt)

- **"Tiliä ei ole määritetty"** — lisää API-avain valitsemallesi palveluntarjoajalle **AI-Hub** -asetuksissa.
- **Palveluntarjoaja hylkää liitteen** — tarkista tiedoston tyyppi ja koko; kokeile toista mallia tai palveluntarjoajaa, joka tukee tarvitsemaasi mediaa.

Ongelmat ja kontribuutiot: käytä AI-Hub -valikon **GitHub repository** -linkkiä.
