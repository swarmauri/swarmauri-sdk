"""Utility helpers for key pair management."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from peagen.transport import RPCRequest, RPCResponse

from peagen._utils.config_loader import load_peagen_toml
from peagen.plugins import PluginManager

DEFAULT_GATEWAY = "http://localhost:8000/rpc"


def _get_driver(key_dir: Path | None = None, passphrase: str | None = None) -> Any:
    """Instantiate the configured secrets driver."""
    cfg = load_peagen_toml()
    pm = PluginManager(cfg)
    try:
        drv = pm.get("secrets_drivers")
    except KeyError:
        from peagen.plugins.secret_drivers import AutoGpgDriver

        drv = AutoGpgDriver()

    # fallback to AutoGpgDriver if the driver lacks key management helpers
    if not hasattr(drv, "list_keys"):
        from peagen.plugins.secret_drivers import AutoGpgDriver

        drv = AutoGpgDriver()
    if key_dir is not None and hasattr(drv, "key_dir"):
        drv.key_dir = Path(key_dir)
        drv.priv_path = drv.key_dir / "private.asc"
        drv.pub_path = drv.key_dir / "public.asc"
    if passphrase is not None and hasattr(drv, "passphrase"):
        drv.passphrase = passphrase
    if hasattr(drv, "_ensure_keys"):
        drv._ensure_keys()
    return drv


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
    drv = _get_driver(key_dir=key_dir, passphrase=passphrase)
    return {"private": str(drv.priv_path), "public": str(drv.pub_path)}


def upload_public_key(
    key_dir: Path | None = None,
    gateway_url: str = DEFAULT_GATEWAY,
) -> dict:
    """Upload the local public key to the gateway."""
    drv = _get_driver(key_dir=key_dir)
    pubkey = drv.pub_path.read_text()
    envelope = RPCRequest(method="Keys.upload", params={"public_key": pubkey})
    res = httpx.post(gateway_url, json=envelope.model_dump(), timeout=10.0)
    res.raise_for_status()
    return RPCResponse.model_validate(res.json()).model_dump()


def remove_public_key(fingerprint: str, gateway_url: str = DEFAULT_GATEWAY) -> dict:
    """Remove a stored public key on the gateway."""
    envelope = RPCRequest(
        method="Keys.delete",
        params={"fingerprint": fingerprint},
    )
    res = httpx.post(gateway_url, json=envelope.model_dump(), timeout=10.0)
    res.raise_for_status()
    return RPCResponse.model_validate(res.json()).model_dump()


def fetch_server_keys(gateway_url: str = DEFAULT_GATEWAY) -> dict:
    """Fetch trusted keys from the gateway."""
    envelope = RPCRequest(method="Keys.fetch")
    res = httpx.post(gateway_url, json=envelope.model_dump(), timeout=10.0)
    res.raise_for_status()
    return RPCResponse.model_validate(res.json()).result or {}


def list_local_keys(key_dir: Path | None = None) -> Dict[str, str]:
    """Return a mapping of key fingerprints to public key paths."""

    drv = _get_driver(key_dir=key_dir)
    return drv.list_keys()


def export_public_key(
    fingerprint: str,
    *,
    key_dir: Path | None = None,
    fmt: str = "armor",
) -> str:
    """Return ``fingerprint`` key in the requested ``fmt``."""

    drv = _get_driver(key_dir=key_dir)
    return drv.export_public_key(fingerprint, fmt=fmt)


def add_key(
    public_key: Path,
    *,
    private_key: Path | None = None,
    key_dir: Path | None = None,
    name: str | None = None,
) -> dict:
    """Store ``public_key`` (and optional ``private_key``) under ``key_dir``."""

    drv = _get_driver(key_dir=key_dir)
    return drv.add_key(public_key, private_key=private_key, name=name)
