"""Manage encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import uuid
import httpx
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.transport import Request, Response
from peagen.transport.jsonrpc_schemas.worker import WORKER_LIST, ListParams, ListResult
from peagen.cli.task_helpers import build_task, submit_task


local_secrets_app = typer.Typer(help="Manage local secret store.")
remote_secrets_app = typer.Typer(help="Manage secrets via gateway.")
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    """Return public keys advertised by workers in ``pool``."""
    envelope = Request(
        id=str(uuid.uuid4()),
        method=WORKER_LIST,
        params=ListParams(pool=pool).model_dump(),
    )
    try:
        resp = httpx.post(
            gateway_url, json=envelope.model_dump(mode="json"), timeout=10.0
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            workers = data
        else:
            parsed = Response[ListResult].model_validate(data)
            if parsed.result is None:
                workers = []
            elif hasattr(parsed.result, "root"):
                workers = parsed.result.root
            else:
                workers = parsed.result
    except Exception:
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
def add_secret(name: str, value: str, recipients: List[Path] = typer.Option([])) -> None:
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
    pubs.extend(_pool_worker_pubs(pool, gateway_url))
    _ = drv.encrypt(value.encode(), pubs).decode()
    args = {
        "secret_id": secret_id,
        "value": value,
        "version": version,
        "recipient": [str(p) for p in recipient],
        "pool": pool,
        "gateway_url": gateway_url,
    }
    task = build_task("remote-add", args, pool=ctx.obj.get("pool", "default"))
    res = submit_task(gateway_url, task)
    if "error" in res:
        typer.echo(f"Error: {res['error']}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Uploaded secret {secret_id}")


@remote_secrets_app.command("get")
def get_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
    pool: str = typer.Option("default", "--pool"),
) -> None:
    """Retrieve and decrypt a secret from the gateway."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
    drv = AutoGpgDriver()
    args = {
        "secret_id": secret_id,
        "gateway_url": gateway_url,
        "pool": pool,
    }
    task = build_task("remote-get", args, pool=ctx.obj.get("pool", "default"))
    res = submit_task(gateway_url, task)
    if "error" in res:
        typer.echo(f"Error: {res['error']}", err=True)
        raise typer.Exit(1)
    cipher = res.get("result", {}).get("secret", "").encode()
    typer.echo(drv.decrypt(cipher).decode())


@remote_secrets_app.command("remove")
def remove_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    version: int = typer.Option(None, "--version"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
    pool: str = typer.Option("default", "--pool"),
) -> None:
    """Delete a secret on the gateway."""
    gateway_url = ctx.obj.get("gateway_url", "http://localhost:8000/rpc")
    gateway_url = gateway_url.rstrip("/")
    if not gateway_url.endswith("/rpc"):
        gateway_url += "/rpc"
    args = {
        "secret_id": secret_id,
        "version": version,
        "gateway_url": gateway_url,
        "pool": pool,
    }
    task = build_task("remote-remove", args, pool=ctx.obj.get("pool", "default"))
    res = submit_task(gateway_url, task)
    if "error" in res:
        typer.echo(f"Error: {res['error']}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Removed secret {secret_id}")
