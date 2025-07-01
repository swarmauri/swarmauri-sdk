"""Manage encrypted secrets."""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from peagen.core import secrets_core
from peagen.transport.client import RPCResponseError, RPCTransportError

local_secrets_app = typer.Typer(help="Manage local secret store.")
remote_secrets_app = typer.Typer(help="Manage secrets via gateway.")


@local_secrets_app.command("add")
def add_local_secret(
    name: str, value: str, recipients: List[Path] = typer.Option([], "--recipient")
) -> None:
    """Encrypt and store a secret locally."""
    try:
        secrets_core.add_local_secret(name, value, recipients=recipients)
        typer.echo(f"Stored secret '{name}' locally.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@local_secrets_app.command("get")
def get_local_secret(name: str) -> None:
    """Decrypt and print a secret."""
    try:
        plain_text = secrets_core.get_local_secret(name)
        typer.echo(plain_text)
    except (KeyError, Exception) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@local_secrets_app.command("remove")
def remove_local_secret(name: str) -> None:
    """Delete a secret from local store."""
    try:
        secrets_core.remove_local_secret(name)
        typer.echo(f"Removed secret '{name}' from local store.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


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
    try:
        secrets_core.add_remote_secret(
            secret_id=secret_id,
            value=value,
            gateway_url=gateway_url,
            version=version,
            recipients=recipient,
            pool=pool,
        )
        typer.echo(f"Uploaded secret '{secret_id}' to gateway.")
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
    try:
        plain_text = secrets_core.get_remote_secret(
            secret_id=secret_id, gateway_url=gateway_url
        )
        typer.echo(plain_text)
    except (RPCTransportError, RPCResponseError, ValueError) as e:
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
    try:
        result = secrets_core.remove_remote_secret(
            secret_id=secret_id, gateway_url=gateway_url, version=version
        )
        if result.get("ok"):
            typer.echo(f"Removed secret '{secret_id}' from gateway.")
        else:
            typer.echo(f"Failed to remove secret '{secret_id}' from gateway.", err=True)
            raise typer.Exit(1)
    except (RPCTransportError, RPCResponseError) as e:
        typer.echo(f"Error: {e}", err=True)
