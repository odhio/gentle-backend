from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import join_room

router = APIRouter()


@router.post("/join", response_model=join_room.JoinRoomResponse)
async def _join_room(
    join_room_req: join_room.JoinRoomRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await join_room.handler(session, join_room_req)
