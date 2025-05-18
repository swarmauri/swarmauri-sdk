# peagen/commands/templates.py
"""
Peagen “template-sets” sub-commands (list | show | add).

Wire it in peagen/cli.py with:

    from peagen.commands.templates import template_sets_app
    app.add_typer(template_sets_app, name="template-sets")
"""

from pathlib import Path
from typing import Dict, List, Optional
import importlib.metadata as im
import subprocess
import sys

import typer
import peagen.templates as _pt  # root namespace that ships built-in sets

# ──────────────────────────────────────
template_sets_app = typer.Typer(
    help="Manage Peagen template-sets.",
    add_completion=False,
)

# ─── helpers ───────────────────────────
def _namespace_dirs() -> List[Path]:
    """Return the search roots that may contain template-set folders."""
    return [Path(p) for p in _pt.__path__]

def _discover_template_sets() -> Dict[str, List[Path]]:
    """
    Build a mapping  SET_NAME -> [<all physical locations that provide it>].
    """
    sets: Dict[str, List[Path]] = {}
    for ns_root in _namespace_dirs():
        try:
            for child in ns_root.iterdir():
                if child.is_dir():
                    sets.setdefault(child.name, []).append(child)
        except PermissionError:
            # Skip unreadable roots but keep going.
            continue
    # also gather sets exposed via entry-points so wheels without a physical
    # folder in peagen.templates still show up.
    for ep in im.entry_points(group="peagen.template_sets"):
        try:
            pkg = ep.load()                             # this is now the module object
            for root in getattr(pkg, "__path__", []):   # pkg.__path__ is a list of dirs
                sets.setdefault(ep.name, []).append(Path(root))
        except Exception as e:
            print(f"⚠️  could not load plugin {ep.name!r}: {e}")
            continue
    return sets


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
    discovered = _discover_template_sets()
    if not discovered:
        typer.echo("⚠️  No template-sets found.")
        raise typer.Exit(code=1)

    typer.echo("\nAvailable template-sets:")
    for name, paths in sorted(discovered.items()):
        typer.echo(f" • {name}")
        if verbose:
            for p in paths:
                typer.echo(f"     ↳ {p}")
    typer.echo(f"\nTotal: {len(discovered)} set(s)")


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
@template_sets_app.command("add", help="Install a template-set wheel or PyPI package.")
def add_template_set(
    source: str = typer.Argument(..., metavar="PKG|WHEEL"),
    force: bool = typer.Option(
        False,
        "--force",
        help="Re-install even if already present.",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Show pip output.",
    ),
):
    """
    Install a template-set distribution.

    * `source` can be:
        • a PyPI project slug  (e.g. ``peagen_template_minimal_fast``)
        • a wheel or sdist path (``./dist/peagen_template_minimal-0.3.0-py3-none-any.whl``)
    """
    if Path(source).is_dir():
        typer.echo("❌  Directory installs are not supported; supply a wheel or PyPI slug.")
        raise typer.Exit(code=1)

    pip_cmd = [sys.executable, "-m", "pip", "install", "--no-deps"]
    if force:
        pip_cmd += ["--upgrade", "--force-reinstall"]
    pip_cmd.append(source)

    typer.echo("⏳  Installing via pip …")
    try:
        subprocess.run(
            pip_cmd,
            check=True,
            text=True,
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        typer.echo("❌  pip install failed.")
        if not verbose and exc.stdout:
            typer.echo(exc.stdout)
        raise typer.Exit(code=exc.returncode)

    # refresh discovery so the new set appears immediately
    discovered = _discover_template_sets()

    # try to guess the canonical set name(s) provided by this package
    new_sets = [
        name for name, paths in discovered.items()
        if any(source in str(p) for p in paths)
    ]
    if new_sets:
        typer.echo(
            f"✅  Installed template-set{'s' if len(new_sets) > 1 else ''}: "
            + ", ".join(sorted(new_sets))
        )
    else:
        typer.echo("✅  Installation succeeded, but no template-set entry-point found.")
