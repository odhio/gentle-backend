from fastapi import APIRouter, Response

from . import login, sign_up, logout

router = APIRouter()


@router.post("/login", response_model=login.LoginResponse)
async def _login(req: login.LoginRequest, res: Response):
    return await login.handler(req, res)


@router.post("/sign-up", response_model=sign_up.SignUpResponse)
async def _sign_up(req: sign_up.SignUpRequest, res: Response):
    return await sign_up.handler(req, res)


@router.post("/logout", response_model=logout.LogoutResponse)
async def _logout(res: Response):
    return await logout.handler(res)
