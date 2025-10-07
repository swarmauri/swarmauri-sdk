"""Apple OIDC 1.0 app client placeholder implementation."""

from __future__ import annotations

from swarmauri_base.auth_idp import OIDC10AppClientBase
from swarmauri_base.ComponentBase import ComponentBase

from .internal import AppleAppClientMixin


@ComponentBase.register_type(OIDC10AppClientBase, "AppleOIDC10AppClient")
class AppleOIDC10AppClient(AppleAppClientMixin, OIDC10AppClientBase):
    """Document the lack of Apple OIDC 1.0 client credentials support."""

    ...
