"""Manage encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.transport.client import (
    RPCResponseError,
    RPCTransportError,
    send_jsonrpc_request,
)
from peagen.transport.jsonrpc_schemas.secrets import (
    SECRETS_ADD,
    SECRETS_DELETE,
    SECRETS_GET,
    AddParams,
    DeleteParams,
    GetParams,
    GetResult,
)
from peagen.transport.jsonrpc_schemas.worker import WORKER_LIST, ListParams, ListResult

local_secrets_app = typer.Typer(help="Manage local secret store.")
remote_secrets_app = typer.Typer(help="Manage secrets via gateway.")
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    """Return public keys advertised by workers in ``pool``."""
    try:
        params = ListParams(pool=pool)
        result = send_jsonrpc_request(
            gateway_url, WORKER_LIST, params, expect=ListResult
        )
        workers = result.root if hasattr(result, "root") else result
    except (RPCTransportError, RPCResponseError):
        return []

    keys = []
    for w in workers:
        if isinstance(w, dict):
            advert = w.get("advertises") or {}
        else:
            advert = w.advertises or {}
        if isinstance(advert, str):  # gateway may return JSON string
            try:
                advert = json.loads(advert)
            except Exception:  # pragma: no cover - invalid JSON
                advert = {}
        key = advert.get("public_key") or advert.get("pubkey")
        if key:
            keys.append(key)
    return keys


def _load() -> dict:
    if STORE_FILE.exists():
        return json.loads(STORE_FILE.read_text())
    return {}


def _save(data: dict) -> None:
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORE_FILE.write_text(json.dumps(data, indent=2))


@local_secrets_app.command("add")
def add_secret(
    name: str, value: str, recipients: List[Path] = typer.Option([])
) -> None:
    """Encrypt and store a secret locally."""
    drv = AutoGpgDriver()
    pubkeys = [p.read_text() for p in recipients]
    cipher = drv.encrypt(value.encode(), pubkeys).decode()
    data = _load()
    data[name] = cipher
    _save(data)
    typer.echo(f"Stored secret {name}")


@local_secrets_app.command("get")
def get_secret(name: str) -> None:
    """Decrypt and print a secret."""
    drv = AutoGpgDriver()
    val = _load().get(name)
    if not val:
        raise typer.BadParameter("Unknown secret")
    plain = drv.decrypt(val.encode()).decode()
    typer.echo(plain)


@local_secrets_app.command("remove")
def remove_secret(name: str) -> None:
    """Delete a secret from local store."""
    data = _load()
    data.pop(name, None)
    _save(data)
    typer.echo(f"Removed secret {name}")


@remote_secrets_app.command("add")
def add_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    value: str,
    version: int = typer.Option(0, "--version"),
    recipient: List[Path] = typer.Option([], "--recipient"),
    pool: str = typer.Option("default", "--pool"),
) -> None:
    """Upload an encrypted secret to the gateway."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
    drv = AutoGpgDriver()
    pubs = [p.read_text() for p in recipient]
    pubs.append(drv.pub_path.read_text())
    pubs.extend(_pool_worker_pubs(pool, gateway_url))

    encrypted_value = drv.encrypt(value.encode(), list(set(pubs))).decode()

    params = AddParams(name=secret_id, cipher=encrypted_value, version=version)

    try:
        send_jsonrpc_request(gateway_url, SECRETS_ADD, params)
        typer.echo(f"Uploaded secret {secret_id}")
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("get")
def get_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Retrieve and decrypt a secret from the gateway."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
    drv = AutoGpgDriver()
    params = GetParams(name=secret_id)

    try:
        result = send_jsonrpc_request(
            gateway_url, SECRETS_GET, params, expect=GetResult
        )
        if not result.cipher:
            typer.echo("Secret not found or empty.", err=True)
            raise typer.Exit(1)
        plain_text = drv.decrypt(result.cipher.encode()).decode()
        typer.echo(plain_text)
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("remove")
def remove_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    version: int = typer.Option(None, "--version"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Delete a secret on the gateway."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"

    params = DeleteParams(name=secret_id, version=version)
    try:
        send_jsonrpc_request(gateway_url, SECRETS_DELETE, params)
        typer.echo(f"Removed secret {secret_id}")
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
