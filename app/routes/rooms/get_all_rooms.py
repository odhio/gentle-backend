from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import get_all_rooms
from schema import APIBaseModel
from datetime import datetime


class Room(APIBaseModel):
    uuid: str
    name: str
    closed_at: datetime | None


class GetAllRoomsResponse(APIBaseModel):
    rooms: list[Room]


async def handler(session: AsyncSession) -> GetAllRoomsResponse:
    rooms = await get_all_rooms(session)
    return GetAllRoomsResponse(
        rooms=[
            Room(uuid=room.uuid, name=room.name, closed_at=room.closed_at)
            for room in rooms
        ]
    )
