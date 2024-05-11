from sqlalchemy.ext.asyncio import AsyncSession
from crud.message import create_message
from pydantic import BaseModel
from schema import APIBaseModel
from domains import Emotion


class CreateMessageRequest(BaseModel):
    room_uuid: str
    user_uuid: str
    message: str


class CreateMessageResponse(APIBaseModel):
    message_uuid: str


async def handler(
    session: AsyncSession, req: CreateMessageRequest
) -> CreateMessageResponse:
    message = await create_message(
        session, req.room_uuid, req.user_uuid, req.message, Emotion.NEUTRAL
    )
    return CreateMessageResponse(message_uuid=message.uuid)
