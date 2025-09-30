from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from .i_appserver import HttpApp, IAppServer


class AppServerMixin(IAppServer, BaseModel):
    """Stores and validates an application callback for app-terminating transports."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    _app: Optional[HttpApp] = None

    def set_app(self, app: HttpApp) -> None:
        if not callable(app):
            raise TypeError("app must be callable")
        self._app = app

    @property
    def app(self) -> HttpApp:
        if self._app is None:

            async def _default_app(method: str, path: str, headers, body: bytes):
                return 200, {"content-type": "application/octet-stream"}, body

            return _default_app  # type: ignore[return-value]
        return self._app
