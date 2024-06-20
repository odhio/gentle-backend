"""

OAuth で認証を行ったユーザの情報をBEでマッピングするためのモジュールです。
現状は、
① Oauthユーザの名前/imageを登録してアプリケーション用UUIDの払い出し
② 既に登録済みのOauthユーザの場合は、照合して払い出し
のみを行っています。

"""

from pydantic import BaseModel
from fastapi import Response
from crud import user
from sqlalchemy.ext.asyncio import AsyncSession


class OAuthMeRequest(BaseModel):
    name: str
    image: str|None = None


class OAuthMeResponse(BaseModel):
    success: bool
    uuid: str | None = None


async def handler(req: OAuthMeRequest, res: Response, session: AsyncSession):
    try:
        u = await user.get_user_by_name(session, req.name)
        if not u and req.name and req.image:
            print("create user")
            u = await user.create_user(session=session, name=req.name, image=req.image)

        if u and u.image == req.image:
            print("update user")
            u = await user.update_user(session=session, uuid=u.uuid, name=req.name, image=req.image)

        return OAuthMeResponse(success=True, uuid=u.uuid)
    except Exception as e:
        print(e)
        return OAuthMeResponse(success=False, uuid=None)
