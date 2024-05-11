from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import get_all_rooms, create_room, get_active_rooms, close_room

router = APIRouter()


@router.post("/create", response_model=create_room.CreateRoomResponse)
async def _create_room(
    create_room_req: create_room.CreateRoomRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_room.handler(session, create_room_req)


@router.get("/get_all", response_model=get_all_rooms.GetAllRoomsResponse)
async def _get_all_rooms(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_all_rooms.handler(session)


@router.get("/get_active", response_model=get_active_rooms.GetActiveRoomsResponse)
async def _get_active_rooms(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_active_rooms.handler(session)


@router.delete("/close/{room_uuid}", response_model=close_room.CloseRoomResponse)
async def _close_room(
    room_uuid: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await close_room.handler(session, room_uuid)
