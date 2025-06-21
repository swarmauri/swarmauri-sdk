"""Login and bootstrap keys."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.secrets import AutoGpgDriver


login_app = typer.Typer(help="Authenticate and upload your public key.")


@login_app.command("login")
def login(
    ctx: typer.Context,
    passphrase: Optional[str] = typer.Option(None, "--passphrase", hide_input=True),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Ensure keys exist and upload the public key."""
    drv = AutoGpgDriver(key_dir=key_dir, passphrase=passphrase)
    pubkey = drv.pub_path.read_text()
    httpx.post(f"{gateway_url}/keys", json={"public_key": pubkey}, timeout=10.0)
    typer.echo("Logged in and uploaded public key")
