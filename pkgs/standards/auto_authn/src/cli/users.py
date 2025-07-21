"""
auth_authn_idp.cli.users
========================
User‑management commands for the Auth‑AuthN CLI.

Example
-------
    $ peagen users register acme alice alice@example.com --password S3cr3t
    $ peagen users disable  8b10e9fc‑…
    $ peagen users reset‑pwd 8b10e9fc‑… --new‑password N3wS3cr3t
"""

from __future__ import annotations

import asyncio
import secrets
import sys
from typing import Optional
from uuid import UUID

import httpx
import typer
from rich.console import Console
from rich.table import Table

from . import BASE_URL, bearer_header, keyring_save_token

__all__ = ["app"]

console = Console()
app = typer.Typer(add_help_option=False, no_args_is_help=True, rich_help_panel="Users")


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _build_url(tenant: str, path: str) -> str:
    return f"{BASE_URL}/{tenant}{path}"


# --------------------------------------------------------------------------- #
# Commands                                                                    #
# --------------------------------------------------------------------------- #
@app.command("register", help="Create a new user in the specified tenant.")
def register(
    tenant: str = typer.Argument(..., help="Tenant slug"),
    username: str = typer.Argument(..., help="User login name"),
    email: str = typer.Argument(..., help="User e‑mail"),
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="Initial password (prompted if omitted)",
        min=8,
        rich_help_panel="Credentials",
    ),
):
    if password is None:  # interactive prompt
        import getpass

        password = getpass.getpass("🔑  Password: ")
        if len(password) < 8:
            console.print("[red]Password must be at least 8 characters[/]")
            raise typer.Exit(1)

    payload = {
        "username": username,
        "email": email,
        "password": password,
    }

    async def _run() -> None:
        async with httpx.AsyncClient() as c:
            r = await c.post(_build_url(tenant, "/users"), json=payload)
            if r.status_code == 201:
                console.print("[green]✓ User created[/]")
            else:
                console.print(f"[red]Error {r.status_code}: {r.text}[/]")
                raise typer.Exit(r.status_code)

    asyncio.run(_run())


@app.command("list", help="List users in the tenant (requires admin token).")
def list_users(
    tenant: str = typer.Argument(..., help="Tenant slug"),
):
    async def _run() -> None:
        async with httpx.AsyncClient() as c:
            r = await c.get(
                _build_url(tenant, "/users"),
                headers=bearer_header(),
            )
            if r.is_error:
                console.print(f"[red]Error {r.status_code}: {r.text}[/]")
                raise typer.Exit(r.status_code)

            tbl = Table("ID", "Username", "E‑mail", "Active")
            for u in r.json():
                tbl.add_row(u["id"], u["username"], u["email"], str(u["is_active"]))
            console.print(tbl)

    asyncio.run(_run())


@app.command("disable", help="Soft‑disable a user (requires admin token).")
def disable(
    tenant: str = typer.Argument(..., help="Tenant slug"),
    user_id: UUID = typer.Argument(..., help="User UUID"),
):
    async def _run() -> None:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                _build_url(tenant, f"/users/{user_id}/disable"),
                headers=bearer_header(),
            )
            if r.is_error:
                console.print(f"[red]Error {r.status_code}: {r.text}[/]")
                raise typer.Exit(r.status_code)
            console.print("[yellow]User disabled[/]")

    asyncio.run(_run())


@app.command("reset-pwd", help="Admin resets a user's password.")
def reset_pwd(
    tenant: str = typer.Argument(..., help="Tenant slug"),
    user_id: UUID = typer.Argument(..., help="User UUID"),
    new_password: Optional[str] = typer.Option(
        None, "--new-password", "-n", help="Provide a new password (prompt if absent)"
    ),
):
    if new_password is None:
        import getpass

        new_password = getpass.getpass("🔑  New password: ")

    async def _run() -> None:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                _build_url(tenant, f"/users/{user_id}/reset-password"),
                headers=bearer_header(),
                json={"password": new_password},
            )
            if r.is_error:
                console.print(f"[red]Error {r.status_code}: {r.text}[/]")
                raise typer.Exit(r.status_code)
            console.print("[green]✓ Password reset[/]")

    asyncio.run(_run())
