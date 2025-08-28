"""Manage public key material locally and remotely."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from httpx import HTTPError

from peagen.core import keys_core
from peagen.core.publickey_core import login as core_login
from peagen.defaults import DEFAULT_GATEWAY


# ---------------------------------------------------------------------------
# Typer applications
# ---------------------------------------------------------------------------
local_publickey_app = typer.Typer(help="Manage local public key material.")
remote_publickey_app = typer.Typer(help="Manage remote public key material.")


# ---------------------------------------------------------------------------
# Local commands
# ---------------------------------------------------------------------------
@local_publickey_app.command("create")
def create(
    passphrase: Optional[str] = typer.Option(
        None,
        "--passphrase",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    ),
    key_dir: Path = typer.Option(
        Path.home() / ".peagen" / "keys",
        "--key-dir",
        help="Directory containing the key-pair.",
    ),
) -> None:
    """Ensure a key-pair exists locally."""
    try:
        keys_core.create_keypair(key_dir, passphrase)
        typer.echo(f"✅  Created key-pair in {key_dir}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# Remote commands
# ---------------------------------------------------------------------------
@remote_publickey_app.command("upload")
def upload(
    ctx: typer.Context,
    passphrase: Optional[str] = typer.Option(
        None,
        "--passphrase",
        hide_input=True,
        help="Passphrase for the private key, if any.",
    ),
    key_dir: Path = typer.Option(
        Path.home() / ".peagen" / "keys",
        "--key-dir",
        help="Directory containing the key-pair.",
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY,
        "--gateway-url",
        help="JSON-RPC endpoint for the Peagen gateway.",
    ),
) -> None:
    """Upload the public key to the gateway."""
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"

    try:
        reply = core_login(
            key_dir=key_dir,
            passphrase=passphrase,
            gateway_url=gateway_url,
        )
    except HTTPError as exc:  # pragma: no cover – network / HTTP errors
        typer.echo(f"HTTP error: {exc}", err=True)
        raise typer.Exit(1)

    if "error" in reply:  # JSON-RPC error object
        typer.echo(f"Failed to upload key: {reply['error']}", err=True)
        raise typer.Exit(1)

    typer.echo("Uploaded public key")
