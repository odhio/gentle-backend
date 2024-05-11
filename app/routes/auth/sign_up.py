from pydantic import BaseModel
from fastapi import Response
import traceback
from lib.auth import set_token, Token
from crud import user
from sqlalchemy.ext.asyncio import AsyncSession


class SignUpRequest(BaseModel):
    name: str
    image: str


class SignUpResponse(BaseModel):
    success: bool


async def handler(req: SignUpRequest, res: Response, session: AsyncSession):
    try:
        u = await user.get_user_by_name(session, req.name)
        if not u:
            u = await user.create_user(session=session, name=req.name, image=req.image)
        set_token(res, Token(uuid=u.uuid, name=u.name, image=u.image))
        return SignUpResponse(success=True)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return SignUpResponse(success=False)
