"""Login and bootstrap keys."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from peagen.cli.rpc_utils import httpx
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.protocols import KEYS_UPLOAD, Request


login_app = typer.Typer(help="Authenticate and upload your public key.")


@login_app.command("login")
def login(
    ctx: typer.Context,
    passphrase: Optional[str] = typer.Option(
        None,
        "--passphrase",
        hide_input=True,
    ),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Ensure keys exist and upload the public key."""
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
    drv = AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)
    pubkey = drv.pub_path.read_text()
    envelope = Request(id="0", method=KEYS_UPLOAD, params={"public_key": pubkey})
    try:
        resp = httpx.post(gateway_url, json=envelope.model_dump(), timeout=10.0)
    except Exception as e:  # pragma: no cover - network errors
        typer.echo(f"HTTP error: {e}", err=True)
        raise typer.Exit(1)
    if resp.status_code != 200:
        typer.echo(f"Failed to upload key: {getattr(resp, 'text', '')}", err=True)
        raise typer.Exit(1)
    typer.echo("Logged in and uploaded public key")
