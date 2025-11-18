import whisper
import torch
from typing import Optional
from pydub import AudioSegment
import tempfile

# ⚙️ Model seçimi — 'small' hızlı, 'medium' daha doğru
MODEL_NAME = "medium"  # 'medium' istersen doğruluk artar ama yavaşlar

print(f"🎯 Whisper modeli yükleniyor: {MODEL_NAME}...")
model = whisper.load_model(MODEL_NAME)

# 🧠 GPU kullanımı (RTX 4050 desteği)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(DEVICE)
print(f"✅ Model {DEVICE.upper()} üzerinde çalışıyor.")

def clean_audio(input_path: str) -> str:
    """Ses dosyasını normalize eder (tek kanal, 16kHz WAV)."""
    sound = AudioSegment.from_file(input_path)
    sound = sound.set_channels(1).set_frame_rate(16000)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sound.export(tmp.name, format="wav")
        return tmp.name

def transcribe_file(path: str, language: Optional[str] = "tr") -> str:
    """Türkçe konuşmaları yüksek hızda ve doğrulukla yazıya çevirir."""
    # Girdi WAV değilse dönüştür
    if not path.lower().endswith(".wav"):
        path = clean_audio(path)

    # 🚀 GPU ve Türkçe optimizasyonları
    result = model.transcribe(
        path,
        language="tr",
        fp16=(DEVICE == "cuda"),  # GPU'daysa fp16 aktif
        temperature=0.0,           # Daha az rastgelelik
        condition_on_previous_text=False,  # Kısa segmentlerde hız artışı
        verbose=False
    )

    return result.get("text", "").strip()
