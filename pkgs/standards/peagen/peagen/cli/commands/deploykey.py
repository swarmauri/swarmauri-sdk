"""Manage deploy key material locally and remotely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.core import keys_core
from peagen.defaults import DEFAULT_GATEWAY


# ---------------------------------------------------------------------------
# Typer applications
# ---------------------------------------------------------------------------
local_deploykey_app = typer.Typer(help="Manage local deploy keys.")
remote_deploykey_app = typer.Typer(help="Manage remote deploy keys.")


# ---------------------------------------------------------------------------
# Local commands
# ---------------------------------------------------------------------------
@local_deploykey_app.command("create")
def create(
    passphrase: Optional[str] = typer.Option(
        None,
        "--passphrase",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    ),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Generate a deploy key-pair locally."""
    try:
        keys_core.create_keypair(key_dir=key_dir, passphrase=passphrase)
        typer.echo(f"✅  Created key-pair in {key_dir}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


@local_deploykey_app.command("list")
def list_keys(
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """List locally available deploy keys."""
    typer.echo(json.dumps(keys_core.list_local_keys(key_dir), indent=2))


@local_deploykey_app.command("show")
def show(
    fingerprint: str,
    fmt: str = typer.Option("armor", "--format", help="armor | pem | ssh"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    """Display a local deploy key in the desired format."""
    typer.echo(keys_core.export_public_key(fingerprint, key_dir=key_dir, fmt=fmt))


@local_deploykey_app.command("add")
def add(
    public_key: Path,
    private_key: Optional[Path] = typer.Option(None, "--private"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    name: Optional[str] = typer.Option(None, "--name"),
) -> None:
    """Import an existing deploy key."""
    info = keys_core.add_key(
        public_key,
        private_key=private_key,
        key_dir=key_dir,
        name=name,
    )
    typer.echo(json.dumps(info, indent=2))


# ---------------------------------------------------------------------------
# Remote commands
# ---------------------------------------------------------------------------
@remote_deploykey_app.command("upload")
def upload(
    ctx: typer.Context,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    """Upload a deploy key to the gateway."""
    try:
        res = keys_core.upload_public_key(key_dir=key_dir, gateway_url=gateway_url)
        typer.echo(
            f"🚀  Uploaded key – fingerprint: {res.get('fingerprint', 'unknown')}"
        )
    except (httpx.HTTPError, ValueError) as exc:
        typer.echo(f"❌  Upload failed: {exc}", err=True)
        raise typer.Exit(1)


@remote_deploykey_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    """Remove a deploy key from the gateway."""
    try:
        keys_core.remove_public_key(fingerprint=fingerprint, gateway_url=gateway_url)
        typer.echo(f"🗑️  Removed key {fingerprint} from gateway.")
    except httpx.HTTPError as exc:
        typer.echo(f"❌  Removal failed: {exc}", err=True)
        raise typer.Exit(1)


@remote_deploykey_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    """Retrieve deploy keys from the gateway."""
    try:
        keys = keys_core.fetch_server_keys(gateway_url=gateway_url)
        typer.echo(json.dumps(keys, indent=2))
    except httpx.HTTPError as exc:
        typer.echo(f"❌  Fetch failed: {exc}", err=True)
        raise typer.Exit(1)
