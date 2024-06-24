from infra.db_connector import create_async_session_with_context
from crud.room import close_room, add_room_summary, add_room_emotion
from crud.room_member import (
    get_room_members_by_room_uuid,
    add_summary as add_member_summary,
)
from crud.message import get_messages_by_room_uuid, get_messages_by_room_uuid_user_joined
from pydantic import BaseModel
from domains import Emotion

from lib.analytics import create_tfidf_matrix

from openai import AsyncAzureOpenAI
import dotenv
import os
import logging

dotenv.load_dotenv()

version = os.environ.get("AZURE_OPENAI_PREVIEW_API_VERSION", "2024-03-01-preview")
model = os.environ.get("AZURE_OPENAI_MODEL")

openai_client = AsyncAzureOpenAI(
    api_version=version,
    api_key=os.environ.get("OPENAI_API_KEY"),
    azure_endpoint=os.environ.get("OPENAI_AZURE_ENDPOINT")
    )

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CloseRoomResponse(BaseModel):
    status: str


async def handler(room_uuid: str):
    async with create_async_session_with_context() as session:
        try:
            room = await close_room(session, room_uuid)
            room_members = await get_room_members_by_room_uuid(session, room.uuid)
            # ↓userテーブルを明示的にjoinedloadしてあげないとgreenlet_spawn has not been called…エラーが出ます
            messages = await get_messages_by_room_uuid_user_joined(session, room.uuid)
            logger.info(f"Got {len(messages)} messages for room {room.uuid}.")

        except Exception as e:
            logger.error(f"Failed to get/set information from the DB {room_uuid}: {e}")
            raise e
        member_summaries = []

        try:
            messages_list = [message.message for message in messages if message.message != ""]
            result = create_tfidf_matrix(messages_list)
            topics = [k for k, v in result.items() if v > 1]
            logger.info(f"Topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to get topics from messages: {e}")
            raise e

        for member in room_members:
            try:
                member_messages = [
                    message for message in messages if message.user.uuid == member.user_uuid and message.message != ""
                ]

                logger.info(f"Found {len(member_messages)} messages for member {member.uuid}.")
                if len(member_messages) == 0:
                    logger.info(f"No messages found for member {member.uuid}.")
                    continue

                member_messages_text = "\n".join(
                    [f"発言: {message.message}" for message in member_messages]
                )
            except Exception as e:
                logger.error(f"Failed to get messages for member {member.uuid}: {e}")
                raise e
            member_system_prompt = """
            ユーザーの全ての発言を要約してください。またユーザが抱える課題や関心を推定し要約に含めるようにしてください。
    """
            member_messages = [
                {"role": "system", "content": member_system_prompt},
                {"role": "user", "content": member_messages_text},
            ]
            try:
                member_res = await openai_client.chat.completions.create(
                    model=model,
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

            except Exception as e:
                logger.error(f"Failed to generate summary for member {member.uuid}: {e}")
                raise e
        try:
            room_summary = "\n\n".join(
                [f"{member_summary['user_name']}:\n{member_summary['summary']}" for member_summary in member_summaries]
            )

            room_system_prompt = """
        参加者全員の発言のまとめを基に、チーム全体の会話を要約し、課題があるときは今後採るべき方策ついて提案してください。
        """
            if len(topics) > 0:
                room_system_prompt += f"参考資料となる本会議におけるトピックは以下の通りです: {','.join(topics)}"
                logger.info(f"system prompt: {room_system_prompt}")
            room_messages = [
                {"role": "system", "content": room_system_prompt},
                {"role": "user", "content": room_summary},
            ]
        except Exception as e:
            logger.error(f"Failed to set all member's summary : {e}")
            raise e

        try:
            room_res = await openai_client.chat.completions.create(
                model=model,
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

        except Exception as e:
            logger.error(f"Failed to generate summary for room {room.uuid}: {e}")
            raise e
