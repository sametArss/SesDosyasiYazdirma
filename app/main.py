from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from app.transcribe import transcribe_file
import uvicorn

app = FastAPI(title="Whisper Local Transcribe API")

@app.post("/transcribe/")
async def transcribe_endpoint(file: UploadFile = File(...)):
    # Geçici olarak dosyayı kaydet
    contents = await file.read()
    tmp_path = "temp_upload_" + file.filename  # "temp_upload" yerine "temp_upload_" daha iyi
    with open(tmp_path, "wb") as f:
        f.write(contents)

    try:
        text = transcribe_file(tmp_path)
        return JSONResponse({"text": text})
    finally:
        import os
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)