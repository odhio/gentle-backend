from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import create_dream, get_dream

router = APIRouter()


@router.post("/create", response_model=create_dream.CreateDreamResponse)
async def _create_dream(
    create_dream_req: create_dream.CreateDreamRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_dream.handler(session, create_dream_req)


@router.get("/", response_model=get_dream.GetDreamResponse)
async def _get_dream(
    session: AsyncSession = Depends(get_async_session),
):
    return await get_dream.handler(session)
