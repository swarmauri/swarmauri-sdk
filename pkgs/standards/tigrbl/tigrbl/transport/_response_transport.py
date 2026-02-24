"""Response finalization helpers for ASGI/WSGI transports."""

from __future__ import annotations

from typing import Any


NO_BODY_STATUS = set(range(100, 200)) | {204, 205, 304}


def finalize_transport_response(
    scope: dict[str, Any],
    status: int,
    headers: list[tuple[bytes, bytes]],
    body: bytes,
) -> tuple[list[tuple[bytes, bytes]], bytes]:
    """Enforce HTTP body/header invariants immediately before transport writes."""

    method = str(scope.get("method", "GET")).upper()

    if method == "HEAD" or status in NO_BODY_STATUS:
        drop = {b"content-length", b"content-type", b"transfer-encoding"}
        headers = [(k, v) for (k, v) in headers if k.lower() not in drop]
        return headers, b""

    headers = [(k, v) for (k, v) in headers if k.lower() != b"content-length"]
    headers.append((b"content-length", str(len(body)).encode("latin-1")))

    return headers, body


__all__ = ["NO_BODY_STATUS", "finalize_transport_response"]
