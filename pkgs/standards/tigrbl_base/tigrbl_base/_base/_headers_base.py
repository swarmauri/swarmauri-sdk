from __future__ import annotations


class HeadersBase(dict[str, str]):
    """Base header mapping type for response implementations."""


class HeaderCookiesBase(dict[str, str]):
    """Base cookie mapping type for response implementations."""


__all__ = ["HeaderCookiesBase", "HeadersBase"]
