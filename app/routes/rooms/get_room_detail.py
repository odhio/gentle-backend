from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import get_room_by_uuid
from schema import APIBaseModel
from datetime import datetime
from typing import Any, Optional


class RoomMember(APIBaseModel):
    member_uuid: str
    user_uuid: str
    name: str
    summary: str


class GetRoomDetailResponse(APIBaseModel):
    uuid: str
    name: str
    summary: str
    emotion: str
    room_members: list[RoomMember]
    google_schedule: Optional[dict[str, Any]]


async def handler(session: AsyncSession, room_uuid: str) -> GetRoomDetailResponse:
    room = await get_room_by_uuid(session, room_uuid)
    return GetRoomDetailResponse(
        uuid=room.uuid,
        name=room.name,
        summary=room.summary,
        emotion=room.emotion,
        room_members=[
            RoomMember(
                member_uuid=room_member.uuid,
                user_uuid=room_member.user_uuid,
                name=room_member.user.name,
                summary=room_member.summary,
            )
            for room_member in room.members
        ],
        google_schedule=room.google_schedule,
    )
