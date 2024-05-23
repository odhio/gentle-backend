from fastapi import APIRouter, Depends, Response
from infra.db_connector import get_async_session

from . import login, sign_up, logout, jwt, oauth

router = APIRouter()


@router.post("/login", response_model=login.LoginResponse)
async def _login(
    req: login.LoginRequest,
    res: Response,
    session=Depends(get_async_session),
):
    print(req.model_dump_json())
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


@router.post("/me", response_model=jwt.AuthMeResponse)
async def _auth_me(req: jwt.AuthMeRequest, res: Response):
    return await jwt.auth_me(req)


@router.post("/oauth2/me", response_model=oauth.OAuthMeResponse)
async def _oauth2_me(req: oauth.OAuthMeRequest, res: Response, session=Depends(get_async_session)):
    return await oauth.handler(req, res, session)
