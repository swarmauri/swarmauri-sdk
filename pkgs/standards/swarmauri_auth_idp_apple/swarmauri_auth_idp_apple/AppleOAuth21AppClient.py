"""Apple OAuth 2.1 app client placeholder implementation."""

from __future__ import annotations

from swarmauri_base.auth_idp import OAuth21AppClientBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(OAuth21AppClientBase, "AppleOAuth21AppClient")
class AppleOAuth21AppClient(OAuth21AppClientBase):
    """Document the lack of Apple OAuth 2.1 client credentials support."""

    ...
