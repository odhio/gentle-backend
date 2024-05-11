from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import time
from routes import audio, generate

logging.basicConfig(level=logging.INFO)

app = FastAPI()


# 速度計測用のミドルウェア
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    if request.url.path != "/":
        print(f"{request.url.path} - Process time: {process_time}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])


def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug", reload=True)


if __name__ == "__main__":
    main()
