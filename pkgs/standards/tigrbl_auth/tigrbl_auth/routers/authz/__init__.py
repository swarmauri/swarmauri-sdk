from tigrbl_auth.deps import TigrblApi
from tigrbl_auth.rfc import rfc6749_token, rfc7662_introspection

api = TigrblApi()
api.include_router(rfc6749_token.api)
api.include_router(rfc7662_introspection.api)

router = api

from . import oidc  # noqa: E402,F401

__all__ = ["api", "router"]
