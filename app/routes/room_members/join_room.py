from sqlalchemy.ext.asyncio import AsyncSession
from crud.room_member import join_room
from pydantic import BaseModel
from schema import APIBaseModel


class JoinRoomRequest(BaseModel):
    room_uuid: str
    user_uuid: str


class JoinRoomResponse(APIBaseModel):
    success: bool


async def handler(session: AsyncSession, req: JoinRoomRequest) -> JoinRoomResponse:
    room_member = await join_room(session, req.room_uuid, req.user_uuid)
    return JoinRoomResponse(success=room_member is not None)
