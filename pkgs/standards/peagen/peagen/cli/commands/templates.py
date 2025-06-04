# peagen/commands/templates.py
"""
Peagen “template-sets” sub-commands (list | show | add).

Wire it in peagen/cli.py with:

    from peagen.commands.templates import template_sets_app
    app.add_typer(template_sets_app, name="template-sets")
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, Optional

from peagen.handlers.templates_handler import templates_handler
from peagen.models import Task
import typer

# ──────────────────────────────────────
template_sets_app = typer.Typer(
    help="Manage Peagen template-sets.",
    add_completion=False,
)


# ─── helpers ───────────────────────────
def _run_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    task = Task(id=str(uuid.uuid4()), pool="default", payload={"args": args})
    return asyncio.run(templates_handler(task))


# ─── list ──────────────────────────────
@template_sets_app.command("list", help="List all discovered template-sets.")
def list_template_sets(
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


# ─── show ──────────────────────────────
@template_sets_app.command("show", help="Show the contents of a template-set.")
def show_template_set(
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


# ─── add ───────────────────────────────
@template_sets_app.command(
    "add",
    help=(
        "Install a template-set distribution from PyPI, a wheel/sdist, or a "
        "local directory."
    ),
)
def add_template_set(
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
        help="Stream pip/uv output.",
    ),
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


@template_sets_app.command(
    "remove",
    help="Uninstall the package that owns a template-set.",
)
def remove_template_set(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip confirmation prompt.",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Show pip/uv output.",
    ),
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
