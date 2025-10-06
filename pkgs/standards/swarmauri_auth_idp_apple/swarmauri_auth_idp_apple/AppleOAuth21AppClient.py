"""Apple OAuth 2.1 app client placeholder implementation."""

from __future__ import annotations

from typing import Literal

from swarmauri_base.auth_idp import OAuth21AppClientBase

from ._app_client_base import AppleAppClientMixin


class AppleOAuth21AppClient(AppleAppClientMixin, OAuth21AppClientBase):
    """Document the lack of Apple OAuth 2.1 client credentials support."""

    type: Literal["AppleOAuth21AppClient"] = "AppleOAuth21AppClient"
