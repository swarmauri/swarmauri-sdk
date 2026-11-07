"""HTTP Bearer credential extraction without token-format assumptions."""

from __future__ import annotations

from collections.abc import Mapping


class BearerTokenError(ValueError):
    """Raised when an HTTP Bearer credential is missing or malformed."""


class BearerTokenExtractor:
    """Extract a token from an RFC 6750-style Authorization header."""

    def __init__(self, header_name: str = "Authorization") -> None:
        self.header_name = header_name

    def extract(self, headers: Mapping[str, str]) -> str:
        """Return the Bearer credential without interpreting its contents."""

        authorization = headers.get(self.header_name)
        if authorization is None:
            authorization = headers.get(self.header_name.lower())
        if not authorization:
            raise BearerTokenError("Missing Authorization header")

        scheme, separator, credential = authorization.partition(" ")
        if not separator or scheme.casefold() != "bearer":
            raise BearerTokenError("Invalid authorization scheme")
        token = credential.strip()
        if not token:
            raise BearerTokenError("Missing Bearer token")
        return token
