from domains import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload

import uuid


async def get_users(
    session: AsyncSession,
):
    stmt = select(User)
    return (await session.execute(stmt)).scalars().all()


async def get_user_by_name(session: AsyncSession, name: str):
    stmt = select(User).where(User.name == name)
    return (await session.execute(stmt)).scalars().first()


async def create_user(session: AsyncSession, name: str, image: str):
    user_uuid = str(uuid.uuid4())
    user = User(uuid=user_uuid, name=name, image=image)
    session.add(user)
    await session.flush()
    await session.refresh(user)

    return user
