from typing import Literal
from pydantic import BaseModel
from schema import APIBaseModel

from openai import AsyncAzureOpenAI
import os

version = os.environ.get("AZURE_OPENAI_PREVIEW_API_VERSION", "2024-03-01-preview")
model = os.environ.get("AZURE_OPENAI_MODEL")

openai_client = AsyncAzureOpenAI(
    api_version=version,
    api_key=os.environ.get("OPENAI_API_KEY"),
    azure_endpoint=os.environ.get("OPENAI_AZURE_ENDPOINT")
    )

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class GenerateRequest(BaseModel):
    messages: list[Message]


class GenerateResponse(APIBaseModel):
    content: str


async def handler(req: GenerateRequest) -> str:
    _messages = []
    for message in req.messages:
        if isinstance(message, dict):
            m = Message(**message)
            _messages.append(m.dict())
        else:
            _messages.append(message.dict())

    res = await openai_client.chat.completions.create(
        model=model,
        messages=_messages,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=False,
    )
    return GenerateResponse(content=res.choices[0].message.content)
