import typing as t

from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from starlette.responses import RedirectResponse

from ...libs.dependencies.common import get_oauth_client, settings_factory
from ...libs.settings import AppSettings


router = APIRouter(tags=["Admin"])


@router.get("/auth/google")
async def login_google(
    request: Request,
    oauth_client: t.Any = Depends(get_oauth_client),
    settings: AppSettings = Depends(settings_factory),
) -> Response:
    token = await oauth_client.authorize_access_token(request)

    if not (user := token.get("userinfo")) and user["email"] not in settings.allowed_users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    request.session["user"] = user

    return RedirectResponse(request.url_for("admin:index"))
