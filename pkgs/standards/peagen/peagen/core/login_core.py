"""Helpers for authenticating a user and uploading their public key to a Peagen
gateway.

This module is intentionally free of any task-queue or database logic: it runs
entirely on the *client* side.

Typical usage
-------------
>>> from pathlib import Path
>>> from peagen.core.login_core import login
>>> login(key_dir=Path("~/.peagen/keys").expanduser(),
...       passphrase=None,
...       gateway_url="https://gw.peagen.com/rpc")
{'result': 'ok'}

The caller (CLI, GUI, or test) is responsible for interpreting the returned JSON-
RPC envelope.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import httpx

from peagen.plugins.secret_drivers import AutoGpgDriver

__all__ = ["login"]

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
_JSONRPC_VERSION = "2.0"


def _build_payload(public_key: str) -> dict[str, Any]:
    """Return a minimal JSON-RPC request body for Keys.upload."""
    return {
        "jsonrpc": _JSONRPC_VERSION,
        "method": "Keys.upload",
        "params": {"public_key": public_key},
        "id": 1,  # single-shot call; clients may overwrite
    }


def login(
    *,
    key_dir: Path | None = None,
    passphrase: Optional[str] = None,
    gateway_url: str = DEFAULT_GATEWAY,
    timeout_s: float = 10.0,
) -> dict[str, Any]:
    """Ensure a GPG key-pair exists and upload the public key to *gateway_url*.

    Parameters
    ----------
    key_dir
        Directory that should contain (or will receive) the key-pair.
        If *None*, the AutoGpgDriver default (~/.peagen/keys) is used.
    passphrase
        Optional passphrase for unlocking an encrypted private key.
    gateway_url
        Fully-qualified URL of the Peagen gateway JSON-RPC endpoint.
        Defaults to ``http://localhost:8000/rpc``.
    timeout_s
        HTTP timeout in seconds for the upload call.

    Returns
    -------
    dict
        The parsed JSON response envelope from the gateway.

    Raises
    ------
    httpx.HTTPError
        For transport-level problems (DNS, TLS, etc.) or a non-2xx HTTP status.
    json.JSONDecodeError
        If the gateway returns invalid JSON.
    RuntimeError
        If the gateway responds with a JSON-RPC *error* object.
    """
    # 1. Ensure key-pair exists locally (generates if absent)
    drv = AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)

    public_key = drv.pub_path.read_text(encoding="utf-8")

    # 2. Assemble JSON-RPC request
    payload = _build_payload(public_key)

    # 3. Upload
    with httpx.Client(timeout=timeout_s) as client:
        response = client.post(gateway_url, json=payload)
        response.raise_for_status()

    data: dict[str, Any] = json.loads(response.text)

    # 4. Surface gateway-level errors as Python exceptions
    if "error" in data:
        raise RuntimeError(
            f"Gateway returned JSON-RPC error: {data['error']}"
        )

    return data
