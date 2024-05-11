import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from .upload import LabelsResponse, predict_audio

router = APIRouter()


@router.post("/upload", response_model=LabelsResponse)
def _audio_upload(audio: UploadFile = File(...)):
    try:
        content = audio.file.read()
        return predict_audio(content)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")
