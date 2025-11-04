import whisper
from typing import Optional
from pydub import AudioSegment
import tempfile

# 🎯 Daha doğru sonuç için "medium" modelini kullanalım
MODEL_NAME = "medium"  # tiny / base / small / medium / large
model = whisper.load_model(MODEL_NAME)

def clean_audio(input_path):
    """Ses dosyasını normalize eder (tek kanal, 16kHz)"""
    sound = AudioSegment.from_file(input_path)
    sound = sound.set_channels(1)
    sound = sound.set_frame_rate(16000)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sound.export(tmp.name, format="wav")
        return tmp.name


def transcribe_file(path: str, language: Optional[str] = "tr") -> str:
    """Türkçe konuşmaları doğru şekilde yazıya çevirir"""
    # Ses dosyasını temizleyelim
    cleaned_path = clean_audio(path)

    # Whisper ayarları
    options = {
        "language": "tr",  # Türkçe'yi zorla
        "fp16": False       # CPU uyumu
    }

    # Modeli çalıştır
    result = model.transcribe(cleaned_path, **options)

    # Çıktıyı döndür
    return result.get("text", "").strip()
