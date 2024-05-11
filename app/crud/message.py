from domains import Message, Emotion
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload


async def get_messages_by_room_uuid(db: AsyncSession, room_uuid: str):
    query = select(Message).where(Message.room_uuid == room_uuid)
    result = await db.execute(query)
    return result.scalars().all()


async def create_message(
    db: AsyncSession, room_uuid: str, user_uuid: str, message: str, emotion: Emotion
):
    message = Message(
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        message=message,
        emotion=emotion,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)

    return message
