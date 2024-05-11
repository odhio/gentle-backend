from pydantic import BaseModel
from fastapi import Response
from lib.auth import delete_token
import traceback


class LogoutResponse(BaseModel):
    success: bool


async def handler(res: Response):
    try:
        delete_token(res)
        return LogoutResponse(success=True)
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return LogoutResponse(success=False)
