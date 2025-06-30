"""CLI helpers for managing Peagen key pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from peagen.core import keys_core
from peagen.transport.client import RPCResponseError, RPCTransportError

keys_app = typer.Typer(help="Manage local and remote public keys.")


@keys_app.command("create")
def create(
    passphrase: Optional[str] = typer.Option(
        None, "--passphrase", prompt=True, hide_input=True, confirmation_prompt=True
    ),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Generate a new key pair."""
    try:
        keys_core.create_keypair(key_dir=key_dir, passphrase=passphrase)
        typer.echo(f"Created key pair in {key_dir}")
    except Exception as e:
        typer.echo(f"Failed to create key pair: {e}", err=True)
        raise typer.Exit(1)


@keys_app.command("upload")
def upload(
    ctx: typer.Context,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Upload the public key to the gateway."""
    try:
        result = keys_core.upload_public_key(key_dir=key_dir, gateway_url=gateway_url)
        fingerprint = result.get("fingerprint")
        if fingerprint:
            typer.echo(f"Uploaded public key. Fingerprint: {fingerprint}")
        else:
            typer.echo("Failed to upload key: No fingerprint returned.", err=True)
            raise typer.Exit(1)
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Failed to upload key: {e}", err=True)
        raise typer.Exit(1)


@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Remove a public key from the gateway."""
    try:
        result = keys_core.remove_public_key(
            fingerprint=fingerprint, gateway_url=gateway_url
        )
        if result.get("ok"):
            typer.echo(f"Removed key {fingerprint} from gateway.")
        else:
            typer.echo(f"Failed to remove key {fingerprint} on gateway.", err=True)
            raise typer.Exit(1)
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Failed to remove key: {e}", err=True)
        raise typer.Exit(1)


@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Fetch trusted public keys from the gateway."""
    try:
        result = keys_core.fetch_server_keys(gateway_url=gateway_url)
        typer.echo(json.dumps(result, indent=2))
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@keys_app.command("list")
def list_keys(
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """List fingerprints of locally stored keys."""
    data = keys_core.list_local_keys(key_dir)
    typer.echo(json.dumps(data, indent=2))


@keys_app.command("show")
def show(
    fingerprint: str,
    fmt: str = typer.Option("armor", "--format"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Output a public key in the requested format."""
    out = keys_core.export_public_key(fingerprint, key_dir=key_dir, fmt=fmt)
    typer.echo(out)


@keys_app.command("add")
def add(
    public_key: Path,
    private_key: Optional[Path] = typer.Option(None, "--private"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    name: Optional[str] = typer.Option(None, "--name"),
) -> None:
    """Add an existing key pair to the key store."""
    info = keys_core.add_key(
        public_key,
        private_key=private_key,
        key_dir=key_dir,
        name=name,
    )
    typer.echo(json.dumps(info))
