from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.contracts import Language, TranscribeResponse

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe(audio: UploadFile = File(...), language: Language = Form(...)):
    raise HTTPException(501)
