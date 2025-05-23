# peagen/commands/templates.py
"""
Peagen “template-sets” sub-commands (list | show | add).

Wire it in peagen/cli.py with:

    from peagen.commands.templates import template_sets_app
    app.add_typer(template_sets_app, name="template-sets")
"""

import importlib.metadata as im
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

import peagen.templates as _pt  # root namespace that ships built-in sets
import typer

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
            pkg = ep.load()  # this is now the module object
            for root in getattr(pkg, "__path__", []):  # pkg.__path__ is a list of dirs
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
    src_path = Path(from_bundle) if from_bundle else Path(source)
    is_local = src_path.exists()

    # ------------------------------------------------------------------ helpers
    def _build_installer(use_editable: bool) -> List[str]:
        """
        Prefer **uv** if it is on PATH; fall back to stdlib pip.
        """
        import shutil

        if shutil.which("uv"):
            base = ["uv", "pip", "install"]
        else:
            base = [sys.executable, "-m", "pip", "install"]

        base += ["--no-deps"]
        if force:
            base += ["--upgrade", "--force-reinstall"]
        if use_editable:
            base += ["-e"]
        return base

    # ----------------------------------------------------------------- resolve
    if is_local:
        # directory OR file
        if src_path.is_dir():
            pip_cmd = _build_installer(editable)
            pip_cmd.append(str(src_path.resolve()))
        else:  # file (wheel / sdist)
            pip_cmd = _build_installer(False)
            pip_cmd.append(str(src_path.resolve()))
    else:
        # assume a PyPI project slug
        pip_cmd = _build_installer(False)
        pip_cmd.append(source)

    # ------------------------------------------------------------ install step
    typer.echo("⏳  Installing via pip …")
    sets_before = set(_discover_template_sets().keys())

    try:
        subprocess.run(
            pip_cmd,
            check=True,
            text=True,
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        typer.echo("❌  Installation failed.")
        if not verbose and exc.stdout:
            typer.echo(exc.stdout)
        raise typer.Exit(code=exc.returncode)

    # --------------------------------------------------------------- feedback
    sets_after = set(_discover_template_sets().keys())
    new_sets = sorted(sets_after - sets_before)

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
    """
    Uninstall the wheel / editable project that exposes *SET_NAME* in the
    ``peagen.template_sets`` entry-point group.
    """
    # ---------------------------------------------------------------- find dist(s)
    dists: list[str] = []
    for dist in im.distributions():
        if any(
            ep.group == "peagen.template_sets" and ep.name == name
            for ep in dist.entry_points
        ):
            dists.append(dist.metadata["Name"])

    if not dists:
        typer.echo(f"❌  Template-set '{name}' not found (nothing to remove).")
        raise typer.Exit(code=1)

    # ---------------------------------------------------------------- protect core
    PROTECTED_DISTS = {"peagen"}  # core wheel(s)
    protected = [d for d in dists if d.lower() in PROTECTED_DISTS]
    removable = [d for d in dists if d.lower() not in PROTECTED_DISTS]

    if protected and not removable:
        typer.echo(
            "⚠️  The requested template-set is bundled with Peagen itself and "
            "cannot be uninstalled."
        )
        raise typer.Exit(code=1)

    if protected and removable:
        typer.echo(
            "⚠️  Skipping core distribution(s) "
            + ", ".join(protected)
            + "; proceeding to uninstall "
            + ", ".join(removable)
        )
        dists = removable

    # ---------------------------------------------------------------- confirm
    if not yes:
        if not typer.confirm(f"Uninstall distribution(s): {', '.join(dists)} ?"):
            typer.echo("Aborted.")
            raise typer.Exit()

    # ---------------------------------------------------------------- build cmd
    if shutil.which("uv"):
        # uv’s pip clone does not need/allow -y (non-interactive by default)
        cmd = ["uv", "pip", "uninstall"] + dists
    else:
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y"] + dists

    # ---------------------------------------------------------------- run uninstall
    typer.echo("⏳  Uninstalling via pip …")
    try:
        subprocess.run(
            cmd,
            check=True,
            text=True,
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        typer.echo("❌  Uninstall failed.")
        if not verbose and exc.stdout:
            typer.echo(exc.stdout)
        raise typer.Exit(code=exc.returncode)

    # ---------------------------------------------------------------- verify
    if name in _discover_template_sets():
        typer.echo(
            "⚠️  Uninstall completed, but the template-set is still discoverable."
        )
    else:
        typer.echo(f"✅  Removed template-set '{name}'.")
