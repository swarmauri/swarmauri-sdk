"""CLI helpers for managing Peagen key pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.secrets import AutoGpgDriver


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
    payload = {"public_key": pubkey}
    httpx.post(f"{gateway_url}/keys", json=payload, timeout=10.0)
    typer.echo("Uploaded public key")


@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Remove a public key from the gateway."""
    httpx.delete(f"{gateway_url}/keys/{fingerprint}", timeout=10.0)
    typer.echo(f"Removed key {fingerprint}")


@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Fetch trusted public keys from the gateway."""
    res = httpx.get(f"{gateway_url}/keys", timeout=10.0)
    typer.echo(json.dumps(res.json(), indent=2))
