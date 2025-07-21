"""
auth_authn_idp
==============
OpenID‑Connect / OAuth2 Provider with multi‑tenant isolation.

Typical ASGI boot
-----------------
    from fastapi import FastAPI
    from auto_authn import settings, lifespan, router

    app = FastAPI(title="Auth‑AuthN IdP", lifespan=lifespan)
    app.include_router(router)              # /.well‑known, /token, /userinfo, …
"""

from __future__ import annotations

import importlib.metadata as _importlib_metadata
import logging
import sys
from typing import TYPE_CHECKING

# --------------------------------------------------------------------------- #
# Version                                                                     #
# --------------------------------------------------------------------------- #

try:  # pragma: no cover
    __version__: str = _importlib_metadata.version("auth-authn")
except _importlib_metadata.PackageNotFoundError:  # editable installs
    __version__ = "0.0.0-dev"

# --------------------------------------------------------------------------- #
# Public‑facing api                                                           #
# --------------------------------------------------------------------------- #
from .config import settings  # noqa: E402  (import after __version__)
from .db import lifespan  # FastAPI lifespan context (engine bootstrap)
from .provider import router  # FastAPI router with OIDC endpoints

# convenience import if users want to build providers manually
from .provider import _provider_factory as build_provider  # type: ignore

__all__: tuple[str, ...] = (
    "settings",
    "lifespan",
    "router",
    "build_provider",
    "__version__",
)


# --------------------------------------------------------------------------- #
# Logging preset (opt‑in)                                                     #
# --------------------------------------------------------------------------- #
def _install_default_logging() -> None:  # pragma: no cover
    """
    Activate a *minimal* structured logging configuration **only** when the host
    application hasn’t configured logging yet.  This prevents duplicate
    handler spam when uvicorn or gunicorn already set root handlers.
    """
    root = logging.getLogger()
    if root.handlers:
        return  # app already configured logging

    level = settings.log_level.upper()
    fmt = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s "
        "(%(filename)s:%(lineno)d)"
    )
    handler: logging.Handler
    if sys.stderr.isatty():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
    else:  # running inside k8s / docker
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt))
    root.setLevel(level)
    root.addHandler(handler)
    root.debug("auth_authn logging initialised (level=%s)", level)


_install_default_logging()

# --------------------------------------------------------------------------- #
# Type‑checking friendly re‑exports                                           #
# --------------------------------------------------------------------------- #
if TYPE_CHECKING:  # pragma: no cover
    from fastapi import APIRouter
    from .config import Settings
    from oic.oic.provider import Provider

    # Re‑export types so IDEs know about them
    settings: "Settings"
    lifespan: callable  # FastAPI lifespan async‑context fn
    router: "APIRouter"
    build_provider: callable[[...], "Provider"]
