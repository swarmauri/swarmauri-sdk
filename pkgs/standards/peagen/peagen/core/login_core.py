"""Helpers for user authentication."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.protocols import Request, KEYS_UPLOAD

DEFAULT_GATEWAY = "http://localhost:8000/rpc"


def login(
    key_dir: Path | None = None,
    passphrase: Optional[str] = None,
    gateway_url: str = DEFAULT_GATEWAY,
) -> dict:
    """Ensure a key pair exists and upload the public key.

    Args:
        key_dir (Path | None): Directory containing the key pair.
        passphrase (Optional[str]): Optional private key passphrase.
        gateway_url (str): JSON-RPC endpoint for the gateway.

    Returns:
        dict: JSON response from the gateway.
    """
    drv = AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)
    pubkey = drv.pub_path.read_text()
    envelope = Request(
        id="0",
        method=KEYS_UPLOAD,
        params={"public_key": pubkey},
    ).model_dump()
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    return res.json()
