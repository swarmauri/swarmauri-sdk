"""Login and bootstrap keys."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver


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
    payload = {
        "jsonrpc": "2.0",
        "method": "Keys.upload",
        "params": {"public_key": pubkey},
    }
    headers = ctx.obj.get("headers") or None
    kwargs = {"json": payload, "timeout": 10.0}
    if headers:
        kwargs["headers"] = headers
    try:
        res = httpx.post(gateway_url, **kwargs)
    except httpx.RequestError as e:  # pragma: no cover - network errors
        typer.echo(f"HTTP error: {e}", err=True)
        raise typer.Exit(1)
    if res.status_code == 404:
        typer.echo(
            "Gateway endpoint not found. Did you append '/rpc'?",
            err=True,
        )
        raise typer.Exit(1)
    if res.status_code >= 400:
        typer.echo(
            f"Failed to upload key: {res.status_code} {res.text}",
            err=True,
        )
        raise typer.Exit(1)
    typer.echo("Logged in and uploaded public key")
