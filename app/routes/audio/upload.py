import traceback
from pydantic import BaseModel
from typing import Literal, Union
from lib import wav2vec2
from crud.message import add_message_emotion
from sqlalchemy.ext.asyncio import AsyncSession


PressureLevel = Literal["low", "medium", "high"]


class LabelsResponse(BaseModel):
    result: Union[str, None]
    pressure: PressureLevel


async def predict_audio(session: AsyncSession, message_uuid: str, content: bytes) -> LabelsResponse:
    emotions, pressure = wav2vec2.predict(content)

    level: PressureLevel = "high"
    if pressure < 0.02:
        level = "low"
    elif pressure < 0.04:
        level = "medium"

    emote_count_dict = {}
    for emotion in emotions:
        emote_count_dict[emotion] = emote_count_dict.get(emotion, 0) + 1

    most_emote = max(emote_count_dict, key=emote_count_dict.get)
    message = await add_message_emotion(session, message_uuid, most_emote, pressure)
    return LabelsResponse(result=most_emote, pressure=level)
