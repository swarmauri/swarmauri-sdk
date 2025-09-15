from ...deps import APIRouter

router = APIRouter()

from . import rfc6749, rfc7662, oidc  # noqa: E402,F401
