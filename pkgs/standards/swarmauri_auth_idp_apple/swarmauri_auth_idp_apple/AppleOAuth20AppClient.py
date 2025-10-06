"""Apple OAuth 2.0 app client placeholder implementation."""

from __future__ import annotations

from typing import Literal

from swarmauri_base.auth_idp import OAuth20AppClientBase

from ._app_client_base import AppleAppClientMixin


class AppleOAuth20AppClient(AppleAppClientMixin, OAuth20AppClientBase):
    """Document the lack of Apple OAuth 2.0 client credentials support."""

    type: Literal["AppleOAuth20AppClient"] = "AppleOAuth20AppClient"
