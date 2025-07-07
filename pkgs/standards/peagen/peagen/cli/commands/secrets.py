"""Manage encrypted secrets."""
from __future__ import annotations

import json, uuid, httpx, typer
from pathlib import Path
from typing import List, Optional

from peagen.core      import secrets_core
from autoapi_client   import AutoAPIClient                   # ← new
from autoapi.v2       import AutoAPI                       # ← for get_schema
from peagen.orm       import Secret               # ← ORM resource

# CLI root groups
local_secrets_app  = typer.Typer(help="Manage local secret store.")
remote_secrets_app = typer.Typer(help="Manage secrets via gateway.")


# ───────────────────────── helper shortcuts ──────────────────────────
def _rpc(ctx: typer.Context) -> AutoAPIClient:
    """Return a ready JSON-RPC client bound to ctx.obj['gateway_url']."""
    return AutoAPIClient(ctx.obj["gateway_url"])

def _schema(tag: str):
    """Fetch the exact Pydantic model AutoAPI generated for <Secret, tag>."""
    return AutoAPI.get_schema(Secret, tag)


# ───────────────────────── local commands (unchanged) ────────────────
@local_secrets_app.command("add")
def add_local_secret(
    name: str,
    value: str,
    recipients: List[Path] = typer.Option([], "--recipient"),
) -> None:
    try:
        secrets_core.add_local_secret(name, value, recipients=recipients)
        typer.echo(f"Stored secret '{name}' locally.")
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@local_secrets_app.command("get")
def get_local_secret(name: str) -> None:
    try:
        typer.echo(secrets_core.get_local_secret(name))
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@local_secrets_app.command("remove")
def remove_local_secret(name: str) -> None:
    try:
        secrets_core.remove_local_secret(name)
        typer.echo(f"Removed secret '{name}' from local store.")
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


# ───────────────────────── remote commands (RPC) ─────────────────────
@remote_secrets_app.command("add")
def add_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    value: str,
    version: int = typer.Option(0, "--version"),
    recipient: List[Path] = typer.Option([], "--recipient"),
    pool: str = typer.Option("default", "--pool"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    ctx.obj = {"gateway_url": gateway_url}   # make URL visible to helpers

    SCreate = _schema("create")
    SRead   = _schema("read")

    params  = SCreate(secretId=secret_id,
                      value=value,
                      version=version,
                      recipients=[str(p) for p in recipient],
                      pool=pool)

    try:
        with _rpc(ctx) as rpc:
            res = rpc.call("Secrets.create", params=params, out_schema=SRead)
        typer.echo(f"Uploaded secret '{res.secretId}' to gateway.")
    except (httpx.HTTPError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("get")
def get_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    version: int = typer.Option(0, "--version"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    ctx.obj = {"gateway_url": gateway_url}

    SRead = _schema("read")

    try:
        with _rpc(ctx) as rpc:
            res = rpc.call("Secrets.read",
                           params={"secretId": secret_id, "version": version},
                           out_schema=SRead)
        typer.echo(res.plainValue)                 # assuming field name
    except (httpx.HTTPError, RuntimeError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@remote_secrets_app.command("remove")
def remove_remote_secret(
    ctx: typer.Context,
    secret_id: str,
    version: int = typer.Option(None, "--version"),
    gateway_url: str = typer.Option("http://localhost:8000/rpc", "--gateway-url"),
) -> None:
    ctx.obj = {"gateway_url": gateway_url}

    SDel = _schema("delete")

    try:
        params = SDel(secretId=secret_id, version=version)
        with _rpc(ctx) as rpc:
            res: dict = rpc.call("Secrets.delete", params=params, out_schema=dict)
        if res.get("ok"):
            typer.echo(f"Removed secret '{secret_id}' from gateway.")
        else:
            typer.echo(f"Failed to remove secret '{secret_id}'.", err=True)
            raise typer.Exit(1)
    except (httpx.HTTPError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
