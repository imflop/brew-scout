import typing as t

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse


class AdminAuthenticationBackend(AuthenticationBackend):
    def __init__(self, secret_key: str, client: t.Any):
        self.client = client
        super().__init__(secret_key)

    async def login(self, request: Request) -> bool:
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        if not request.session.get("user"):
            redirect_uri = request.url_for("login_google")
            return await self.client.authorize_redirect(request, redirect_uri)

        return True
