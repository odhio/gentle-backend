from pydantic import BaseModel
from fastapi import Response
import traceback
from lib.auth import set_token, Token


class SignUpRequest(BaseModel):
    id: str
    password: str
    image: str


class SignUpResponse(BaseModel):
    success: bool


async def handler(req: SignUpRequest, res: Response):
    try:
        set_token(res, Token(id=req.id))
        return SignUpResponse(success=True)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return SignUpResponse(success=False)
