from domains import RoomMember
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload


async def get_room_members_by_room_uuid(db: AsyncSession, room_uuid: str):
    query = select(RoomMember).where(RoomMember.room_uuid == room_uuid)
    result = await db.execute(query)
    return result.scalars().all()


async def join_room(db: AsyncSession, room_uuid: str, user_uuid: str):
    room_member = RoomMember(room_uuid=room_uuid, user_uuid=user_uuid)
    db.add(room_member)
    await db.flush()
    await db.refresh(room_member)

    return room_member
