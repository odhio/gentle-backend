from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import (
    create_milestone,
    get_milestones,
    set_current_milestone,
    get_current_milestone,
)

router = APIRouter()


@router.post("/create", response_model=create_milestone.CreateMilestoneResponse)
async def _create_milestone(
    create_milestone_req: create_milestone.CreateMilestoneRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_milestone.handler(session, create_milestone_req)


@router.get(
    "/get_list/{dream_uuid}", response_model=get_milestones.GetMilestonesResponse
)
async def _get_milestones(
    dream_uuid: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_milestones.handler(session, dream_uuid)


@router.post(
    "/set_current/{milestone_uuid}",
    response_model=set_current_milestone.SetCurrentMilestoneResponse,
)
async def _set_current_milestone(
    milestone_uuid: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await set_current_milestone.handler(session, milestone_uuid)


@router.get(
    "/get_current/{dream_uuid}",
    response_model=get_current_milestone.GetCurrentMilestoneResponse,
)
async def _get_current_milestone(
    dream_uuid: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_current_milestone.handler(session, dream_uuid)
