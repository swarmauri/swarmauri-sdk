"""CLI helpers for managing Peagen key pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver


keys_app = typer.Typer(help="Manage local and remote public keys.")


@keys_app.command("create")
def create(
    passphrase: Optional[str] = typer.Option(
        None, "--passphrase", prompt=False, hide_input=True
    ),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Generate a new key pair."""
    AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)
    typer.echo(f"Created key pair in {key_dir}")


@keys_app.command("upload")
def upload(
    ctx: typer.Context,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Upload the public key to the gateway."""
    drv = AutoGpgDriver(key_dir=key_dir)
    pubkey = drv.pub_path.read_text()
    envelope = {
        "jsonrpc": "2.0",
        "method": "Keys.upload",
        "params": {"public_key": pubkey},
    }
    httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo("Uploaded public key")


@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Remove a public key from the gateway."""
    envelope = {
        "jsonrpc": "2.0",
        "method": "Keys.delete",
        "params": {"fingerprint": fingerprint},
    }
    httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(f"Removed key {fingerprint}")


@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Fetch trusted public keys from the gateway."""
    envelope = {"jsonrpc": "2.0", "method": "Keys.fetch"}
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(json.dumps(res.json().get("result", {}), indent=2))


@keys_app.command("list")
def list_keys(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """List public keys stored on the gateway."""
    envelope = {"jsonrpc": "2.0", "method": "Keys.fetch"}
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(json.dumps(res.json().get("result", {}), indent=2))


@keys_app.command("show")
def show(
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Display the local public key."""
    drv = AutoGpgDriver(key_dir=key_dir)
    typer.echo(drv.pub_path.read_text())


@keys_app.command("export")
def export(
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    format: str = typer.Option("pgp", "--format", help="pgp or openssh"),
) -> None:
    """Export the public key in the requested format."""
    drv = AutoGpgDriver(key_dir=key_dir)
    if format == "pgp":
        typer.echo(drv.pub_path.read_text())
        return
    if format != "openssh":
        raise typer.BadParameter("Unknown format")

    from pgpy.constants import PubKeyAlgorithm
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

    key = drv.public
    if key.key_algorithm in (
        PubKeyAlgorithm.RSAEncrypt,
        PubKeyAlgorithm.RSASign,
        PubKeyAlgorithm.RSAEncryptOrSign,
    ):
        material = key._key.keymaterial
        n = int(material.n)
        e = int(material.e)
        rsa_key = rsa.RSAPublicNumbers(e, n).public_key()
        data = rsa_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        ).decode()
    elif key.key_algorithm is PubKeyAlgorithm.EdDSA:
        material = key._key.keymaterial
        pub_bytes = int(material.q).to_bytes(32, "big")
        ed_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        data = ed_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        ).decode()
    else:
        raise typer.BadParameter("Unsupported key algorithm for OpenSSH export")
    typer.echo(data)


@keys_app.command("add")
def add(
    private_key: Path,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    passphrase: Optional[str] = typer.Option(None, "--passphrase", hide_input=True),
) -> None:
    """Add an existing private key to the key directory."""
    from pgpy import PGPKey
    from pgpy.constants import HashAlgorithm, SymmetricKeyAlgorithm

    priv = PGPKey()
    priv.parse(private_key.read_text())
    if passphrase:
        priv.protect(passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)
    key_dir.mkdir(parents=True, exist_ok=True)
    (key_dir / "private.asc").write_text(str(priv))
    (key_dir / "public.asc").write_text(str(priv.pubkey))
    typer.echo(f"Added key in {key_dir}")
