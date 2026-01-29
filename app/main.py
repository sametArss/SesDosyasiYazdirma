from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import aiofiles
import os
from pathlib import Path
import logging
from typing import Optional
from contextlib import asynccontextmanager

from .transcribe import get_transcriber

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Temp klasör
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Desteklenen formatlar
SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}


# Lifespan event (startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Model yükle
    logger.info("🚀 Uygulama başlatılıyor...")
    get_transcriber()  # Model yükle
    logger.info("✅ Model hazır!")
    
    yield
    
    # Shutdown: Temizlik
    logger.info("🛑 Uygulama kapatılıyor...")
    # Geçici dosyaları temizle
    for file in UPLOAD_DIR.glob("*"):
        file.unlink()
    logger.info("✅ Temizlik tamamlandı.")


app = FastAPI(
    title="Whisper Transcribe API",
    description="Türkçe ses dosyalarını metne çeviren hızlı API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (Frontend için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prod'da sadece domain'ini yaz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response modeli
class TranscriptionResponse(BaseModel):
    text: str
    language: str = "tr"
    file_name: str
    segments: Optional[list] = None


def cleanup_file(file_path: Path):
    """Background task ile dosya silme"""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"🗑️ Silindi: {file_path.name}")
    except Exception as e:
        logger.error(f"❌ Silme hatası: {e}")


@app.get("/")
async def root():
    return {
        "message": "Whisper Transcribe API",
        "endpoints": {
            "POST /transcribe/": "Ses dosyası yükle ve transkribe et",
            "GET /health/": "API sağlık kontrolü"
        }
    }


@app.get("/health/")
async def health_check():
    """API sağlık kontrolü"""
    transcriber = get_transcriber()
    return {
        "status": "healthy",
        "model": transcriber.model_name,
        "device": transcriber.device
    }


@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = "tr"
):
    """
    Ses dosyasını metne çevirir.
    
    - **file**: Ses dosyası (mp3, wav, m4a, etc.)
    - **language**: Dil kodu (varsayılan: tr)
    """
    # Format kontrolü
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen format: {file_ext}. Desteklenenler: {SUPPORTED_FORMATS}"
        )
    
    # Geçici dosya oluştur
    temp_file = UPLOAD_DIR / f"{os.urandom(8).hex()}_{file.filename}"
    
    try:
        # Dosyayı async yaz
        async with aiofiles.open(temp_file, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"📁 Dosya alındı: {file.filename} ({len(content)} bytes)")
        
        # Transcribe et
        transcriber = get_transcriber()
        result = transcriber.transcribe(str(temp_file), language=language)
        
        # Background'da dosyayı sil
        background_tasks.add_task(cleanup_file, temp_file)
        
        return TranscriptionResponse(
            text=result["text"],
            language=result["language"],
            file_name=file.filename,
            segments=result.get("segments")
        )
    
    except Exception as e:
        # Hata durumunda dosyayı hemen sil
        if temp_file.exists():
            temp_file.unlink()
        
        logger.error(f"❌ Transcribe hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Dev modda otomatik reload
        log_level="info"
    )