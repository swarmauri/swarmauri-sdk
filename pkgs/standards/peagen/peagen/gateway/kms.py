"""Utilities for wrapping key material with an external KMS."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from .runtime_cfg import settings


async def wrap_key_with_kms(key: str) -> str:
    """Return KMS-wrapped *key* if a KMS endpoint is configured.

    Parameters
    ----------
    key:
        The raw key material to wrap.

    Returns
    -------
    str
        The wrapped key returned by the KMS or the original key when no KMS is
        configured or the request fails.
    """

    kms_url = settings.kms_wrap_url
    if not kms_url:
        return key

    payload: dict[str, Any] = {
        "key_material_b64": base64.b64encode(key.encode()).decode()
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(kms_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("wrapped_key_b64", key)
    except Exception:
        # Fail open – loggers in calling code can capture details if desired.
        return key
