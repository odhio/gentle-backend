from fastapi import APIRouter, Depends
from . import create_plot
from infra.db_connector import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/create_plot/{room_uuid}", response_model=create_plot.CreatePlotResponse)
async def _create_plot(room_uuid: str, session: AsyncSession = Depends(get_async_session)):
    return await create_plot.handler(session, room_uuid)
