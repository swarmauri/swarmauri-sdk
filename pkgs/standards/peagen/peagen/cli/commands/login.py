"""Login CLI command: create/verify key-pair locally and upload the public key."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from httpx import HTTPError

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.core.login_core import login as core_login
from peagen.defaults import DEFAULT_GATEWAY

# ---------------------------------------------------------------------------#
# Typer application
# ---------------------------------------------------------------------------#
login_app = typer.Typer(help="Authenticate and upload your public key.")


@login_app.command("login")
def login(
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
        help="Directory containing the GPG key-pair.",
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY,
        "--gateway-url",
        help="JSON-RPC endpoint for the Peagen gateway.",
    ),
) -> None:
    """Ensure keys exist locally and send the public key to the gateway."""
    # Normalise URL to …/rpc
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"

    # Fail fast if the key-pair is missing or unreadable.
    AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)

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

    typer.echo("Logged in and uploaded public key")
