import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import upload
from infra.db_connector import get_async_session

router = APIRouter()


@router.post("/upload/{message_uuid}", response_model=upload.LabelsResponse)
async def _audio_upload(
    message_uuid: str,
    audio: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        content = audio.file.read()
        return await upload.predict_audio(session, message_uuid, content)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")
