from sqlalchemy.ext.asyncio import AsyncSession
from crud.milestone import get_current_milestone
from crud.room import get_rooms_by_milestone_uuid
from schema import APIBaseModel
from datetime import datetime
from domains import Emotion


class Room(APIBaseModel):
    uuid: str
    name: str
    closed_at: datetime | None
    emotion: Emotion


class GetCurrentMilestoneResponse(APIBaseModel):
    uuid: str
    name: str
    description: str
    rooms: list[Room]


async def handler(
    session: AsyncSession, dream_uuid: str
) -> GetCurrentMilestoneResponse:
    current_milestone = await get_current_milestone(session, dream_uuid)
    rooms = await get_rooms_by_milestone_uuid(session, current_milestone.milestone_uuid)
    return GetCurrentMilestoneResponse(
        uuid=current_milestone.milestone_uuid,
        name=current_milestone.milestone.name,
        description=current_milestone.milestone.description,
        rooms=[
            Room(
                uuid=room.uuid,
                name=room.name,
                closed_at=room.closed_at,
                emotion=room.emotion,
            )
            for room in rooms
        ],
    )
