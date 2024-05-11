from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import close_room, add_room_summary, add_room_emotion
from crud.room_member import (
    get_room_members_by_room_uuid,
    add_summary as add_member_summary,
)
from crud.message import get_messages_by_room_uuid
from pydantic import BaseModel
from schema import APIBaseModel
from domains import Emotion

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
    room_emotion: str


async def handler(session: AsyncSession, room_uuid: str) -> CloseRoomResponse:
    room = await close_room(session, room_uuid)
    room_members = await get_room_members_by_room_uuid(session, room.uuid)
    messages = await get_messages_by_room_uuid(session, room.uuid)

    member_summaries = []
    for member in room_members:
        member_messages = [
            message for message in messages if message.user.uuid == member.user_uuid
        ]
        member_messages_text = "\n".join(
            [
                f"発言: {message.message}、感情: {message.emotion}"
                for message in member_messages
            ]
        )
        print(member_messages_text)

        member_system_prompt = """デイリースプリントが終了しました。
参加者の全ての発言とその時の感情を基に、直近のユーザーのタスク進捗と会議中の感情についてまとめてください。
"""
        member_messages = [
            {"role": "system", "content": member_system_prompt},
            {"role": "user", "content": member_messages_text},
        ]
        member_res = _pipe(member_messages, **_generation_args)

        member_summaries.append(
            {"user_name": member.user.name, "summary": member_res[0]["generated_text"]}
        )

        await add_member_summary(session, member.uuid, member_res[0]["generated_text"])

    room_summary = "\n\n".join(
        [
            f"{member_summary['user_name']}:\n{member_summary['summary']}"
            for member_summary in member_summaries
        ]
    )

    room_system_prompt = """デイリースプリントが終了しました。
参加者全員の発言とその時の感情のまとめを基に、チーム全体のタスク進捗と会議中の感情についてまとめてください。
"""
    room_messages = [
        {"role": "system", "content": room_system_prompt},
        {"role": "user", "content": room_summary},
    ]
    room_res = _pipe(room_messages, **_generation_args)

    await add_room_summary(session, room.uuid, room_res[0]["generated_text"])

    emotions = [message.emotion for message in messages]
    emotion = max(set(emotions), key=emotions.count)
    await add_room_emotion(session, room.uuid, Emotion(emotion))

    return CloseRoomResponse(
        room_uuid=room.uuid,
        room_summary=room_res[0]["generated_text"],
        room_emotion=emotion,
    )
