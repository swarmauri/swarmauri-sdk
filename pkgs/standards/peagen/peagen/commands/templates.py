# peagen/commands/templates.py
"""
Peagen “template-sets” sub-commands.

Usage (wired in peagen/cli.py):

    from peagen.commands.templates import template_sets_app
    app.add_typer(template_sets_app, name="template-sets")

This gives you:

    peagen template-sets list              # list all discovered sets
    peagen template-sets show <SET_NAME>   # inspect a single set
"""

from pathlib import Path
from typing import Dict, List

import typer

# ── absolute-import the namespace that holds built-in template folders ────────
import peagen.templates as _pt

# ── Typer sub-app boilerplate ────────────────────────────────────────────────
template_sets_app = typer.Typer(
    help="Manage Peagen template-sets (list, show).",
    add_completion=False,
)

# ── helpers ───────────────────────────────────────────────────────────────────
def _namespace_dirs() -> List[Path]:
    """Return the search roots that may contain template-set folders."""
    return [Path(p) for p in _pt.__path__]

def _discover_template_sets() -> Dict[str, List[Path]]:
    """
    Walk every namespace dir and build a mapping
    SET_NAME -> [<all physical locations that provide it>].
    """
    sets: Dict[str, List[Path]] = {}
    for ns_root in _namespace_dirs():
        try:
            for child in ns_root.iterdir():
                if child.is_dir():
                    sets.setdefault(child.name, []).append(child)
        except PermissionError:
            # Skip unreadable namespace roots but keep going.
            continue
    return sets


# ── sub-commands ─────────────────────────────────────────────────────────────
@template_sets_app.command("list", help="List all discovered template-sets.")
def list_template_sets(
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Increase verbosity (-v shows physical paths).",
    ),
):
    """
    Enumerate every template-set Peagen can see on the current search path.
    """
    discovered = _discover_template_sets()
    if not discovered:
        typer.echo("⚠️  No template-sets found!")
        raise typer.Exit(code=1)

    typer.echo("\nAvailable template-sets:")
    for name, paths in sorted(discovered.items()):
        typer.echo(f" • {name}")
        if verbose:
            for p in paths:
                typer.echo(f"     ↳ {p}")
    typer.echo(f"\nTotal: {len(discovered)} set(s)")


@template_sets_app.command("show", help="Show the contents of a template-set.")
def show_template_set(
    name: str = typer.Argument(..., metavar="SET_NAME"),
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Increase verbosity (-v prints file list, -vv prints full paths).",
    ),
):
    """
    Display basic information about a single template-set.

    The first matching set on the search path wins, but add -v / -vv to
    inspect all duplicates and their files.
    """
    discovered = _discover_template_sets()
    if name not in discovered:
        typer.echo(f"❌  Template-set '{name}' not found.")
        raise typer.Exit(code=1)

    # First hit wins unless user asked for more detail.
    primary_path = discovered[name][0]
    typer.echo(f"\nTemplate-set: {name}")
    typer.echo(f"Location: {primary_path}")

    if len(discovered[name]) > 1 and verbose:
        typer.echo("\n⚠️  Multiple copies found on search path:")
        for p in discovered[name][1:]:
            typer.echo(f"   ↳ {p}")

    if verbose:
        # List files (non-recursive for -v, recursive for -vv).
        def _iter_files(base: Path):
            if verbose == 1:
                yield from sorted(f.name for f in base.iterdir() if f.is_file())
            else:  # verbose >= 2 ⇒ full recursive tree
                for fp in base.rglob("*"):
                    if fp.is_file():
                        yield fp.relative_to(base)

        typer.echo("\nFiles:")
        for rel in _iter_files(primary_path):
            typer.echo(f" • {rel}")

