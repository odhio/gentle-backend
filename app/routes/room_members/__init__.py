from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import join_room, my_joined_rooms, get_all_room_members

router = APIRouter()


@router.post("/join", response_model=join_room.JoinRoomResponse)
async def _join_room(
    join_room_req: join_room.JoinRoomRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await join_room.handler(session, join_room_req)


@router.post("/my_joined_rooms", response_model=my_joined_rooms.MyJoinedRoomResponse)
async def _my_joined_rooms(
    my_joined_rooms_req: my_joined_rooms.MyJoinedRoomRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await my_joined_rooms.handler(session, my_joined_rooms_req)


@router.get("/get_all", response_model=get_all_room_members.GetAllRoomMemberResponse)
async def _get_all_room_members(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_all_room_members.handler(session)
