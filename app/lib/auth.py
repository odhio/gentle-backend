from typing import Optional, Union
from fastapi import Request, Response
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import os
import dotenv
from jose import jwt

dotenv.load_dotenv()


__token_key = "access_token"
__secreat_key = os.getenv("SECRET_KEY", None)
__algorithm = os.getenv("SECRET_ALGORITHM", None)


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


def create_jwt(user: Token, expires_delta: Union[timedelta, None] = None) -> str:
    try:
        if not __secreat_key or not __algorithm:
            raise Exception("SECRET_KEY or SECRET_ALGORITHM is not set.")

        to_encode = user.model_dump().copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, __secreat_key, algorithm=__algorithm)
        return encoded_jwt

    except Exception as e:
        print(e)
        return None


def decode_jwt(jwt_token: str) -> Token:
    try:
        if not __secreat_key or not __algorithm:
            raise Exception("SECRET_KEY or SECRET_ALGORITHM is not set.")

        payload = jwt.decode(jwt_token, __secreat_key, algorithms=[__algorithm])
        return Token(**payload)
    except Exception as e:
        print(e)
        return None
