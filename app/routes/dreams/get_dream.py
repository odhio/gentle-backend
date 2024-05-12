from sqlalchemy.ext.asyncio import AsyncSession
from crud.dream import get_dream
from pydantic import BaseModel
from schema import APIBaseModel
from domains import Emotion


class GetDreamResponse(APIBaseModel):
    dream_uuid: str
    name: str
    description: str


async def handler(session: AsyncSession) -> GetDreamResponse:
    dream = await get_dream(session)
    return GetDreamResponse(
        dream_uuid=dream.uuid, name=dream.name, description=dream.description
    )
