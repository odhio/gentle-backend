from pydantic import BaseModel
from infra.db_connector import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import create_message

router = APIRouter()


@router.post("/create", response_model=create_message.CreateMessageResponse)
async def _create_message(
    create_message_req: create_message.CreateMessageRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_message.handler(session, create_message_req)
