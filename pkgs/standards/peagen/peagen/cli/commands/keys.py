"""CLI helpers for managing Peagen key pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from peagen.cli.rpc_utils import rpc_post
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.core import keys_core
from peagen.protocols import KEYS_UPLOAD, KEYS_DELETE, KEYS_FETCH
from peagen.protocols.methods.keys import (
    UploadParams,
    DeleteParams,
    FetchParams,
    UploadResult,
    DeleteResult,
    FetchResult,
)


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
    pubkey = drv.pub_path.read_text()
    params = UploadParams(public_key=pubkey).model_dump()
    rpc_post(
        gateway_url,
        KEYS_UPLOAD,
        params,
        timeout=10.0,
        result_model=UploadResult,
    )
    typer.echo("Uploaded public key")


@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Remove a public key from the gateway."""
    params = DeleteParams(fingerprint=fingerprint).model_dump()
    rpc_post(
        gateway_url,
        KEYS_DELETE,
        params,
        timeout=10.0,
        result_model=DeleteResult,
    )
    typer.echo(f"Removed key {fingerprint}")


@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Fetch trusted public keys from the gateway."""
    params = FetchParams().model_dump()
    res = rpc_post(
        gateway_url,
        KEYS_FETCH,
        params,
        timeout=10.0,
        result_model=FetchResult,
    )
    typer.echo(json.dumps(res.result.model_dump() if res.result else {}, indent=2))


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
