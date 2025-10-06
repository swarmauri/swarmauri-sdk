"""Apple OAuth 2.0 app client placeholder implementation."""

from __future__ import annotations

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20AppClientBase

from .internal import AppleAppClientMixin


@ComponentBase.register_type(OAuth20AppClientBase, "AppleOAuth20AppClient")
class AppleOAuth20AppClient(AppleAppClientMixin, OAuth20AppClientBase):
    """Document the lack of Apple OAuth 2.0 client credentials support."""
    ...