from typing import Literal, Union
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from openai import AsyncOpenAI

openai_cient = AsyncOpenAI()


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


async def predict(messages: Union[list[dict[str, str]], list[Message]]) -> str:
    _messages = []
    for message in messages:
        if isinstance(message, dict):
            m = Message.model_validate(message)
            _messages.append(m.model_dump())
        else:
            _messages.append(message.model_dump())

        res = await openai_cient.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=_messages,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )
    return res.choices[0].message.content
