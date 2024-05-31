from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import get_all_rooms, create_room, get_active_rooms, close_room, get_room_detail, get_all_rooms_detail

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
    result = await get_all_rooms.handler(session)
    print(result)
    return await get_all_rooms.handler(session)


@router.get("/get_active", response_model=get_active_rooms.GetActiveRoomsResponse)
async def _get_active_rooms(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_active_rooms.handler(session)


@router.post("/close/{room_uuid}")
async def _close_room(
    room_uuid: str,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(close_room.handler, room_uuid)


@router.get("/detail/{room_uuid}", response_model=get_room_detail.GetRoomDetailResponse)
async def _get_room_detail(
    room_uuid: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_room_detail.handler(session, room_uuid)


@router.get("/get_all/detail", response_model=get_all_rooms_detail.GetAllRoomsDetailResponse)
async def _get_all_rooms_detail(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_all_rooms_detail.handler(session)
