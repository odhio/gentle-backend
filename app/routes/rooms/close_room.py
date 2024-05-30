from sqlalchemy.ext.asyncio import AsyncSession
from crud.room import close_room, add_room_summary, add_room_emotion, add_room_schedule
from crud.room_member import (
    get_room_members_by_room_uuid,
    add_summary as add_member_summary,
)
from crud.message import get_messages_by_room_uuid
from pydantic import BaseModel
from domains import Emotion

import openai
import dotenv
import os
import time
import json
from datetime import datetime, timezone, timedelta


dotenv.load_dotenv()
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-0125")
openai_client = openai.Client()

class CloseRoomResponse(BaseModel):
    status: str


async def handler(room_uuid: str, session: AsyncSession):
    room = await close_room(room_uuid)
    room_members = await get_room_members_by_room_uuid(session, room.uuid)
    messages = await get_messages_by_room_uuid(session, room.uuid)

    member_summaries = []
    for member in room_members:
        member_messages = [message for message in messages if message.user.uuid == member.user_uuid]
        member_messages_text = "\n".join(
            [f"発言: {message.message}、感情: {message.emotion}" for message in member_messages]
        )

        member_system_prompt = """
        ユーザーの全ての発言と感情を基に、直近のタスク進捗と会議中の感情についてまとめてください。
"""
        member_messages = [
            {"role": "system", "content": member_system_prompt},
            {"role": "user", "content": member_messages_text},
        ]

        member_res = openai_client.chat.completions.create(
            model=openai_model,
            messages=member_messages,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )

        member_res = member_res.choices[0].message.content

        member_summaries.append({"user_name": member.user.name, "summary": member_res})
        await add_member_summary(session, member.uuid, member_res)

    room_summary = "\n\n".join(
        [f"{member_summary['user_name']}:\n{member_summary['summary']}" for member_summary in member_summaries]
    )

    room_system_prompt = """
参加者全員の発言とその時の感情のまとめを基に、チーム全体のタスク進捗と会議中の感情についてまとめてください。
"""
    room_messages = [
        {"role": "system", "content": room_system_prompt},
        {"role": "user", "content": room_summary},
    ]
    room_res = openai_client.chat.completions.create(
        model=openai_model,
        messages=room_messages,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=False,
    )

    room_res = room_res.choices[0].message.content

    await add_room_summary(session, room.uuid, room_res)

    emotions = [message.emotion for message in messages]
    emotion = max(set(emotions), key=emotions.count)
    await add_room_emotion(session, room.uuid, Emotion(emotion))

    # NOTE:　議事メモから Google Calendar 登録用JSONBを吐き出す処理を試験的に追加しました。
    # ルーム単位で紐づけていますが、実運用的にはユーザ単位でリレーションを張るべきかもしれません。
    schedule_system_prompt = """ユーザの会話に日時や場所など将来の確定した予定が含まれているときは、その情報を詳細かつ端的に抽出しユーザをサポートしてください。
    """
    schedule_messages = [
        {"role": "system", "content": schedule_system_prompt},
        {"role": "user", "content": room_summary},
    ]

    schedule_init_tools = [
        {
            "type": "function",
            "function": {
                "name": "is_included",
                "description": "日時場所を含む将来の確定した予定が会話に含まれているか",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_included": {
                            "type": "boolean",
                            "description": "日時場所を含む将来の確定した予定が会話に含まれているか",
                        }
                    },
                    "required": ["is_included"],
                },
            },
        }
    ]
    schedule_init_function_response = openai_client.chat.completions.create(
        messages=schedule_messages,
        temperature=1,
        model=openai_model,
        stop=None,
        top_p=1,
        tools=schedule_init_tools,
        tool_choice={
            "type": "function",
            "function": {"name": "is_included"},
        },
    )

    tool_calls = schedule_init_function_response.choices[0].message.tool_calls[0]
    args_1 = json.loads(tool_calls.function.arguments)
    if "is_included" in args_1.keys():
        if args_1["is_included"]:
            required_tools = ["summary", "who", "where", "why", "when", "how"]
            detail_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "set_calendar",
                        "description": "メンバーのカレンダーに予定（詳細な内容と日時、場所）を登録します。固有名詞は除外することなく、予定の内容を詳細に抽出してください。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string",
                                    "description": "予定の具体的かつ詳細な内容を抽出する。",
                                },
                                "who": {"type": "string", "description": "誰が、誰に対してといった人に関する情報"},
                                "where": {"type": "string", "description": "予定の場所"},
                                "why": {"type": "string", "description": "予定の目的や経緯"},
                                "when": {
                                    "type": "string",
                                    "description": "会話から推定される予定の開始時刻",
                                },
                                "how": {"type": "string", "description": "交通手段や持参物など"},
                            },
                            "required": required_tools,
                        },
                    },
                }
            ]
            schedule_detail_function_response = openai_client.chat.completions.create(
                messages=schedule_messages,
                temperature=1,
                max_tokens=500,
                model=openai_model,
                stop=None,
                top_p=1,
                tools=detail_tools,
                tool_choice={
                    "type": "function",
                    "function": {"name": "set_calendar"},
                },
            )
            tool_call = schedule_detail_function_response.choices[0].message.tool_calls[0]
            args_2 = json.loads(tool_call.function.arguments)
            if all(tool in args_2.keys() for tool in required_tools):
                event = {
                    "summary": f'{args_2["summary"]}',
                    "location": f'{args_2["where"]}',
                    "description": (
                        f'【参加者等】{args_2["who"]}\n【時期等】{args_2["when"]}\n【詳細】{args_2["why"]}、{args_2["how"]}'
                    ),
                    "start": {
                        "dateTime": datetime.fromtimestamp(int(time.time()), timezone(timedelta(hours=9))).isoformat(),
                        "timeZone": "Asia/Tokyo",
                    },
                    "end": {
                        "dateTime": datetime.fromtimestamp(int(time.time()), timezone(timedelta(hours=9))).isoformat(),
                        "timeZone": "Asia/Tokyo",
                    },
                }
                print(event)
                await add_room_schedule(session, room.uuid, event)
