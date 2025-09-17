from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from typing import Optional
import uuid
import json

app = FastAPI(title="Audio Transcription Service", version="1.0.0")

# Ensure uploads directory exists
os.makedirs("/app/uploads", exist_ok=True)

class TranscriptionRequest(BaseModel):
    audio_url: Optional[str] = None
    language: str = "en"

class TranscriptionResponse(BaseModel):
    transcription: str
    confidence: float
    language: str
    duration: float

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """Mock audio transcription - simulates speech-to-text conversion"""
    
    # Mock transcriptions for common property queries
    mock_transcriptions = [
        "Show me 3-bedroom villas in Dubai under AED 2 million with swimming pool",
        "I'm looking for a 2-bedroom apartment in Downtown Dubai with Burj Khalifa view",
        "Find me properties in Dubai Hills Estate with private garden",
        "What are the available 4-bedroom houses in Emirates Hills",
        "Show me luxury apartments in Palm Jumeirah with sea view",
        "I need a studio apartment in Dubai Marina under 800k",
        "Find properties with gym and swimming pool amenities",
        "What's available in Jumeirah Village Circle for families"
    ]
    
    import random
    transcription = random.choice(mock_transcriptions)
    
    return TranscriptionResponse(
        transcription=transcription,
        confidence=0.95,
        language=request.language,
        duration=3.2
    )

@app.post("/upload-audio", response_model=UploadResponse)
async def upload_audio_file(file: UploadFile = File(...)):
    """Upload audio file for transcription"""
    
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    stored_filename = f"{file_id}{file_extension}"
    file_path = f"/app/uploads/{stored_filename}"
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=len(content)
    )

@app.post("/transcribe-file/{file_id}", response_model=TranscriptionResponse)
async def transcribe_uploaded_file(file_id: str, language: str = "en"):
    """Transcribe previously uploaded audio file"""
    
    # In a real implementation, you would:
    # 1. Find the file by file_id
    # 2. Use a speech-to-text service (Whisper, Google Speech-to-Text, etc.)
    # 3. Return the actual transcription
    
    # Mock response
    mock_transcription = "Show me 3-bedroom villas in Dubai under AED 2 million with swimming pool"
    
    return TranscriptionResponse(
        transcription=mock_transcription,
        confidence=0.92,
        language=language,
        duration=4.1
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "audio_transcription", "port": 8002}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
