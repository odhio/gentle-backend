from typing import Literal, Union
from pydantic import BaseModel
from schema import APIBaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from openai import openai, AsyncOpenAI

openai_client = AsyncOpenAI()


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
        model="gpt-3.5-turbo-0125",
        messages=_messages,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=False,
    )
    return GenerateResponse(content=res.choices[0].message.content)
