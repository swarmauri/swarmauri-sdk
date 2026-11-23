"""Shared mixin for unsupported Apple Sign-in app clients."""

from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import ConfigDict


class AppleAppClientMixin:
    """Mixin that reports unsupported Apple client credential flows."""

    model_config = ConfigDict(extra="forbid")
    unsupported_message: ClassVar[str] = (
        "Apple does not issue generic client_credentials access tokens. "
        "Use user login flows instead."
    )

    async def access_token(self, scope: Optional[str] = None) -> str:  # noqa: D401
        """Always raise to signal the unsupported grant."""

        raise NotImplementedError(self.unsupported_message)
