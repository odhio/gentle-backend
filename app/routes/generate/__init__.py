from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from . import phi

router = APIRouter()


class GenerateResponse(BaseModel):
    content: str


@router.post("/", response_model=phi.GenerateResponse)
def _generate(req: phi.GenerateRequest):
    try:
        return phi.handler(req)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        raise HTTPException(status_code=422, detail="UNPROCESSABLE_ENTITY")
