from sqlalchemy.ext.asyncio import AsyncSession
from crud.message import get_messages_by_room_uuid
from pydantic import BaseModel
from schema import APIBaseModel
from datetime import datetime


class ResponseMessage(APIBaseModel):
    uuid: str
    message: str
    emotion: str
    created_at: datetime
    pressure: float


class GetMessageByRoomRequest(APIBaseModel):
    room_uuid: str


class GetMessageByRoomResponse(APIBaseModel):
    messages: list[ResponseMessage]


async def handler(session: AsyncSession, room_uuid: str) -> GetMessageByRoomResponse:
    result = await get_messages_by_room_uuid(session, room_uuid)
    print(result)
    return GetMessageByRoomResponse(
        messages=[
            ResponseMessage(
                uuid=message.uuid,
                message=message.message,
                emotion=message.emotion,
                created_at=message.created_at,
                pressure=message.pressure,
            )
            for message in result
        ]
    )
