"""
auto_authn.cli.clients
==========================
Manage **OIDC clients / relying‑parties** under a tenant.

Typical usage
-------------
# Register a SPA
auto-authn clients register acme \
  --redirect-uris https://app.example.com/callback \
  --response-types code \
  --grant-types authorization_code,refresh_token

# List all clients
auto-authn clients list acme

# Rotate client_secret
auto-authn clients rotate-secret acme my-spa

# Deactivate
auto-authn clients deactivate acme old-legacy-rp
"""

from __future__ import annotations

import asyncio
import secrets
from typing import List, Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

from . import BASE_URL, bearer_header

console = Console()
app = typer.Typer(
    help="OIDC client / RP lifecycle commands.",
    add_completion=False,
)


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _url(tenant: str, suffix: str = "") -> str:
    return f"{BASE_URL}/{tenant}/clients{suffix}"


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=15.0, follow_redirects=True)


def _random_secret() -> str:
    return secrets.token_urlsafe(40)


# --------------------------------------------------------------------------- #
# Commands – CREATE / LIST                                                    #
# --------------------------------------------------------------------------- #
@app.command("register")
def register(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: Optional[str] = typer.Option(
        None, "--client-id", "-c", help="Custom client_id (optional)."
    ),
    redirect_uris: List[str] = typer.Option(
        ..., "--redirect-uris", "-r", help="Repeat for multiple URIs."
    ),
    response_types: List[str] = typer.Option(
        ["code"], "--response-types", "-R", help="OIDC response types."
    ),
    grant_types: List[str] = typer.Option(
        ["authorization_code", "refresh_token"],
        "--grant-types",
        "-g",
        help="OAuth2 grant types.",
    ),
    token_auth_method: str = typer.Option(
        "client_secret_basic",
        "--auth-method",
        "-m",
        help="token_endpoint_auth_method",
    ),
    no_secret: bool = typer.Option(
        False,
        "--no-secret",
        help="Don't generate client_secret (public client / SPA).",
    ),
):
    """
    Register a new relying‑party for *tenant*.
    """
    payload = {
        "client_id": client_id,
        "redirect_uris": redirect_uris,
        "response_types": response_types,
        "grant_types": grant_types,
        "token_endpoint_auth_method": token_auth_method,
        "generate_secret": not no_secret,
    }

    async def _run() -> None:
        async with await _client() as c:
            r = await c.post(_url(tenant), json=payload, headers=bearer_header())
        if r.is_error:
            console.print(f"[red]Error {r.status_code}: {r.text}[/]")
            raise typer.Exit(1)

        data = r.json()
        console.print(
            f"[green]✓ Client '{data['client_id']}' created under tenant '{tenant}'[/]"
        )
        if data.get("client_secret"):
            console.print(
                "[yellow]Store this client_secret securely (won't be shown again):[/]"
            )
            console.print(f"[bold]{data['client_secret']}[/]")

    asyncio.run(_run())


@app.command("list", help="List clients for a tenant.")
def list_clients(
    tenant: str = typer.Argument(..., help="Tenant slug."),
):
    async def _run() -> None:
        async with await _client() as c:
            r = await c.get(_url(tenant), headers=bearer_header())
        if r.is_error:
            console.print(f"[red]Error {r.status_code}: {r.text}[/]")
            raise typer.Exit(1)

        rows = r.json()
        if not rows:
            console.print("No clients registered.")
            return

        tbl = Table("Client ID", "Auth Method", "Active", "# Redirects")
        for c in rows:
            tbl.add_row(
                c["client_id"],
                c["token_endpoint_auth_method"],
                "yes" if c["active"] else "no",
                str(len(c["redirect_uris"])),
            )
        console.print(tbl)

    asyncio.run(_run())


# --------------------------------------------------------------------------- #
# Commands – SECRET ROTATION / STATE CHANGE                                   #
# --------------------------------------------------------------------------- #
async def _post_no_body(url: str):
    async with await _client() as c:
        r = await c.post(url, headers=bearer_header())
    if r.is_error:
        console.print(f"[red]Error {r.status_code}: {r.text}[/]")
        raise typer.Exit(1)
    return r


@app.command("rotate-secret", help="Generate a new client_secret.")
def rotate_secret(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: str = typer.Argument(..., help="Client ID."),
):
    async def _run() -> None:
        r = await _post_no_body(_url(tenant, f"/{client_id}/rotate-secret"))
        secret = r.json().get("client_secret")
        console.print("[green]✓ Secret rotated.[/]")
        console.print(
            "[yellow]Store the new secret now (won't be shown again):[/]\n"
            f"[bold]{secret}[/]"
        )

    asyncio.run(_run())


@app.command("deactivate", help="Soft‑disable a client.")
def deactivate(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: str = typer.Argument(..., help="Client ID."),
):
    asyncio.run(_post_no_body(_url(tenant, f"/{client_id}/deactivate")))
    console.print(f"[yellow]Client '{client_id}' deactivated.[/]")


@app.command("activate", help="Re‑enable a previously disabled client.")
def activate(
    tenant: str = typer.Argument(..., help="Tenant slug."),
    client_id: str = typer.Argument(..., help="Client ID."),
):
    asyncio.run(_post_no_body(_url(tenant, f"/{client_id}/activate")))
    console.print(f"[green]Client '{client_id}' activated.[/]")
