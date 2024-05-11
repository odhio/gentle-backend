from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import create_user
from pydantic import BaseModel
from schema import APIBaseModel


class CreateUserRequest(BaseModel):
    name: str
    image: str


class CreateUserResponse(APIBaseModel):
    user_uuid: str
    name: str
    image: str


async def handler(session: AsyncSession, req: CreateUserRequest) -> CreateUserResponse:
    user = await create_user(session, req.name, req.image)
    return CreateUserResponse(user_uuid=user.uuid, name=user.name, image=user.image)
