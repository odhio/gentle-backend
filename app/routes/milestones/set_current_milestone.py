from sqlalchemy.ext.asyncio import AsyncSession
from crud.milestone import get_milestone_by_uuid, set_current_milestone
from pydantic import BaseModel
from schema import APIBaseModel


class SetCurrentMilestoneResponse(APIBaseModel):
    current_milestone_uuid: str


async def handler(
    session: AsyncSession, milestone_uuid: str
) -> SetCurrentMilestoneResponse:
    current_milestone = await set_current_milestone(session, milestone_uuid)
    return SetCurrentMilestoneResponse(current_milestone_uuid=current_milestone.uuid)
