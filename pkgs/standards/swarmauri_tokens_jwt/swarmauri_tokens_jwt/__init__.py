"""JWT token service plugin.

This package exposes the :class:`JWTTokenService` used for minting and
verifying JSON Web Tokens within the Swarmauri framework.
"""

from .JWTTokenService import JWTTokenService

__all__ = ["JWTTokenService"]
