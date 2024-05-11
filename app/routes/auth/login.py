from pydantic import BaseModel
from fastapi import Response
import traceback
from lib.auth import set_token, Token
from crud import user
from sqlalchemy.ext.asyncio import AsyncSession

class LoginRequest(BaseModel):
    name: str


class LoginResponse(BaseModel):
    success: bool


async def handler(req: LoginRequest, res: Response, session: AsyncSession):
    try:
        u = await user.get_by_name(session, req.name)
        if not u:
            return LoginResponse(success=False)
        set_token(res, Token(uuid=u.uuid, name=u.name, image=u.image))
        return LoginResponse(success=True)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return LoginResponse(success=False)
