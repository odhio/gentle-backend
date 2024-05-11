from fastapi import APIRouter, Depends, Response
from infra.db_connector import get_async_session

from . import login, sign_up, logout

router = APIRouter()


@router.post("/login", response_model=login.LoginResponse)
async def _login(
    req: login.LoginRequest,
    res: Response,
    session=Depends(get_async_session),
):
    return await login.handler(req, res, session)


@router.post("/sign-up", response_model=sign_up.SignUpResponse)
async def _sign_up(
    req: sign_up.SignUpRequest,
    res: Response,
    session=Depends(get_async_session),
):
    return await sign_up.handler(req, res, session)


@router.post("/logout", response_model=logout.LogoutResponse)
async def _logout(res: Response):
    return await logout.handler(res)
