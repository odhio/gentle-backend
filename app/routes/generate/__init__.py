from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from .phi import predict, Message

router = APIRouter()


class GenerateResponse(BaseModel):
    content: str


@router.post("/", response_model=GenerateResponse)
def _generate(req: list[Message]):
    try:
        res = predict(req)
        return GenerateResponse(content=res)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")
