"""Manage encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from peagen.cli.rpc_utils import httpx
import typer

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.protocols import SECRETS_ADD, SECRETS_GET, SECRETS_DELETE, Request


local_secrets_app = typer.Typer(help="Manage local secret store.")
remote_secrets_app = typer.Typer(help="Manage secrets via gateway.")
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    """Return public keys advertised by workers in ``pool``."""
    envelope = Request(id="0", method="Worker.list", params={"pool": pool})
    try:
        resp = httpx.post(gateway_url, json=envelope.model_dump(), timeout=10.0)
        resp.raise_for_status()
        res = resp.json()
    except Exception:
        return []
    workers = res.get("result", [])
    keys = []
    for w in workers:
        advert = w.get("advertises") or {}
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
def add(name: str, value: str, recipients: List[Path] = typer.Option([])) -> None:
    """Encrypt and store a secret locally."""
    drv = AutoGpgDriver()
    pubkeys = [p.read_text() for p in recipients]
    cipher = drv.encrypt(value.encode(), pubkeys).decode()
    data = _load()
    data[name] = cipher
    _save(data)
    typer.echo(f"Stored secret {name}")


@local_secrets_app.command("get")
def get(name: str) -> None:
    """Decrypt and print a secret."""
    drv = AutoGpgDriver()
    val = _load().get(name)
    if not val:
        raise typer.BadParameter("Unknown secret")
    plain = drv.decrypt(val.encode()).decode()
    typer.echo(plain)


@local_secrets_app.command("remove")
def remove(name: str) -> None:
    """Delete a secret from local store."""
    data = _load()
    data.pop(name, None)
    _save(data)
    typer.echo(f"Removed secret {name}")


@remote_secrets_app.command("add")
def remote_add(
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
    cipher = drv.encrypt(value.encode(), pubs).decode()
    envelope = {
        "jsonrpc": "2.0",
        "method": SECRETS_ADD,
        "params": {
            "name": secret_id,
            "cipher": cipher,
            "version": version,
            "tenant_id": pool,
        },
    }
    httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(f"Uploaded secret {secret_id}")


@remote_secrets_app.command("get")
def remote_get(
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
    envelope = {
        "jsonrpc": "2.0",
        "method": SECRETS_GET,
        "params": {"name": secret_id, "tenant_id": pool},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    data = res.json()
    cipher = data["result"]["secret"].encode()
    typer.echo(drv.decrypt(cipher).decode())


@remote_secrets_app.command("remove")
def remote_remove(
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
    envelope = {
        "jsonrpc": "2.0",
        "method": SECRETS_DELETE,
        "params": {"name": secret_id, "version": version, "tenant_id": pool},
    }
    httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(f"Removed secret {secret_id}")
