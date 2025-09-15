from tigrbl_auth.deps import APIRouter
from tigrbl_auth.rfc import rfc6749_token, rfc7662_introspection

router = APIRouter()
router.include_router(rfc6749_token.router)
router.include_router(rfc7662_introspection.router)

from . import oidc  # noqa: E402,F401
