"""Utility helpers for key pair management."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import subprocess
import tempfile

import httpx
import pgpy

from peagen.plugins.secret_drivers import AutoGpgDriver

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


def list_local_keys(key_root: Path | None = None) -> Dict[str, str]:
    """Return a mapping of key fingerprints to public key paths."""

    root = Path(key_root or Path.home() / ".peagen" / "keys")
    keys: Dict[str, str] = {}

    def _add(pub: Path) -> None:
        if not pub.exists():
            return
        key = pgpy.PGPKey()
        key.parse(pub.read_text())
        keys[key.fingerprint] = str(pub)

    if (root / "public.asc").exists():
        _add(root / "public.asc")
    else:
        for sub in root.iterdir():
            if not sub.is_dir():
                continue
            _add(sub / "public.asc")

    return keys


def export_public_key(
    fingerprint: str,
    *,
    key_root: Path | None = None,
    fmt: str = "armor",
) -> str:
    """Return ``fingerprint`` key in the requested ``fmt``."""

    keys = list_local_keys(key_root)
    pub_path_str = keys.get(fingerprint)
    if not pub_path_str:
        raise ValueError(f"unknown key: {fingerprint}")

    pub_path = Path(pub_path_str)
    if fmt == "openssh":
        with tempfile.TemporaryDirectory() as gpg_home:
            subprocess.run(
                [
                    "gpg",
                    "--homedir",
                    gpg_home,
                    "--import",
                    str(pub_path),
                ],
                check=True,
                capture_output=True,
            )
            out = subprocess.run(
                [
                    "gpg",
                    "--homedir",
                    gpg_home,
                    "--export-ssh-key",
                    fingerprint,
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        return out

    return pub_path.read_text()


def add_key(
    public_key: Path,
    *,
    private_key: Path | None = None,
    key_root: Path | None = None,
    name: str | None = None,
) -> dict:
    """Store ``public_key`` (and optional ``private_key``) under ``key_root``."""

    text = Path(public_key).read_text()
    key = pgpy.PGPKey()
    key.parse(text)
    fingerprint = key.fingerprint

    dest_root = Path(key_root or Path.home() / ".peagen" / "keys")
    if (dest_root / "public.asc").exists() and not name:
        dest = dest_root
    else:
        dest = dest_root / (name or fingerprint)
        dest.mkdir(parents=True, exist_ok=True)

    (dest / "public.asc").write_text(text)
    if private_key is not None:
        (dest / "private.asc").write_text(Path(private_key).read_text())

    return {"fingerprint": fingerprint, "path": str(dest)}
