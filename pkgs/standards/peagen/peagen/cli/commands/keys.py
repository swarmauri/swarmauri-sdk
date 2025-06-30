"""CLI helpers for managing Peagen key pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.core import keys_core
from peagen.cli.task_helpers import build_task, submit_task


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
    drv.pub_path.read_text()
    args = {"key_dir": str(key_dir), "gateway_url": gateway_url}
    pool = ctx.obj.get("pool", "default") if ctx is not None and ctx.obj else "default"
    task = build_task("upload", args, pool=pool)
    reply = submit_task(gateway_url, task)
    if "error" in reply:
        typer.echo(f"Failed to upload key: {reply['error']}", err=True)
        raise typer.Exit(1)
    typer.echo("Uploaded public key")


@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Remove a public key from the gateway."""
    args = {
        "fingerprint": fingerprint,
        "gateway_url": gateway_url,
    }
    pool = ctx.obj.get("pool", "default") if ctx is not None and ctx.obj else "default"
    task = build_task("remove", args, pool=pool)
    reply = submit_task(gateway_url, task)
    if "error" in reply:
        typer.echo(f"Failed to remove key: {reply['error']}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Removed key {fingerprint}")


@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Fetch trusted public keys from the gateway."""
    args = {"gateway_url": gateway_url}
    pool = ctx.obj.get("pool", "default") if ctx is not None and ctx.obj else "default"
    task = build_task("fetch-server", args, pool=pool)
    res = submit_task(gateway_url, task)
    if "error" in res:
        typer.echo(f"Error: {res['error']}", err=True)
        raise typer.Exit(1)
    typer.echo(json.dumps(res.get("result", {}), indent=2))


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
