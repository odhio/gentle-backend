from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import close_room
from pydantic import BaseModel
from schema import APIBaseModel


class CloseRoomResponse(APIBaseModel):
    room_uuid: str
    name: str


async def handler(session: AsyncSession, room_uuid: str) -> CloseRoomResponse:
    room = await close_room(session, room_uuid)
    return CloseRoomResponse(room_uuid=room.uuid, name=room.name)
