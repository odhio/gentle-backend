from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import create_user, get_all_users, get_user_by_name


router = APIRouter()


@router.post("/create", response_model=create_user.CreateUserResponse)
async def _create_user(
    create_user_req: create_user.CreateUserRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_user.handler(session, create_user_req)


@router.get("/get_by_name", response_model=get_user_by_name.GetUserByNameResponse)
async def _get_user_by_name(
    name: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_user_by_name.handler(session, name)


@router.get("/get_all", response_model=get_all_users.GetAllUsersResponse)
async def _get_all_users(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_all_users.handler(session)
