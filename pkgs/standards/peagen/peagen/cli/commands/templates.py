# peagen/commands/templates.py
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, Optional

import httpx
import typer

from peagen.handlers.templates_handler import templates_handler
from peagen.models import Task

# ──────────────────────────────────────
DEFAULT_GATEWAY = "http://localhost:8000/rpc"

local_template_sets_app = typer.Typer(
    help="Manage Peagen template-sets locally.",
    add_completion=False,
)
remote_template_sets_app = typer.Typer(
    help="Manage Peagen template-sets via JSON-RPC.",
    add_completion=False,
)


# ─── helpers ───────────────────────────
def _run_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    task = Task(id=str(uuid.uuid4()), pool="default", payload={"args": args})
    return asyncio.run(templates_handler(task))


def _submit_task(args: Dict[str, Any], gateway_url: str) -> str:
    """Submit a templates task via JSON-RPC."""
    task = Task(id=str(uuid.uuid4()), pool="default", payload={"args": args})
    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"pool": task.pool, "payload": task.payload},
    }
    resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return str(data.get("id", task.id))


# ─── list ──────────────────────────────
@local_template_sets_app.command("list", help="List all discovered template-sets.")
def run_list(
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="-v shows physical paths.",
    ),
):
    result = _run_handler({"operation": "list", "verbose": verbose})
    discovered = {e["name"]: e.get("paths", []) for e in result.get("sets", [])}
    if not discovered:
        typer.echo("⚠️  No template-sets found.")
        raise typer.Exit(code=1)

    typer.echo("\nAvailable template-sets:")
    for name, paths in sorted(discovered.items()):
        typer.echo(f" • {name}")
        if verbose:
            for p in paths:
                typer.echo(f"     ↳ {p}")
    typer.echo(f"\nTotal: {result['total']} set(s)")


@remote_template_sets_app.command("list", help="Submit a list task via gateway.")
def submit_list(
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="-v shows physical paths.",
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {"operation": "list", "verbose": verbose}
    try:
        task_id = _submit_task(args, gateway_url)
        typer.echo(f"Submitted list → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


# ─── show ──────────────────────────────
@local_template_sets_app.command("show", help="Show the contents of a template-set.")
def run_show(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="-v lists files, -vv lists full paths.",
    ),
):
    try:
        info = _run_handler({"operation": "show", "name": name, "verbose": verbose})
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}")
        raise typer.Exit(code=1)

    typer.echo(f"\nTemplate-set: {info['name']}")
    typer.echo(f"Location:    {info['location']}")

    if info.get("other_locations") and verbose:
        typer.echo("\n⚠️  Multiple copies found on search path:")
        for p in info["other_locations"]:
            typer.echo(f"   ↳ {p}")

    if verbose and info.get("files"):
        typer.echo("\nFiles:")
        for rel in info["files"]:
            typer.echo(f" • {rel}")


@remote_template_sets_app.command("show", help="Submit a show task via gateway.")
def submit_show(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="-v lists files, -vv lists full paths.",
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {"operation": "show", "name": name, "verbose": verbose}
    try:
        task_id = _submit_task(args, gateway_url)
        typer.echo(f"Submitted show → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


# ─── add ───────────────────────────────
@local_template_sets_app.command(
    "add",
    help=(
        "Install a template-set distribution from PyPI, a wheel/sdist, or a "
        "local directory."
    ),
)
def run_add(
    source: str = typer.Argument(
        ...,
        metavar="PKG|WHEEL|DIR",
        help=(
            "PyPI project slug, path to a wheel/tar.gz, or a directory that "
            "contains a template-set extension."
        ),
    ),
    from_bundle: Optional[str] = typer.Option(
        None, "--from-bundle", help="Install from bundled archive"
    ),
    editable: bool = typer.Option(
        False,
        "--editable",
        "-e",
        help="When SOURCE is a directory, install it in editable (-e) mode.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Re-install even if the distribution is already present.",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Show pip/uv output.",
    ),
):
    typer.echo("⏳  Installing via pip …")
    try:
        result = _run_handler(
            {
                "operation": "add",
                "source": source,
                "from_bundle": from_bundle,
                "editable": editable,
                "force": force,
                "verbose": verbose,
            }
        )
    except Exception as exc:  # noqa: BLE001
        typer.echo("❌  Installation failed.")
        if not verbose:
            typer.echo(str(exc))
        raise typer.Exit(code=1)

    new_sets = result.get("installed", [])
    if new_sets:
        typer.echo(
            f"✅  Installed template-set{'s' if len(new_sets) > 1 else ''}: "
            + ", ".join(new_sets)
        )
    else:
        typer.echo(
            "✅  Installation succeeded, but no *new* template-set entry-point "
            "was detected."
        )


@remote_template_sets_app.command("add", help="Submit an add task via gateway.")
def submit_add(
    source: str = typer.Argument(..., metavar="PKG|WHEEL|DIR"),
    from_bundle: Optional[str] = typer.Option(
        None, "--from-bundle", help="Install from bundled archive"
    ),
    editable: bool = typer.Option(False, "--editable", "-e"),
    force: bool = typer.Option(False, "--force"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {
        "operation": "add",
        "source": source,
        "from_bundle": from_bundle,
        "editable": editable,
        "force": force,
        "verbose": verbose,
    }
    try:
        task_id = _submit_task(args, gateway_url)
        typer.echo(f"Submitted add → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@local_template_sets_app.command(
    "remove", help="Uninstall the package that owns a template-set."
)
def run_remove(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show pip/uv output."),
):
    if not yes:
        if not typer.confirm(f"Uninstall template-set '{name}' ?"):
            typer.echo("Aborted.")
            raise typer.Exit()

    typer.echo("⏳  Uninstalling via pip …")
    try:
        result = _run_handler({"operation": "remove", "name": name, "verbose": verbose})
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}")
        raise typer.Exit(code=1)

    if result.get("removed"):
        typer.echo(f"✅  Removed template-set '{name}'.")
    else:
        typer.echo(
            "⚠️  Uninstall completed, but the template-set is still discoverable."
        )


@remote_template_sets_app.command("remove", help="Submit a remove task via gateway.")
def submit_remove(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt."),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    if not yes:
        if not typer.confirm(f"Uninstall template-set '{name}' ?"):
            typer.echo("Aborted.")
            raise typer.Exit()

    args = {"operation": "remove", "name": name, "verbose": verbose}
    try:
        task_id = _submit_task(args, gateway_url)
        typer.echo(f"Submitted remove → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
