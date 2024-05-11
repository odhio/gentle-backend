from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import close_room
from crud.room_member import get_room_members_by_room_uuid
from crud.message import get_messages_by_room_uuid
from pydantic import BaseModel
from schema import APIBaseModel

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

torch.random.manual_seed(0)

_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-128k-instruct",
    device_map="cuda" if torch.cuda.is_available() else "auto",
    torch_dtype="auto",
    trust_remote_code=True,
)
_tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct")

_pipe = pipeline(
    "text-generation",
    model=_model,
    tokenizer=_tokenizer,
)

_generation_args = {
    "max_new_tokens": 1000,
    "return_full_text": False,
    "do_sample": True,
}
class CloseRoomResponse(APIBaseModel):
    room_uuid: str
    room_summary: str


async def handler(session: AsyncSession, room_uuid: str) -> CloseRoomResponse:
    room = await close_room(session, room_uuid)
    room_member = await get_room_members_by_room_uuid(session, room.uuid)
    messages = await get_messages_by_room_uuid(session, room.uuid)

    return CloseRoomResponse(room_uuid=room.uuid, name=room.name)
