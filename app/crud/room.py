from domains import Room, RoomMember
from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


async def get_active_rooms(db: AsyncSession):
    query = select(Room).where(Room.closed_at.is_(None))
    result = await db.execute(query)
    return result.scalars().all()


async def get_all_rooms(db: AsyncSession):
    query = select(Room).order_by(asc(Room.closed_at))
    result = await db.execute(query)
    return result.scalars().all()


async def get_room_by_uuid(db: AsyncSession, room_uuid: str):
    query = (
        select(Room)
        .join(Room.members)
        .where(Room.uuid == room_uuid)
        .options(joinedload(Room.members).joinedload(RoomMember.user))
    )
    result = await db.execute(query)
    return result.scalars().first()


async def create_room(db: AsyncSession, room_uuid: str, name: str):
    room = Room(uuid=room_uuid, name=name)
    db.add(room)
    await db.flush()
    await db.refresh(room)

    return room


async def close_room(db: AsyncSession, room_uuid: str):
    query = select(Room).where(Room.uuid == room_uuid)
    room = (await db.execute(query)).scalars().first()
    room.closed_at = datetime.now()
    await db.flush()
    await db.refresh(room)

    return room


async def add_room_emotion(db: AsyncSession, room_uuid: str, emotion: str):
    query = select(Room).where(Room.uuid == room_uuid)
    room = (await db.execute(query)).scalars().first()
    room.emotion = emotion
    await db.flush()
    await db.refresh(room)

    return room


async def add_room_summary(db: AsyncSession, room_uuid: str, summary: str):
    query = select(Room).where(Room.uuid == room_uuid)
    room = (await db.execute(query)).scalars().first()
    room.summary = summary
    await db.flush()
    await db.refresh(room)

    return room


async def get_rooms_by_milestone_uuid(db: AsyncSession, milestone_uuid: str):
    query = select(Room).where(Room.milestone_uuid == milestone_uuid)
    result = await db.execute(query)
    return result.scalars().all()


async def add_room_schedule(db: AsyncSession, room_uuid: str, event: JSONB):
    query = select(Room).where(Room.uuid == room_uuid)
    room = (await db.execute(query)).scalars().first()
    room.google_schedule = event
    await db.flush()
    await db.refresh(room)

    return room
