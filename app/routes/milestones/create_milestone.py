from sqlalchemy.ext.asyncio import AsyncSession
from crud.milestone import create_milestone
from pydantic import BaseModel
from schema import APIBaseModel


class CreateMilestoneRequest(BaseModel):
    dream_uuid: str
    name: str
    description: str
    days: int


class CreateMilestoneResponse(APIBaseModel):
    milestone_uuid: str
    name: str
    description: str


async def handler(
    session: AsyncSession, req: CreateMilestoneRequest
) -> CreateMilestoneResponse:
    milestone = await create_milestone(
        session, req.dream_uuid, req.name, req.description, req.days
    )
    return CreateMilestoneResponse(
        milestone_uuid=milestone.uuid,
        name=milestone.name,
        description=milestone.description,
        days=milestone.due_date,
    )
