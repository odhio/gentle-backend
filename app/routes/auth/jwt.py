from pydantic import BaseModel
from fastapi import Response
import traceback
from lib.auth import create_jwt, decode_jwt, Token


# Create
class AuthJWTRequest(BaseModel):
    name: str


class AuthJWTResponse(BaseModel):
    jwt: str


async def auth_jwt(req: AuthJWTRequest, res: Response) -> AuthJWTResponse:
    try:
        token = Token
        jwt = create_jwt(token)
        return AuthJWTResponse(jwt=jwt)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return AuthJWTResponse(jwt="")


# Read
class AuthMeRequest(BaseModel):
    jwt: str


class AuthMeResponse(BaseModel):
    uuid: str
    name: str
    image: str


async def auth_me(req: AuthMeRequest) -> AuthMeResponse:
    try:
        token = decode_jwt(req.jwt)
        return AuthMeResponse(uuid=token.uuid, name=token.name, image=token.image)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return AuthMeResponse(uuid="", name="", image="")
