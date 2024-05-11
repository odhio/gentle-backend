from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import get_user_by_name
from pydantic import BaseModel
from schema import APIBaseModel


class GetUserByNameRequest(BaseModel):
    name: str


class GetUserByNameResponse(APIBaseModel):
    uuid: str
    name: str
    image: str


async def handler(session: AsyncSession, name: str) -> GetUserByNameResponse:
    user = await get_user_by_name(session, name)
    return GetUserByNameResponse(uuid=user.uuid, name=user.name, image=user.image)
