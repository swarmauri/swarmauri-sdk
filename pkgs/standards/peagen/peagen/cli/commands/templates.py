# peagen/commands/templates.py
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, Optional

from peagen.handlers.templates_handler import templates_handler
from peagen.models import Task
import typer
import httpx

# ──────────────────────────────────────
local_template_sets_app = typer.Typer(
    help="Manage Peagen template-sets.",
    add_completion=False,
)

list_app = typer.Typer(help="List template-sets")
show_app = typer.Typer(help="Show details about a template-set")
add_app = typer.Typer(help="Install a template-set")
remove_app = typer.Typer(help="Remove a template-set")

template_sets_app.add_typer(list_app, name="list")
template_sets_app.add_typer(show_app, name="show")
template_sets_app.add_typer(add_app, name="add")
template_sets_app.add_typer(remove_app, name="remove")


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
def list_template_sets(
    ctx: typer.Context,
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


@list_app.command("submit", help="Submit a list task via gateway.")
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
def show_template_set(
    ctx: typer.Context,
    name: str = typer.Argument(..., metavar="SET_NAME"),
):
    discovered = _discover_template_sets()
    if name not in discovered:
        typer.echo(f"❌  Template-set '{name}' not found.")
        raise typer.Exit(code=1)

    # first hit wins unless user asked for more detail
    primary_path = discovered[name][0]
    typer.echo(f"\nTemplate-set: {name}")
    typer.echo(f"Location:    {primary_path}")

    if len(discovered[name]) > 1 and verbose:
        typer.echo("\n⚠️  Multiple copies found on search path:")
        for p in discovered[name][1:]:
            typer.echo(f"   ↳ {p}")

    if verbose:

        def _iter_files(base: Path):
            if verbose == 1:
                yield from sorted(f.name for f in base.iterdir() if f.is_file())
            else:  # verbose ≥ 2 ⇒ recursive
                for fp in base.rglob("*"):
                    if fp.is_file():
                        yield fp.relative_to(base)

        typer.echo("\nFiles:")
        for rel in _iter_files(primary_path):
            typer.echo(f" • {rel}")


# ─── add ───────────────────────────────
@local_template_sets_app.command(
    "add",
    help=(
        "Install a template-set distribution from PyPI, a wheel/sdist, or a "
        "local directory."
    ),
)
def add_template_set(
    ctx: typer.Context,
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
    )
):
    """
    Install a template-set extension.

    * **PyPI slug** → `pip install <slug>`
    * **Wheel / sdist** → `pip install ./dist/…`
    * **Directory** → `pip install (-e) <dir>`  (use *-e/--editable* to develop)
    """
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


@local_template_sets_app.command(
    "remove",
    help="Uninstall the package that owns a template-set.",
)
def remove_template_set(
    ctx: typer.Context,
    name: str = typer.Argument(..., metavar="SET_NAME"),
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip confirmation prompt.",
    )
):
    """Uninstall the wheel/editable project that exposes ``SET_NAME``."""
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


@remove_app.command("submit", help="Submit a remove task via gateway.")
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
