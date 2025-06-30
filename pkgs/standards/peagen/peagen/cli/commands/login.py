"""Login and bootstrap keys."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.cli.task_helpers import build_task, submit_task


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
    drv.pub_path.read_text()
    try:
        args = {
            "key_dir": str(key_dir),
            "passphrase": passphrase,
            "gateway_url": gateway_url,
        }
        task = build_task("login", args, pool=ctx.obj.get("pool", "default"))
        reply = submit_task(gateway_url, task)
    except Exception as e:  # pragma: no cover - network errors
        typer.echo(f"HTTP error: {e}", err=True)
        raise typer.Exit(1)
    if "error" in reply:
        typer.echo(f"Failed to upload key: {reply['error']}", err=True)
        raise typer.Exit(1)
    typer.echo("Logged in and uploaded public key")
