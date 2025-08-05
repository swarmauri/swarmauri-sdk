"""Helpers for authenticating a user and uploading their public key to a Peagen
gateway – refactored for AutoAPIClient.

The function still:

1. Ensures a local GPG key-pair exists (generating one if absent).
2. Uploads the *public* key to the JSON-RPC gateway.
3. Returns the validated success envelope or raises for any error.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import httpx

from autoapi_client import AutoAPIClient  # ← new client
from autoapi.v2 import AutoAPI  # ← for .get_schema()
from peagen.orm import PublicKey  # ORM resource

from peagen.defaults import DEFAULT_GATEWAY
from peagen.plugins.cryptos import ParamikoCrypto

__all__ = ["login"]


# ----------------------------------------------------------------------
def _schema(tag: str):
    """Shortcut to the server-generated schema for the PublicKey resource."""
    return AutoAPI.get_schema(PublicKey, tag)


def login(
    *,
    key_dir: Path | None = None,
    passphrase: Optional[str] = None,
    gateway_url: str = DEFAULT_GATEWAY,
    timeout_s: float = 10.0,
) -> dict[str, Any]:
    """Ensure a key-pair exists and upload the public key to *gateway_url*.

    Raises
    ------
    httpx.HTTPError
        Network or non-2xx HTTP error from the gateway.
    RuntimeError
        JSON-RPC error returned by the gateway.
    """
    # 1 ─ ensure local SSH key-pair
    drv = ParamikoCrypto(key_dir=key_dir, passphrase=passphrase)
    public_key = drv.public_key_str()          # returns single-line OpenSSH key

    # 2 ─ build request/response schemas dynamically
    SCreate = _schema("create")
    SRead = _schema("read")

    params = SCreate(public_key=public_key, title="default")

    # 3 ─ JSON-RPC call via AutoAPIClient
    with AutoAPIClient(gateway_url, client=httpx.Client(timeout=timeout_s)) as rpc:
        try:
            result = rpc.call("PublicKeys.create", params=params, out_schema=SRead)
        except (httpx.HTTPError, RuntimeError):
            raise

    # 4 ─ return success as plain dict for callers that expect JSON
    return result.model_dump()