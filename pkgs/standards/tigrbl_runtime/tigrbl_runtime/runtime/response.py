"""Runtime-facing helpers for response specification adaptation."""

from __future__ import annotations

from typing import Optional

from tigrbl_atoms.atoms.response.renderer import ResponseHints
from tigrbl_core._spec.response_spec import ResponseSpec


def infer_hints(
    spec: Optional[ResponseSpec],
) -> tuple[ResponseHints, Optional[bool], Optional[str]]:
    """Convert a resolved response spec into renderer-compatible response hints."""
    if spec is None:
        return ResponseHints(), None, None

    headers = dict(spec.headers or {})
    if spec.cache_control:
        headers.setdefault("Cache-Control", spec.cache_control)

    hints = ResponseHints(
        media_type=spec.media_type,
        status_code=spec.status_code or 200,
        headers=headers,
        filename=spec.filename,
        download=bool(spec.download) if spec.download is not None else False,
        etag=spec.etag,
    )
    return hints, spec.envelope, spec.media_type


__all__ = ["ResponseHints", "infer_hints"]
