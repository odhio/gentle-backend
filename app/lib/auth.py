from typing import Optional
from fastapi import Request, Response
from pydantic import BaseModel

__token_key = "access_token"


class Token(BaseModel):
    uuid: str
    name: str
    image: str


def get_token(req: Request) -> Optional[Token]:
    return Token(**req.cookies.get(__token_key, {}))


def set_token(res: Response, token: Token):
    res.set_cookie(
        key=__token_key,
        value=token.model_dump_json(),
        httponly=True,
        secure=False,
        expires=3600000,
    )


def delete_token(res: Response):
    res.delete_cookie(key=__token_key)
