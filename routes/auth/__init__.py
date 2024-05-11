from fastapi import FastAPI, Response

from . import login, sign_up, logout

router = FastAPI()


@router.post("/login", response_model=login.LoginResponse)
def _login(req: login.LoginRequest, res: Response):
    return login.handler(req, res)


@router.post("/sign-up", response_model=sign_up.SignUpResponse)
def _sign_up(req: sign_up.SignUpRequest, res: Response):
    return sign_up.handler(req, res)


@router.post("/logout", response_model=logout.LogoutResponse)
def _logout(res: Response):
    return logout.handler(res)
