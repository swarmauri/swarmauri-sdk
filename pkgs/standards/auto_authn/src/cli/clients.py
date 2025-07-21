"""
auth_authn_idp.cli.clients
==========================
Manage **OIDC clients / relying‑parties** registered under a tenant.

Examples
--------
# Register Peagen for tenant 'acme'
auth-authn clients register acme \
    --redirect-uris https://app.peagen.io/auth/callback/acme \
    --response-types code

# List all clients for 'acme'
auth-authn clients list acme

# Rotate Peagen's client_secret
auth-authn clients rotate-secret acme peagen-acme

# Deactivate a client
auth-authn clients deactivate acme old-legacy-rp
"""

from __future__ import annotations

import asyncio
import logging
import secrets
import textwrap
from typing import List, Optional

import typer
from rich import box
from rich.table import Table
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..crypto import get_active_signing_key
from ..db import get_session
from ..models import Client, Tenant

log = logging.getLogger("auth_authn.cli.clients")
app = typer.Typer(
    help="OIDC client (relying‑party) lifecycle commands.",
    add_completion=False,
)

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


async def _tenant_obj(db: AsyncSession, slug: str) -> Tenant | None:
    q = select(Tenant).where(Tenant.slug == slug, Tenant.active)
    return (await db.scalars(q)).one_or_none()


async def _client_obj(db: AsyncSession, tenant_id: int, client_id: str) -> Client | None:
    q = select(Client).where(Client.tenant_id == tenant_id, Client.client_id == client_id)
    return (await db.scalars(q)).one_or_none()


def _random_secret() -> str:
    return secrets.token_urlsafe(40)


# --------------------------------------------------------------------------- #
# Commands                                                                    #
# --------------------------------------------------------------------------- #
@app.command("register")
def register(
    tenant: str = typer.Argument(..., help="Tenant slug under which to register."),
    client_id: str = typer.Option(
        None,
        "--client-id",
        "-c",
        help="Optional custom client_id (otherwise a random one is generated).",
    ),
    redirect_uris: List[str] = typer.Option(
        ...,
        "--redirect-uris",
        "-r",
        help="One or more redirect URIs (comma separated or repeated).",
    ),
    response_types: List[str] = typer.Option(
        ["code"], "--response-types", help="OIDC response types.",
    ),
    grant_types: List[str] = typer.Option(
        ["authorization_code", "refresh_token"], "--grant-types", help="OAuth2 grant types.",
    ),
    token_auth_method: str = typer.Option(
        "client_secret_basic",
        "--auth-method",
        help="token_endpoint_auth_method",
        case_sensitive=False,
    ),
    generate_secret: bool = typer.Option(
        True, "--generate-secret/--no-generate-secret", help="Create a client_secret."
    ),
):
    """
    Register a new RP / client for the given tenant.
    """
    async def _inner():
        async for db in get_session():
            ten = await _tenant_obj(db, tenant)
            if ten is None:
                typer.secho(f"Tenant '{tenant}' not found or inactive.", fg=typer.colors.RED)
                raise typer.Exit(1)

            if client_id is None:
                client_id_local = Client.generate_client_id()
            else:
                client_id_local = client_id

            if await _client_obj(db, ten.id, client_id_local):
                typer.secho("Client ID already exists", fg=typer.colors.RED)
                raise typer.Exit(1)

            secret_plain = _random_secret() if generate_secret else None

            client = Client(
                tenant_id=ten.id,
                client_id=client_id_local,
                redirect_uris=list(redirect_uris),
                response_types=list(response_types),
                grant_types=list(grant_types),
                token_endpoint_auth_method=token_auth_method,
            )
            if secret_plain:
                client.set_client_secret(secret_plain)
            db.add(client)
            await db.commit()

            typer.secho(
                f"✅  client '{client_id_local}' created under tenant '{tenant}'",
                fg=typer.colors.GREEN,
            )
            if secret_plain:
                typer.echo(
                    typer.style(
                        "\nStore this client_secret securely NOW (won’t be shown again):\n",
                        bold=True,
                    )
                    + typer.style(textwrap.indent(secret_plain, "   "), fg=typer.colors.YELLOW)
                )

    asyncio.run(_inner())


@app.command("list")
def list_clients(
    tenant: str = typer.Argument(..., help="Tenant slug to query."),
):
    """
    List clients for a tenant.
    """
    async def _inner():
        async for db in get_session():
            ten = await _tenant_obj(db, tenant)
            if ten is None:
                typer.secho(f"Tenant '{tenant}' not found.", fg=typer.colors.RED)
                raise typer.Exit(1)

            rows = (
                await db.scalars(
                    select(Client).where(Client.tenant_id == ten.id).order_by(Client.client_id)
                )
            ).all()

            if not rows:
                typer.echo("No clients registered.")
                return

            table = Table(box=box.SIMPLE)
            table.add_column("Client ID")
            table.add_column("Auth Method")
            table.add_column("Active")
            table.add_column("# Redirects")

            for c in rows:
                table.add_row(
                    c.client_id,
                    c.token_endpoint_auth_method,
                    "yes" if c.active else "no",
                    str(len(c.redirect_uris)),
                )
            from rich.console import Console

            Console().print(table)

    asyncio.run(_inner())


@app.command("rotate-secret")
def rotate_secret(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: str = typer.Argument(..., help="Client to rotate."),
):
    """
    Generates a new client_secret, hashes it, and returns the *plaintext* once.
    """
    async def _inner():
        async for db in get_session():
            ten = await _tenant_obj(db, tenant)
            if ten is None:
                typer.secho(f"Tenant '{tenant}' not found.", fg=typer.colors.RED)
                raise typer.Exit(1)

            client = await _client_obj(db, ten.id, client_id)
            if client is None:
                typer.secho("Client not found.", fg=typer.colors.RED)
                raise typer.Exit(1)

            new_secret = _random_secret()
            client.set_client_secret(new_secret)
            await db.commit()
            typer.secho(f"🔑 New secret set for '{client_id}'.", fg=typer.colors.GREEN)
            typer.echo(typer.style(new_secret, fg=typer.colors.YELLOW, bold=True))

    asyncio.run(_inner())


@app.command("deactivate")
def deactivate(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: str = typer.Argument(..., help="Client to deactivate."),
):
    """
    Soft‑disable a client (token endpoint rejects auth).
    """
    async def _inner(active: bool):
        async for db in get_session():
            ten = await _tenant_obj(db, tenant)
            if ten is None:
                typer.secho(f"No tenant '{tenant}'.", fg=typer.colors.RED)
                raise typer.Exit(1)

            upd = (
                update(Client)
                .where(Client.tenant_id == ten.id, Client.client_id == client_id)
                .values(active=active)
                .returning(Client.client_id)
            )
            res = (await db.execute(upd)).scalar_one_or_none()
            await db.commit()

            if res is None:
                typer.secho("Client not found.", fg=typer.colors.RED)
                raise typer.Exit(1)
            state = "reactivated" if active else "deactivated"
            typer.secho(f"✅ Client '{client_id}' {state}", fg=typer.colors.GREEN)

    asyncio.run(_inner(False))


@app.command("activate")
def activate(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: str = typer.Argument(..., help="Client to activate."),
):
    """
    Reactivate a previously disabled client.
    """
    async def _inner():
        await deactivate.callback(tenant, client_id, _standalone_mode=False)

    asyncio.run(_inner())
