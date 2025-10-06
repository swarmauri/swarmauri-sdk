"""Apple OIDC 1.0 app client placeholder implementation."""

from __future__ import annotations

from typing import Literal

from swarmauri_base.auth_idp import OIDC10AppClientBase

from ._app_client_base import AppleAppClientMixin


class AppleOIDC10AppClient(AppleAppClientMixin, OIDC10AppClientBase):
    """Document the lack of Apple OIDC 1.0 client credentials support."""

    type: Literal["AppleOIDC10AppClient"] = "AppleOIDC10AppClient"
