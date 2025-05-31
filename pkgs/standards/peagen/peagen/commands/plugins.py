from __future__ import annotations

import importlib.metadata as im
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Set

import typer

from peagen.plugin_registry import GROUPS, registry, discover_and_register_plugins

plugins_app = typer.Typer(help="Manage Peagen plugins.", add_completion=False)


def _installed_plugins() -> Dict[str, Set[str]]:
    return {k: set(v.keys()) for k, v in registry.items()}


def _build_installer(editable: bool, force: bool) -> list[str]:
    if shutil.which("uv"):
        cmd = ["uv", "pip", "install"]
    else:
        cmd = [sys.executable, "-m", "pip", "install"]
    cmd += ["--no-deps"]
    if force:
        cmd += ["--upgrade", "--force-reinstall"]
    if editable:
        cmd += ["-e"]
    return cmd


@plugins_app.command("list", help="List discovered plugins.")
def list_plugins(verbose: bool = typer.Option(False, "-v", "--verbose")) -> None:
    for group_key, (ep_group, _) in GROUPS.items():
        eps = im.entry_points(group=ep_group)
        if not eps:
            continue
        typer.echo(f"\n{group_key}:")
        for ep in sorted(eps, key=lambda e: e.name):
            line = f" • {ep.name}"
            if verbose:
                dist = getattr(ep, "dist", None)
                if dist is not None:
                    line += f" ({dist.metadata.get('Name')})"
            typer.echo(line)


@plugins_app.command("install", help="Install a plugin distribution.")
def install_plugin(
    source: str = typer.Argument(..., metavar="PKG|WHEEL|DIR"),
    editable: bool = typer.Option(False, "--editable", "-e", help="Editable mode for directories."),
    force: bool = typer.Option(False, "--force", help="Re-install even if already present."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show pip output."),
) -> None:
    src_path = Path(source)
    is_local = src_path.exists()

    if is_local:
        if src_path.is_dir():
            cmd = _build_installer(editable, force)
            cmd.append(str(src_path.resolve()))
        else:
            cmd = _build_installer(False, force)
            cmd.append(str(src_path.resolve()))
    else:
        cmd = _build_installer(False, force)
        cmd.append(source)

    before = _installed_plugins()
    typer.echo("⏳  Installing via pip …")
    try:
        subprocess.run(
            cmd,
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

    discover_and_register_plugins()
    after = _installed_plugins()
    added = {g: after[g] - before.get(g, set()) for g in after}
    new_items = [f"{g}:{','.join(sorted(v))}" for g, v in added.items() if v]
    if new_items:
        typer.echo("✅  Installed plugin(s): " + ", ".join(new_items))
    else:
        typer.echo("✅  Installation succeeded.")


@plugins_app.command("remove", help="Uninstall a plugin distribution by package name.")
def remove_plugin(
    package: str = typer.Argument(..., metavar="PACKAGE"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show pip output."),
) -> None:
    if not yes:
        if not typer.confirm(f"Uninstall distribution {package} ?"):
            typer.echo("Aborted.")
            raise typer.Exit()

    if shutil.which("uv"):
        cmd = ["uv", "pip", "uninstall", package]
    else:
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package]

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

    discover_and_register_plugins()
    typer.echo(f"✅  Removed distribution '{package}'.")
