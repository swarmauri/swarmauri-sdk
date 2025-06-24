"""Utility helpers for key pair management."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx

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


def read_public_key(key_dir: Path | None = None) -> str:
    """Return the local public key as a string."""
    drv = AutoGpgDriver(key_dir=key_dir)
    return drv.pub_path.read_text()


def export_public_key(format: str = "pgp", key_dir: Path | None = None) -> str:
    """Export the local public key in ``format``."""
    drv = AutoGpgDriver(key_dir=key_dir)
    if format == "pgp":
        return drv.pub_path.read_text()

    from pgpy.constants import PubKeyAlgorithm
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

    key = drv.public
    if format == "openssh":
        if key.key_algorithm in (
            PubKeyAlgorithm.RSAEncrypt,
            PubKeyAlgorithm.RSASign,
            PubKeyAlgorithm.RSAEncryptOrSign,
        ):
            material = key._key.keymaterial
            n = int(material.n)
            e = int(material.e)
            rsa_key = rsa.RSAPublicNumbers(e, n).public_key()
            return rsa_key.public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            ).decode()
        if key.key_algorithm is PubKeyAlgorithm.EdDSA:
            material = key._key.keymaterial
            pub_bytes = int(material.q).to_bytes(32, "big")
            ed_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            return ed_key.public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            ).decode()
        raise ValueError("Unsupported key algorithm for OpenSSH export")
    raise ValueError("Unknown format")


def import_private_key(
    private_key: str | Path,
    key_dir: Path | None = None,
    passphrase: Optional[str] = None,
) -> dict:
    """Add a private key to ``key_dir`` and return file paths."""
    from pgpy import PGPKey
    from pgpy.constants import HashAlgorithm, SymmetricKeyAlgorithm

    key_dir = Path(key_dir or Path.home() / ".peagen" / "keys")
    key_dir.mkdir(parents=True, exist_ok=True)
    priv_text = (
        Path(private_key).read_text()
        if isinstance(private_key, (str, Path))
        else private_key
    )
    priv = PGPKey()
    priv.parse(priv_text)
    if passphrase:
        priv.protect(passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)
    (key_dir / "private.asc").write_text(str(priv))
    (key_dir / "public.asc").write_text(str(priv.pubkey))
    return {
        "private": str(key_dir / "private.asc"),
        "public": str(key_dir / "public.asc"),
    }
