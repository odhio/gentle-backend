from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import get_all_rooms
from schema import APIBaseModel


class Room(APIBaseModel):
    uuid: str
    name: str


class GetAllRoomsResponse(APIBaseModel):
    rooms: list[Room]


async def handler(session: AsyncSession) -> GetAllRoomsResponse:
    rooms = await get_all_rooms(session)
    return GetAllRoomsResponse(
        rooms=[Room(uuid=room.uuid, name=room.name) for room in rooms]
    )
