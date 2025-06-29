# peagen/commands/templates.py
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from peagen.cli.rpc_utils import rpc_post
import typer

from uuid import uuid4

from peagen.handlers.templates_handler import templates_handler
from peagen.transport.jsonrpc_schemas import TASK_SUBMIT
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult

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
    submit = SubmitParams(
        id=str(uuid4()),
        pool="default",
        payload={"action": "templates", "args": args},
    )
    return asyncio.run(templates_handler(submit))


def _submit_task(args: Dict[str, Any], gateway_url: str) -> str:
    """Submit a templates task via JSON-RPC."""
    submit = SubmitParams(
        id=str(uuid4()),
        pool="default",
        payload={"action": "templates", "args": args},
    )
    reply = rpc_post(
        gateway_url,
        TASK_SUBMIT,
        submit.model_dump(),
        timeout=10.0,
        result_model=SubmitResult,
    )
    if reply.error:
        raise RuntimeError(reply.error.message)
    return str(reply.result.taskId if reply.result else submit.id)


# ─── list ──────────────────────────────
@local_template_sets_app.command("list", help="List all discovered template-sets.")
def run_list():
    """List template-set packages found on the search path."""
    result = _run_handler({"operation": "list"})
    discovered = {e["name"]: e.get("paths", []) for e in result.get("sets", [])}
    if not discovered:
        typer.echo("⚠️  No template-sets found.")
        raise typer.Exit(code=1)

    typer.echo("\nAvailable template-sets:")
    for name in sorted(discovered.keys()):
        typer.echo(f" • {name}")
    typer.echo(f"\nTotal: {result['total']} set(s)")


@remote_template_sets_app.command("list", help="Submit a list task via gateway.")
def submit_list(
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Enqueue a template-set listing task on the gateway."""
    args = {"operation": "list", "repo": repo, "ref": ref}
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
):
    """Show metadata and files for a template-set."""
    try:
        info = _run_handler({"operation": "show", "name": name})
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}")
        raise typer.Exit(code=1)

    typer.echo(f"\nTemplate-set: {info['name']}")
    typer.echo(f"Location:    {info['location']}")

    if info.get("other_locations"):
        typer.echo("\n⚠️  Multiple copies found on search path:")
        for p in info["other_locations"]:
            typer.echo(f"   ↳ {p}")

    if info.get("files"):
        typer.echo("\nFiles:")
        for rel in info["files"]:
            typer.echo(f" • {rel}")


@remote_template_sets_app.command("show", help="Submit a show task via gateway.")
def submit_show(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Request detailed information about a template-set."""
    args = {"operation": "show", "name": name, "repo": repo, "ref": ref}
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
):
    """Install a template-set from PyPI, wheel, or directory."""
    typer.echo("⏳  Installing via pip …")
    try:
        result = _run_handler(
            {
                "operation": "add",
                "source": source,
                "from_bundle": from_bundle,
                "editable": editable,
                "force": force,
            }
        )
    except Exception:  # noqa: BLE001
        typer.echo("❌  Installation failed.")
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
    editable: bool = typer.Option(
        False, "--editable", "-e", help="Install the source in editable mode"
    ),
    force: bool = typer.Option(
        False, "--force", help="Re-install even if already present"
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Submit a template-set installation job via JSON-RPC."""
    args = {
        "operation": "add",
        "source": source,
        "from_bundle": from_bundle,
        "editable": editable,
        "force": force,
        "repo": repo,
        "ref": ref,
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
):
    """Remove the package that provides a template-set."""
    if not yes:
        if not typer.confirm(f"Uninstall template-set '{name}' ?"):
            typer.echo("Aborted.")
            raise typer.Exit()

    typer.echo("⏳  Uninstalling via pip …")
    try:
        result = _run_handler({"operation": "remove", "name": name})
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
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Submit a template-set removal job via JSON-RPC."""
    if not yes:
        if not typer.confirm(f"Uninstall template-set '{name}' ?"):
            typer.echo("Aborted.")
            raise typer.Exit()

    args = {"operation": "remove", "name": name, "repo": repo, "ref": ref}
    try:
        task_id = _submit_task(args, gateway_url)
        typer.echo(f"Submitted remove → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
