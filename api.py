from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import base64
import requests

# Checking API status
"""
app = FastAPI()
@app.post("/predict")
def predict():
    return {"status": "API working"}
"""

app = FastAPI()
API_KEY = "sk_test_123456789"  # to be changed later

languages = {
    "Tamil",
    "English",
    "Hindi",
    "Malayalam",
    "Telugu"
}

#Request
class VoiceDetectionRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str | None = None
    audioUrl: str | None = None  # for MP3 URL
    message: str | None = None  
    
    class Config:
        extra = "allow"

# Response
class VoiceDetectionResponse(BaseModel):
    status: str
    language: str
    classification: str
    confidenceScore: float
    explanation: str

# endpoint
@app.post("/api/voice-detection", response_model=VoiceDetectionResponse)
def detect_voice(
    request: VoiceDetectionRequest,
    x_api_key: str = Header(None, alias="x-api-key"),
    authorization: str = Header(None)
):
    # API key validation
    api_key = None

    if x_api_key:
        api_key = x_api_key

    elif authorization and authorization.startswith("Bearer "):
        api_key = authorization.replace("Bearer ", "")

    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    # language validation
    if request.language not in languages:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language"
        )

    # audio format validation
    if request.audioFormat.lower() != "mp3":
        raise HTTPException(
            status_code=400,
            detail="Only MP3 format is supported"
        )

    # base64 validation
    audio_bytes = None

    if request.audioBase64:
        try:
            audio_bytes = base64.b64decode(request.audioBase64)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid Base64 audio data"
            )
    
    elif request.audioUrl:
        try:
            response = requests.get(request.audioUrl, timeout=10)
            response.raise_for_status()
            audio_bytes = response.content
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Unable to download audio from URL"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="audioBase64 or audioUrl must be provided"
        )

    # to be replaced by ML model
    classification = "HUMAN"
    confidence = 0.50
    explanation = "Baseline response before model inference"

    return {
        "status": "success",
        "language": request.language,
        "classification": classification,
        "confidenceScore": confidence,
        "explanation": explanation
    }