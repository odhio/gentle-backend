from domains import Room
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload


async def get_active_rooms(db: AsyncSession):
    query = select(Room).where(Room.closed_at.is_(None))
    result = await db.execute(query)
    return result.scalars().all()


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
