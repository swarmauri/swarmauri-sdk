"""RFC-defined defaults for authorization server metadata.

These constants collect the well-known JWKS path and issuer base URL.
OIDC modules should import from here rather than redefining these defaults.
"""

from __future__ import annotations

import os
from typing import Final

JWKS_PATH: Final[str] = "/.well-known/jwks.json"
ISSUER: Final[str] = os.getenv("AUTHN_ISSUER", "https://authn.example.com")

__all__ = ["JWKS_PATH", "ISSUER"]
