from typing import Literal, Union
from pydantic import BaseModel
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


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


def predict(messages: Union[list[dict[str, str]], list[Message]]) -> str:
    _messages = []
    for message in messages:
        if isinstance(message, dict):
            m = Message.model_validate(message)
            _messages.append(m.model_dump())
        else:
            _messages.append(message.model_dump())

    res = _pipe(_messages, **_generation_args)
    return res[0]["generated_text"]
