from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import get_users
from pydantic import BaseModel
from schema import APIBaseModel


class User(BaseModel):
    uuid: str
    name: str
    image: str


class GetAllUsersResponse(APIBaseModel):
    users: list[User]


async def handler(session: AsyncSession) -> GetAllUsersResponse:
    users = await get_users(session)
    return GetAllUsersResponse(
        users=[User(uuid=user.uuid, name=user.name, image=user.image) for user in users]
    )
