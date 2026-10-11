from fastapi import APIRouter, File, Form, UploadFile

from api.contracts import Language, TranscribeResponse

router = APIRouter(prefix="/api/voice", tags=["voice"])


# shortcut: audio is received and discarded, canned text returned; V2 sends it to the ASR service
@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe(audio: UploadFile = File(...), language: Language = Form(...)):
    return TranscribeResponse(text="I want to start a dairy with five animals.")
