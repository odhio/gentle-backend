import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from pydantic import BaseModel
from typing import Literal, Union
import traceback
from lib import wav2vec2, phi
from routes import auth

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# 速度計測用のミドルウェア
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    if request.url.path != "/":
        print(f"{request.url.path} - Process time: {process_time}")
    return response


PressureLevel = Literal["low", "medium", "high"]


class LabelsResponse(BaseModel):
    result: Union[str, None]
    pressure: PressureLevel


@app.post("/api/audio/upload", response_model=LabelsResponse)
def _audio_upload(audio: UploadFile = File(...)):
    try:
        content = audio.file.read()
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
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")


class GenerateResponse(BaseModel):
    content: str


@app.post("/api/generate", response_model=GenerateResponse)
def _generate(req: list[phi.Message]):
    try:
        res = phi.predict(req)
        return GenerateResponse(content=res)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")


app.include_router(auth.router, prefix="/api/auth")


def main():
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="debug", reload=True)


if __name__ == "__main__":
    main()
