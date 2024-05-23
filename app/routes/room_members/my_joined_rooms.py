from sqlalchemy.ext.asyncio import AsyncSession
from crud.room_member import get_room_members_by_user_uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from domains.models import Emotion


class MyJoinedRoomRequest(BaseModel):
    user_uuid: str


class MyJoinedRoomResponse(BaseModel):
    room_uuid: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime]
    emotion: Optional[Emotion]


async def handler(session: AsyncSession, req: MyJoinedRoomRequest) -> MyJoinedRoomResponse:
    joined_romms = await get_room_members_by_user_uuid(session, req.user_uuid)
    if joined_romms is None:
        return None
    return MyJoinedRoomResponse(
        room_uuid=joined_romms.room.uuid,
        name=joined_romms.room.name,
        created_at=joined_romms.room.created_at,
        updated_at=joined_romms.room.updated_at,
        emotion=joined_romms.room.emotion,
    )
