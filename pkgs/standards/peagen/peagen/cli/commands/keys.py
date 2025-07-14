"""
peagen.cli.commands.keys
────────────────────────
Manage local and remote *DeployKey* objects only.
Does not pertain to *PublicKey* or *GPGKey* objects.


Local commands
--------------
• peagen keys create            – generate a key-pair
• peagen keys add               – import an existing key
• peagen keys list / show       – inspect local keys

Remote commands (JSON-RPC via gateway)
--------------------------------------
• peagen keys upload            – POST DeployKeys.create
• peagen keys remove <finger>   – POST DeployKeys.delete
• peagen keys fetch-server      – POST DeployKeys.list
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx
import typer
from autoapi_client import AutoAPIClient
from autoapi.v2 import AutoAPI
from peagen.orm import DeployKey  # ORM model → schema generator
from peagen.core import keys_core  # unchanged util helpers
from peagen.defaults import DEFAULT_GATEWAY

# ---------------------------------------------------------------------

keys_app = typer.Typer(help="Manage local and remote public-key material.")


# ─────────────────────────– helpers ──────────────────────────
def _rpc_client(url: str) -> AutoAPIClient:
    """Return an *AutoAPIClient* bound to *url*."""
    return AutoAPIClient(url)


def _schema(tag: str):
    """Return the Pydantic model for DeployKey + *tag* (create|read|delete|list)."""
    return AutoAPI.get_schema(DeployKey, tag)


# ─────────────────────── local key-pair create ────────────────────────
@keys_app.command("create")
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
    try:
        keys_core.create_keypair(key_dir=key_dir, passphrase=passphrase)
        typer.echo(f"✅  Created key-pair in {key_dir}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


# ─────────────────────── upload (DeployKeys.create) ───────────────────
@keys_app.command("upload")
def upload(
    ctx: typer.Context,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SCreate = _schema("create")
    SRead = _schema("read")

    try:
        payload = keys_core.export_public_key_as_dict(
            key_dir
        )  # {"fingerprint": …, "key": …}
        params = SCreate.model_validate(payload)

        with _rpc_client(gateway_url) as rpc:
            res = rpc.call("DeployKeys.create", params=params, out_schema=SRead)

        typer.echo(f"🚀  Uploaded key – fingerprint: {res.fingerprint}")

    except (httpx.HTTPError, ValueError) as exc:
        typer.echo(f"❌  Upload failed: {exc}", err=True)
        raise typer.Exit(1)


# ─────────────────────── remove (DeployKeys.delete) ───────────────────
@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SDel = _schema("delete")

    try:
        params = SDel(fingerprint=fingerprint)
        with _rpc_client(gateway_url) as rpc:
            rpc.call(
                "DeployKeys.delete", params=params
            )  # returns empty dict on success
        typer.echo(f"🗑️  Removed key {fingerprint} from gateway.")

    except httpx.HTTPError as exc:
        typer.echo(f"❌  Removal failed: {exc}", err=True)
        raise typer.Exit(1)


# ─────────────────────── fetch server keys (DeployKeys.list) ──────────
@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SListIn = _schema("list")
    SRead = _schema("read")

    try:
        with _rpc_client(gateway_url) as rpc:
            keys = rpc.call(
                "DeployKeys.list",
                params=SListIn(),  # empty input model
                out_schema=list[SRead],  # type: ignore[arg-type]
            )

        typer.echo(json.dumps([k.model_dump() for k in keys], indent=2))

    except httpx.HTTPError as exc:
        typer.echo(f"❌  Fetch failed: {exc}", err=True)
        raise typer.Exit(1)


# ─────────────────────── local key inspection cmds ────────────────────
@keys_app.command("list")
def list_keys(
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    typer.echo(json.dumps(keys_core.list_local_keys(key_dir), indent=2))


@keys_app.command("show")
def show(
    fingerprint: str,
    fmt: str = typer.Option("armor", "--format", help="armor | pem | ssh"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    typer.echo(keys_core.export_public_key(fingerprint, key_dir=key_dir, fmt=fmt))


# ─────────────────────── add existing public key ──────────────────────
@keys_app.command("add")
def add(
    public_key: Path,
    private_key: Optional[Path] = typer.Option(None, "--private"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    name: Optional[str] = typer.Option(None, "--name"),
) -> None:
    info = keys_core.add_key(
        public_key,
        private_key=private_key,
        key_dir=key_dir,
        name=name,
    )
    typer.echo(json.dumps(info, indent=2))
