from fastapi import APIRouter

router = APIRouter()

from ...rfc import rfc6749_token, rfc7662_introspection  # noqa: E402,F401
from . import oidc  # noqa: E402,F401
