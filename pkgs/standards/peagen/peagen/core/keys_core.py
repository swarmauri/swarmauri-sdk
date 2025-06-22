"""Utility helpers for key pair management."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx

from peagen.secrets import AutoGpgDriver

DEFAULT_GATEWAY = "http://localhost:8000/rpc"


def create_keypair(
    key_dir: Path | None = None, passphrase: Optional[str] = None
) -> dict:
    """Create a GPG key pair.

    Args:
        key_dir (Path | None): Destination directory for the keys.
        passphrase (Optional[str]): Optional passphrase for the private key.

    Returns:
        dict: Paths of the generated key files.
    """
    drv = AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)
    return {"private": str(drv.priv_path), "public": str(drv.pub_path)}


def upload_public_key(
    key_dir: Path | None = None,
    gateway_url: str = DEFAULT_GATEWAY,
) -> dict:
    """Upload the local public key to the gateway."""
    drv = AutoGpgDriver(key_dir=key_dir)
    pubkey = drv.pub_path.read_text()
    envelope = {
        "jsonrpc": "2.0",
        "method": "Keys.upload",
        "params": {"public_key": pubkey},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    return res.json()


def remove_public_key(fingerprint: str, gateway_url: str = DEFAULT_GATEWAY) -> dict:
    """Remove a stored public key on the gateway."""
    envelope = {
        "jsonrpc": "2.0",
        "method": "Keys.delete",
        "params": {"fingerprint": fingerprint},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    return res.json()


def fetch_server_keys(gateway_url: str = DEFAULT_GATEWAY) -> dict:
    """Fetch trusted keys from the gateway."""
    envelope = {"jsonrpc": "2.0", "method": "Keys.fetch"}
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    return res.json().get("result", {})
