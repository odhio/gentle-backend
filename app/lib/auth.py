from typing import Optional
from fastapi import Request, Response
from pydantic import BaseModel

__token_key = "access_token"


class Token(BaseModel):
    id: str


def get_token(req: Request) -> Optional[Token]:
    return Token(**req.cookies.get(__token_key, {}))


def set_token(res: Response, token: Token):
    res.set_cookie(
        key=__token_key,
        value=token.model_dump_json(),
        path="/",
        httponly=True,
        secure=True,
        samesite="none",
        max_age=3600000,
    )


def delete_token(res: Response):
    res.delete_cookie(key=__token_key)
