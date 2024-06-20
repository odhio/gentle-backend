from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from . import gpt

router = APIRouter()


class GenerateResponse(BaseModel):
    content: str


@router.post("/", response_model=gpt.GenerateResponse)
def _generate(req: gpt.GenerateRequest):
    try:
        return gpt.handler(req)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")
