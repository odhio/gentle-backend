from domains import Milestone, CurrentMilestone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
import uuid
from datetime import datetime, timedelta


async def get_milestones(db: AsyncSession, dream_uuid: str):
    query = select(Milestone).where(Milestone.dream_uuid == dream_uuid)
    result = await db.execute(query)
    return result.scalars().all()


async def create_milestone(
    db: AsyncSession, dream_uuid: str, name: str, description: str, days: int
):
    milestone_uuid = str(uuid.uuid4())
    # 10日後の日付を取得
    due_date = datetime.now() + timedelta(days=days)
    milestone = Milestone(
        uuid=milestone_uuid,
        dream_uuid=dream_uuid,
        name=name,
        description=description,
        due_date=due_date,
    )
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)

    return milestone


async def set_current_milestone(db: AsyncSession, milestone_uuid: str):
    current_milestone_uuid = str(uuid.uuid4())
    current_milestone = CurrentMilestone(
        uuid=current_milestone_uuid,
        milestone_uuid=milestone_uuid,
    )
    db.add(current_milestone)
    await db.flush()
    await db.refresh(current_milestone)

    return current_milestone


async def get_current_milestone(db: AsyncSession, dream_uuid: str):
    query = (
        select(CurrentMilestone)
        .join(Milestone)
        .where(Milestone.dream_uuid == dream_uuid)
        .options(joinedload(CurrentMilestone.milestone).joinedload(Milestone.rooms))
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_milestone_by_uuid(db: AsyncSession, milestone_uuid: str):
    query = select(Milestone).where(Milestone.uuid == milestone_uuid)
    result = await db.execute(query)
    return result.scalars().first()
