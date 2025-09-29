from __future__ import annotations

import base64
import hashlib
from urllib.parse import urlsplit, urlunsplit


def canon_htm_htu(
    method: str, url: str, *, include_query: bool = False
) -> tuple[str, str]:
    normalized_method = method.upper()
    parts = urlsplit(url)
    query = parts.query if include_query else ""
    htu = urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))
    return normalized_method, htu


def b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sha256_b64u(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return b64u_encode(digest)
