"""CLI helpers for managing Peagen key pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver


keys_app = typer.Typer(help="Manage local and remote public keys.")
remote_keys_app = typer.Typer(help="Manage remote public keys via gateway.")


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


@remote_keys_app.command("upload")
def remote_upload(
    ctx: typer.Context,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Upload the public key to the gateway using ctx settings."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
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


@remote_keys_app.command("remove")
def remote_remove(
    ctx: typer.Context,
    fingerprint: str,
) -> None:
    """Remove a public key from the gateway using ctx settings."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
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


@remote_keys_app.command("fetch-server")
def remote_fetch_server(
    ctx: typer.Context,
) -> None:
    """Fetch trusted public keys from the gateway using ctx settings."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
    envelope = {"jsonrpc": "2.0", "method": "Keys.fetch"}
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(json.dumps(res.json().get("result", {}), indent=2))
