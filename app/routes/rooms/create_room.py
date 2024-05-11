from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import create_room
from pydantic import BaseModel
from schema import APIBaseModel


class CreateRoomRequest(BaseModel):
    room_uuid: str
    name: str


class CreateRoomResponse(APIBaseModel):
    room_uuid: str
    name: str


async def handler(session: AsyncSession, req: CreateRoomRequest) -> CreateRoomResponse:
    room = await create_room(session, req.room_uuid, req.name)
    return CreateRoomResponse(room_uuid=room.uuid, name=room.name)
