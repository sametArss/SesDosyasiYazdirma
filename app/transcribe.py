import whisper
import torch
from typing import Optional
from pydub import AudioSegment
import tempfile
import os
import logging
from pathlib import Path

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """Singleton pattern ile Whisper model yönetimi"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self.model_name = os.getenv("WHISPER_MODEL", "medium")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self._load_model()
    
    def _load_model(self):
        """Model yükle ve GPU'ya taşı"""
        logger.info(f"🎯 Whisper modeli yükleniyor: {self.model_name}...")
        self._model = whisper.load_model(self.model_name)
        self._model = self._model.to(self.device)
        logger.info(f"✅ Model {self.device.upper()} üzerinde hazır.")
    
    @property
    def model(self):
        return self._model
    
    @staticmethod
    def clean_audio(input_path: str) -> str:
        """
        Ses dosyasını Whisper için optimize eder.
        - Mono kanal
        - 16kHz sample rate
        - WAV formatı
        """
        try:
            sound = AudioSegment.from_file(input_path)
            sound = sound.set_channels(1).set_frame_rate(16000)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                sound.export(tmp.name, format="wav")
                logger.info(f"✅ Ses dosyası normalize edildi: {tmp.name}")
                return tmp.name
        except Exception as e:
            logger.error(f"❌ Ses normalize hatası: {e}")
            raise
    
    def transcribe(
        self, 
        file_path: str, 
        language: str = "tr",
        temperature: float = 0.0,
        **kwargs
    ) -> dict:
        """
        Ses dosyasını yazıya çevirir.
        
        Args:
            file_path: Ses dosyası yolu
            language: Dil kodu (varsayılan: tr)
            temperature: Rastgelelik seviyesi (0.0 = deterministik)
            **kwargs: Ekstra Whisper parametreleri
        
        Returns:
            {"text": str, "segments": list, "language": str}
        """
        # WAV formatına çevir (gerekirse)
        processed_path = file_path
        cleanup_needed = False
        
        if not file_path.lower().endswith(".wav"):
            processed_path = self.clean_audio(file_path)
            cleanup_needed = True
        
        try:
            # Whisper transcribe
            result = self.model.transcribe(
                processed_path,
                language=language,
                fp16=(self.device == "cuda"),
                temperature=temperature,
                condition_on_previous_text=False,  # Hız için
                verbose=False,
                **kwargs
            )
            
            return {
                "text": result.get("text", "").strip(),
                "segments": result.get("segments", []),
                "language": result.get("language", language)
            }
        
        finally:
            # Geçici dosyayı temizle
            if cleanup_needed and os.path.exists(processed_path):
                os.remove(processed_path)
                logger.info(f"🗑️ Geçici dosya silindi: {processed_path}")


# Global instance (lazy loading)
_transcriber = None

def get_transcriber() -> WhisperTranscriber:
    """Singleton transcriber instance döndür"""
    global _transcriber
    if _transcriber is None:
        _transcriber = WhisperTranscriber()
    return _transcriber


def transcribe_file(path: str, language: str = "tr") -> str:
    """
    Backward compatibility için basit interface.
    Yeni kodda get_transcriber().transcribe() kullan.
    """
    transcriber = get_transcriber()
    result = transcriber.transcribe(path, language=language)
    return result["text"]