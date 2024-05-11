from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import get_active_rooms
from schema import APIBaseModel


class Room(APIBaseModel):
    uuid: str
    name: str


class GetActiveRoomsResponse(APIBaseModel):
    rooms: list[Room]


async def handler(session: AsyncSession) -> GetActiveRoomsResponse:
    rooms = await get_active_rooms(session)
    return GetActiveRoomsResponse(
        rooms=[Room(uuid=room.uuid, name=room.name) for room in rooms]
    )
