
# 🎙️ Whisper Transcription API

OpenAI Whisper modeli kullanarak ses dosyalarını metne çeviren, GPU destekli ve FastAPI tabanlı REST API servisi.

## 🚀 Özellikler

-   **⚡ Yüksek Performans:** NVIDIA GPU (CUDA) desteği ile %400'e varan hız.
    
-   **🇹🇷 Türkçe Optimize:** Türkçe konuşmalar için özel ayarlanmış model.
    
-   **📄 Word Export:** Transkripti otomatik `.docx` formatında indirme imkanı.
    
-   **🎵 Geniş Format Desteği:** `mp3`, `wav`, `m4a`, `ogg`, `flac`, `mp4` ve dahası.
    
-   **🛠️ Akıllı Altyapı:** Singleton model yükleme, asenkron dosya işleme ve otomatik temizlik.
    

----------

## 📦 Kurulum

### 1. Gereksinimler

Projeyi çalıştırmadan önce sisteminde şunların olduğundan emin ol:

-   **FFmpeg:** Ses işleme için şart. (Windows için [buradan](https://ffmpeg.org/download.html) indir, Linux için `apt install ffmpeg`).
    
-   **Node.js:** Sadece Word çıktısı almak istiyorsan gereklidir (`npm install -g docx`).
    

### 2. Yükleme ve Çalıştırma

Bash

```
# Projeyi klonla
git clone <repo-url>
cd whisper-transcription-api

# Python paketlerini yükle
pip install -r requirements.txt

# Uygulamayı başlat (İlk açılışta Whisper modeli indirilecektir)
python main.py

```

API şu adreste aktif olacak: `http://localhost:8000`

----------

## 🎮 Kullanım

### Ses Dosyasını Metne Çevirme (POST)

Ses dosyanı gönder, karşılığında metni ve Word dosyasını al.

**Endpoint:** `/transcribe/`

**Parametre**

**Zorunlu mu?**

**Açıklama**

`file`

✅ Evet

Ses dosyası (mp3, wav vb.)

`language`

❌ Hayır

Dil kodu (Varsayılan: `tr`)

`save_to_word`

❌ Hayır

Word dosyası oluşturulsun mu? (`true`/`false`)

#### Örnek İstek (Python)

Python

```
import requests

files = {'file': open('kayit.mp3', 'rb')}
data = {'language': 'tr', 'save_to_word': 'true'}

response = requests.post("http://localhost:8000/transcribe/", files=files, data=data)
print(response.json())

```

#### Örnek İstek (cURL)

Bash

```
curl -X POST "http://localhost:8000/transcribe/" \
     -F "file=@toplanti.mp3" \
     -F "language=tr"

```

----------

## ⚙️ Konfigürasyon

Model boyutunu değiştirmek için `.env` dosyası oluşturabilirsin:

Kod snippet'i

```
# Seçenekler: tiny, base, small, medium (önerilen), large
WHISPER_MODEL=medium

```

----------

## 📁 Proje Yapısı

-   `main.py`: API ve endpoint yönetimi.
    
-   `transcribe.py`: Whisper AI model motoru.
    
-   `transcriptions/`: Oluşturulan Word dosyalarının düştüğü klasör.
    
-   `temp_uploads/`: Geçici ses dosyaları (işlem bitince silinir).
    

----------

### 📞 İletişim

Sorularınız veya önerileriniz için Issue açabilirsiniz. İyi kullanımlar! 🎉