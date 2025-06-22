"""Manage encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import httpx
import typer

from peagen.secrets import AutoGpgDriver


local_secrets_app = typer.Typer(help="Manage local secret store.")
remote_secrets_app = typer.Typer(help="Manage secrets via gateway.")
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


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
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Upload an encrypted secret to the gateway."""
    drv = AutoGpgDriver()
    cipher = drv.encrypt(value.encode(), []).decode()
    envelope = {
        "jsonrpc": "2.0",
        "method": "Secrets.add",
        "params": {"id": secret_id, "secret": cipher, "version": version},
    }
    httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(f"Uploaded secret {secret_id}")


@remote_secrets_app.command("get")
def remote_get(
    ctx: typer.Context,
    secret_id: str,
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Retrieve and decrypt a secret from the gateway."""
    drv = AutoGpgDriver()
    envelope = {
        "jsonrpc": "2.0",
        "method": "Secrets.get",
        "params": {"id": secret_id},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    cipher = res.json()["result"]["secret"].encode()
    typer.echo(drv.decrypt(cipher).decode())


@remote_secrets_app.command("remove")
def remote_remove(
    ctx: typer.Context,
    secret_id: str,
    version: int = typer.Option(None, "--version"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    """Delete a secret on the gateway."""
    envelope = {
        "jsonrpc": "2.0",
        "method": "Secrets.delete",
        "params": {"id": secret_id, "version": version},
    }
    httpx.post(gateway_url, json=envelope, timeout=10.0)
    typer.echo(f"Removed secret {secret_id}")
