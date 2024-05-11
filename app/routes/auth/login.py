from pydantic import BaseModel
from fastapi import Response
import traceback
from lib.auth import set_token, Token


class LoginRequest(BaseModel):
    id: str


class LoginResponse(BaseModel):
    success: bool


async def handler(req: LoginRequest, res: Response):
    try:
        set_token(res, Token(id=req.id))
        return LoginResponse(success=True)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return LoginResponse(success=False)
