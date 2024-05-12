from sqlalchemy.ext.asyncio import AsyncSession
from crud.milestone import get_milestones
from pydantic import BaseModel
from schema import APIBaseModel
from datetime import datetime


class Milestone(APIBaseModel):
    milestone_uuid: str
    name: str
    description: str
    due_date: datetime


class GetMilestonesResponse(APIBaseModel):
    milestones: list[Milestone]


async def handler(session: AsyncSession, dream_uuid: str) -> GetMilestonesResponse:
    milestones = await get_milestones(session, dream_uuid)
    return GetMilestonesResponse(
        milestones=[
            Milestone(
                milestone_uuid=milestone.uuid,
                name=milestone.name,
                description=milestone.description,
                due_date=milestone.due_date,
            )
            for milestone in milestones
        ]
    )
