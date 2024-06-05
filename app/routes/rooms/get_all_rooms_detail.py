from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import get_all_rooms, get_room_by_uuid
from schema import APIBaseModel
from datetime import datetime


class RoomMember(APIBaseModel):
    member_uuid: str
    user_uuid: str
    name: str
    summary: str


class RoomDetail(APIBaseModel):
    uuid: str
    name: str
    summary: str
    emotion: str
    closed_at: datetime | None
    room_members: list[RoomMember]


class GetAllRoomsDetailResponse(APIBaseModel):
    rooms: list[RoomDetail]


async def handler(session: AsyncSession) -> GetAllRoomsDetailResponse:
    result = []
    rooms = await get_all_rooms(session)
    for target in rooms:
        room = await get_room_by_uuid(session, target.uuid)
        result.append(
            RoomDetail(
                uuid=room.uuid,
                name=room.name,
                summary=room.summary,
                emotion=room.emotion,
                closed_at=room.closed_at,
                room_members=[
                    RoomMember(
                        member_uuid=room_member.uuid,
                        user_uuid=room_member.user_uuid,
                        name=room_member.user.name,
                        summary=room_member.summary,
                    )
                    for room_member in room.members
                ],
            )
        )
    return GetAllRoomsDetailResponse(rooms=result)
