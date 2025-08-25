# noqa: D401
"""Helpers for OAuth 2.0 Resource Indicators (RFC 8707).

This module validates the ``resource`` parameter defined in RFC 8707.
Values MUST be absolute URIs, MAY appear multiple times, and MUST NOT
contain fragments. The helper returns the first valid resource or
``None`` if none were supplied.
"""

from __future__ import annotations

from typing import Optional, Sequence
from urllib.parse import urlparse

RFC8707_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8707"


def extract_resource(resources: Sequence[str]) -> Optional[str]:
    """Return the first valid resource indicator from ``resources``.

    Raises ``ValueError`` if any supplied value is not an absolute URI or
    contains a fragment component as required by RFC 8707 §2.
    """

    if not resources:
        return None
    for value in resources:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc or parsed.fragment:
            raise ValueError("invalid resource indicator")
    return resources[0]


__all__ = ["extract_resource", "RFC8707_SPEC_URL"]
