from domains import RoomMember
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
import uuid

async def get_room_members_by_room_uuid(db: AsyncSession, room_uuid: str):
    query = (
        select(RoomMember)
        .where(RoomMember.room_uuid == room_uuid)
        .options(joinedload(RoomMember.user))
    )
    result = await db.execute(query)
    return result.scalars().all()


async def join_room(db: AsyncSession, room_uuid: str, user_uuid: str):
    member_uuid = str(uuid.uuid4())
    room_member = RoomMember(uuid=member_uuid, room_uuid=room_uuid, user_uuid=user_uuid)
    db.add(room_member)
    await db.flush()
    await db.refresh(room_member)

    return room_member


async def add_summary(db: AsyncSession, room_member_uuid: str, summary: str):
    room_member = select(RoomMember).where(RoomMember.uuid == room_member_uuid)
    room_member.summary = summary

    return room_member
