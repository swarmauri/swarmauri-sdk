# peagen/cli/commands/secrets.py
"""
Manage encrypted *Secret* objects.

Local store:
  peagen secrets add/get/remove …

Gateway store:
  peagen secrets upload/remove/fetch-server …
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer
from autoapi_client import AutoAPIClient
from autoapi.v2 import AutoAPI
from peagen.orm import RepoSecret
from peagen.core import secrets_core

from peagen.defaults import DEFAULT_GATEWAY, DEFAULT_POOL_ID, DEFAULT_TENANT_ID

# ────────────────────────── apps ───────────────────────────────

local_secrets_app = typer.Typer(help="Manage secrets in the local .peagen store")
remote_secrets_app = typer.Typer(help="Manage secrets on the gateway via JSON-RPC")


# ─────────────────────── helper shortcuts ────────────────────────────
def _rpc(url: str) -> AutoAPIClient:
    return AutoAPIClient(url)


def _schema(tag: str):
    return AutoAPI.get_schema(RepoSecret, tag)


# ─────────────────────── LOCAL COMMANDS (unchanged) ───────────────────
@local_secrets_app.command("add")
def add_local_secret(
    name: str,
    value: str,
    recipients: List[Path] = typer.Option([], "--recipient"),
) -> None:
    try:
        secrets_core.add_local_secret(name, value, recipients=recipients)
        typer.echo(f"✅  stored secret '{name}' locally")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


@local_secrets_app.command("get")
def get_local_secret(name: str) -> None:
    try:
        typer.echo(secrets_core.get_local_secret(name))
    except Exception as exc:
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


@local_secrets_app.command("remove")
def remove_local_secret(name: str) -> None:
    try:
        secrets_core.remove_local_secret(name)
        typer.echo(f"🗑️  removed secret '{name}' from local store")
    except Exception as exc:
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


# ─────────────────────── REMOTE COMMANDS (RPC) ────────────────────────
@remote_secrets_app.command("add")
def add_remote_secret(  # noqa: PLR0913
    secret_id: str,
    value: str,
    version: int = typer.Option(0, "--version"),
    recipient: List[Path] = typer.Option([], "--recipient"),
    pool: str = typer.Option("default", "--pool"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SCreate = _schema("create")
    SRead = _schema("read")
    params = SCreate(
        secretId=secret_id,
        value=value,
        version=version,
        recipients=[str(p) for p in recipient],
        pool=pool,
    )
    try:
        with _rpc(gateway_url) as rpc:
            res = rpc.call("RepoSecrets.create", params=params, out_schema=SRead)
        typer.echo(f"🚀  uploaded secret '{res.secretId}' (v{res.version})")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("get")
def get_remote_secret(
    secret_id: str,
    version: int = typer.Option(0, "--version"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SRead = _schema("read")
    try:
        with _rpc(gateway_url) as rpc:
            secret = rpc.call(
                "RepoSecrets.read",
                params={"secretId": secret_id, "version": version},
                out_schema=SRead,
            )
        typer.echo(secret.plainValue)
    except Exception as exc:
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("remove")
def remove_remote_secret(
    secret_id: str,
    version: Optional[int] = typer.Option(None, "--version"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SDel = _schema("delete")
    try:
        params = SDel(secretId=secret_id, version=version)
        with _rpc(gateway_url) as rpc:
            rpc.call("RepoSecrets.delete", params=params, out_schema=dict)
        typer.echo(f"🗑️  removed secret '{secret_id}' from gateway")
    except Exception as exc:
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("fetch-server")
def fetch_server_secrets(
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
) -> None:
    SListIn = _schema("list")
    SRead = _schema("read")
    try:
        with _rpc(gateway_url) as rpc:
            lst = rpc.call("RepoSecrets.list", params=SListIn(), out_schema=list[SRead])  # type: ignore[arg-type]
        typer.echo(json.dumps([s.model_dump() for s in lst], indent=2))
    except Exception as exc:
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)
