from sqlalchemy.ext.asyncio import AsyncSession
from crud.dream import create_dream
from pydantic import BaseModel
from schema import APIBaseModel
from domains import Emotion


class CreateDreamRequest(BaseModel):
    name: str
    description: str


class CreateDreamResponse(APIBaseModel):
    dream_uuid: str
    name: str
    description: str


async def handler(
    session: AsyncSession, req: CreateDreamRequest
) -> CreateDreamResponse:
    dream = await create_dream(session, req.name, req.description)
    return CreateDreamResponse(
        dream_uuid=dream.uuid, name=dream.name, description=dream.description
    )
