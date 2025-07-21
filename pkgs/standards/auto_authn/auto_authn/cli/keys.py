"""
auto_authn.cli.keys
=======================
CLI management for *long‑lived API keys* (7 – 90 days).

Assumptions
-----------
• `cli/__init__.py` exposes:
      BASE_URL        – root URL of the IdP (e.g. https://login.localhost)
      bearer_header() – returns {"Authorization": "Bearer <jwt>"}
      print_table(...)– pretty‑prints JSON list of dicts
• The IdP serves key routes at:
      /{tenant}/api-keys/
"""

from __future__ import annotations

import asyncio
from typing import List, Optional
from uuid import UUID

import httpx
import keyring
import typer
from rich.console import Console
from rich.table import Table

from . import BASE_URL, bearer_header

__all__ = ["app"]

console = Console()
app = typer.Typer(help="Manage long‑lived API keys")


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _url(tenant: str, suffix: str = "") -> str:
    return f"{BASE_URL}/{tenant}/api-keys{suffix}"


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=15.0, follow_redirects=True)


# --------------------------------------------------------------------------- #
# Commands                                                                    #
# --------------------------------------------------------------------------- #
@app.command("create", help="Create a new API key (visible once).")
def create(
    tenant: str = typer.Argument(..., help="Tenant slug"),
    ttl: int = typer.Option(30, "--ttl", "-t", min=7, max=90, help="Days"),
    scopes: List[str] = typer.Option(
        ["read"], "--scope", "-s", show_default=False, help="Repeat for multiple"
    ),
    label: Optional[str] = typer.Option(None, "--label", "-l", help="Friendly name"),
    save: bool = typer.Option(
        False, "--save", help="Persist in OS keyring under 'default' profile"
    ),
):
    async def _run() -> None:
        payload = {"ttl_days": ttl, "scopes": scopes, "label": label}
        async with await _client() as c:
            resp = await c.post(_url(tenant), json=payload, headers=bearer_header())
        if resp.is_error:
            console.print(f"[red]Error {resp.status_code}: {resp.text}[/]")
            raise typer.Exit(1)

        secret = resp.text.strip('"')  # JSONResponse returns quoted str
        console.print(f"[green]🔑 {secret}[/]  (store it securely)")

        if save:
            keyring.set_password("auto_authn-api-key", "default", secret)
            console.print("[cyan]✓ Saved to OS keyring (profile 'default')[/]")

    asyncio.run(_run())


@app.command("list", help="List API keys for the authenticated user.")
def list_keys(
    tenant: str = typer.Argument(..., help="Tenant slug"),
):
    async def _run() -> None:
        async with await _client() as c:
            resp = await c.get(_url(tenant), headers=bearer_header())
        if resp.is_error:
            console.print(f"[red]Error {resp.status_code}: {resp.text}[/]")
            raise typer.Exit(1)

        data = resp.json()
        tbl = Table("ID", "Prefix", "Scopes", "Expires", "Revoked")
        for k in data:
            tbl.add_row(
                k["id"],
                k["prefix"],
                ",".join(k["scopes"]),
                k["expires_at"].split("T")[0],
                str(k.get("revoked")),
            )
        console.print(tbl)

    asyncio.run(_run())


@app.command("revoke", help="Revoke an existing API key.")
def revoke(
    tenant: str = typer.Argument(..., help="Tenant slug"),
    key_id: UUID = typer.Argument(..., help="API‑key UUID"),
):
    async def _run() -> None:
        async with await _client() as c:
            resp = await c.delete(_url(tenant, f"/{key_id}"), headers=bearer_header())
        if resp.is_error:
            console.print(f"[red]Error {resp.status_code}: {resp.text}[/]")
            raise typer.Exit(1)

        console.print("[yellow]✓ Key revoked[/]")

    asyncio.run(_run())
