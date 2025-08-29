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


async def unwrap_key_with_kms(wrapped: str) -> str:
    """Return KMS-unwrapped ``wrapped`` if a KMS endpoint is configured.

    Parameters
    ----------
    wrapped:
        The wrapped key material to unwrap.

    Returns
    -------
    str
        The unwrapped key returned by the KMS or the original value when no
        KMS is configured or the request fails.
    """

    kms_url = settings.kms_unwrap_url
    if not kms_url:
        return wrapped

    payload: dict[str, Any] = {"wrapped_key_b64": wrapped}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(kms_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("key_material_b64")
            if raw is None:
                return wrapped
            try:
                return base64.b64decode(raw.encode()).decode()
            except Exception:
                return wrapped
    except Exception:
        # Fail open – loggers in calling code can capture details if desired.
        return wrapped
