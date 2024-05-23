from sqlalchemy.ext.asyncio import AsyncSession
from crud.room_member import get_all_room_members
from schema import APIBaseModel
from datetime import datetime


class RoomMember(APIBaseModel):
    uuid: str
    room_uuid: str
    user_uuid: str | None
    summary: str | None


class GetAllRoomMemberResponse(APIBaseModel):
    room_members: list[RoomMember]


async def handler(session: AsyncSession) -> GetAllRoomMemberResponse:
    room_members = await get_all_room_members(session)
    return GetAllRoomMemberResponse(
        room_members=[
            RoomMember(
                uuid=member.uuid,
                room_uuid=member.room_uuid,
                user_uuid=member.user_uuid,
                summary=member.summary,
            )
            for member in room_members
        ]
    )
