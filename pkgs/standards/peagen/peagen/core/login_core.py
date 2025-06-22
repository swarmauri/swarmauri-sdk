"""Helpers for user authentication."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx

from peagen import resolve_plugin_spec
from peagen._utils.config_loader import resolve_cfg

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
    cfg = resolve_cfg()
    plugin_name = cfg.get("secrets", {}).get("default_secret", "autogpg")
    Driver = resolve_plugin_spec("secrets", plugin_name)
    drv = Driver(key_dir=key_dir, passphrase=passphrase)
    pubkey = drv.pub_path.read_text()
    payload = {
        "jsonrpc": "2.0",
        "method": "Keys.upload",
        "params": {"public_key": pubkey},
    }
    res = httpx.post(gateway_url, json=payload, timeout=10.0)
    res.raise_for_status()
    return res.json()
