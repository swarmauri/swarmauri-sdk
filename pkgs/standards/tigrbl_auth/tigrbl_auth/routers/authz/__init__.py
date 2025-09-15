from fastapi import APIRouter

router = APIRouter()

from tigrbl_auth.rfc import rfc6749, rfc7662  # noqa: E402,F401
from . import oidc  # noqa: E402,F401
