import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from openai import OpenAI

from api.contracts import Language, TranscribeResponse

router = APIRouter(prefix="/api/voice", tags=["voice"])


def whisper(audio: bytes, filename: str, language: str) -> str:
    client = OpenAI(
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.getenv("GROQ_API_KEY", ""),
        timeout=float(os.getenv("LLM_TIMEOUT_S", "45")),
        max_retries=0,
    )
    model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")
    return client.audio.transcriptions.create(model=model, file=(filename, audio), language=language).text


@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe(audio: UploadFile = File(...), language: Language = Form(...)):
    try:
        text = whisper(audio.file.read(), audio.filename or "voice.webm", language)
    except Exception as exc:
        raise HTTPException(503, "Voice is unavailable right now. Please type instead.") from exc
    return TranscribeResponse(text=text.strip())
