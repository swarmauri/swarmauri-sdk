# cli_keys.py  – refactored
from __future__ import annotations

import json, uuid, typer, httpx
from pathlib import Path
from typing import Optional

from autoapi_client import AutoAPIClient          # ← new import
from autoapi.v2     import AutoAPI                   # ← get_schema lives here
from peagen.orm     import PublicKey      # ORM class for the resource
from peagen.core    import keys_core                 # unchanged

keys_app = typer.Typer(help="Manage local and remote public keys.")


# ---------------- RPC helpers ----------------------------------------- #
def _rpc(ctx: typer.Context) -> AutoAPIClient:
    """Return a ready-to-use JSON-RPC client."""
    return AutoAPIClient(ctx.obj["gateway_url"])


def _schema(tag: str):
    """Shorthand to fetch the correct Pydantic model once."""
    return AutoAPI.get_schema(PublicKey, tag)     # classmethod now


# ---------------- create (local-only) --------------------------------- #
@keys_app.command("create")
def create(
    passphrase: Optional[str] = typer.Option(
        None, "--passphrase", prompt=True, hide_input=True,
        confirmation_prompt=True
    ),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    try:
        keys_core.create_keypair(key_dir=key_dir, passphrase=passphrase)
        typer.echo(f"Created key pair in {key_dir}")
    except Exception as exc:
        typer.echo(f"Failed to create key pair: {exc}", err=True)
        raise typer.Exit(1)


# ---------------- upload ---------------------------------------------- #
@keys_app.command("upload")
def upload(
    ctx: typer.Context,
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    ctx.obj = {"gateway_url": gateway_url}        # make it available to _rpc
    try:
        # build request/response schemas dynamically
        SCreate = _schema("create")
        SRead   = _schema("read")

        payload = keys_core.export_public_key_as_dict(key_dir)  # your util
        params  = SCreate.model_validate(payload)

        with _rpc(ctx) as rpc:
            res = rpc.call("PublicKeys.create", params=params, out_schema=SRead)

        typer.echo(f"Uploaded public key. Fingerprint: {res.fingerprint}")

    except (httpx.HTTPError, ValueError) as exc:
        typer.echo(f"Failed to upload key: {exc}", err=True)
        raise typer.Exit(1)


# ---------------- remove ---------------------------------------------- #
@keys_app.command("remove")
def remove(
    ctx: typer.Context,
    fingerprint: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    ctx.obj = {"gateway_url": gateway_url}
    try:
        SDel   = _schema("delete")
        params = SDel(fingerprint=fingerprint)

        with _rpc(ctx) as rpc:
            res = rpc.call("PublicKeys.delete", params=params, out_schema=dict)

        if res.get("fingerprint"):
            typer.echo(f"Removed key {fingerprint} from gateway.")
        else:
            typer.echo(f"Key {fingerprint} was not found on gateway.", err=True)
            raise typer.Exit(1)

    except httpx.HTTPError as exc:
        typer.echo(f"Failed to remove key: {exc}", err=True)
        raise typer.Exit(1)


# ---------------- fetch-server ---------------------------------------- #
@keys_app.command("fetch-server")
def fetch_server(
    ctx: typer.Context,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    ctx.obj = {"gateway_url": gateway_url}
    try:
        SListIn  = _schema("list")
        SRead    = _schema("read")

        with _rpc(ctx) as rpc:
            res = rpc.call("PublicKeys.list", params=SListIn(), out_schema=list[SRead])  # type: ignore

        typer.echo(json.dumps([k.model_dump() for k in res], indent=2))

    except httpx.HTTPError as exc:
        typer.echo(f"Error fetching keys: {exc}", err=True)
        raise typer.Exit(1)


# ---------------- local list & show remain unchanged ------------------ #
@keys_app.command("list")
def list_keys(
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    data = keys_core.list_local_keys(key_dir)
    typer.echo(json.dumps(data, indent=2))


@keys_app.command("show")
def show(
    fingerprint: str,
    fmt: str = typer.Option("armor", "--format"),
    key_dir: Path = typer.Option(Path.home() / ".peagen" / "keys", "--key-dir"),
) -> None:
    out = keys_core.export_public_key(fingerprint, key_dir=key_dir, fmt=fmt)
    typer.echo(out)


# ---------------- add (local, no RPC) --------------------------------- #
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
    typer.echo(json.dumps(info))
