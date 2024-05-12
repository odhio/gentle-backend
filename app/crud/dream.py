from domains import Dream
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
import uuid


async def get_dream(db: AsyncSession):
    query = select(Dream)
    result = await db.execute(query)
    return result.scalars().first()


async def create_dream(db: AsyncSession, name: str, description: str):
    dream_uuid = str(uuid.uuid4())
    dream = Dream(uuid=dream_uuid, name=name, description=description)
    db.add(dream)
    await db.flush()
    await db.refresh(dream)

    return dream
