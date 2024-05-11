import traceback
from pydantic import BaseModel
from typing import Literal, Union
from lib import wav2vec2

PressureLevel = Literal["low", "medium", "high"]


class LabelsResponse(BaseModel):
    result: Union[str, None]
    pressure: PressureLevel


def predict_audio(content: bytes) -> LabelsResponse:
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
    return LabelsResponse(result=most_emote, pressure=level)
