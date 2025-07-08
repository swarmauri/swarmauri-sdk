# peagen/commands/fetch.py
"""
CLI front-end for workspace reconstruction.

Run ``peagen fetch`` locally to materialise workspaces from URIs.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import List, Optional

import typer

from peagen.handlers.fetch_handler import fetch_handler
from peagen.orm import Status
from peagen.cli.task_helpers import build_task

fetch_app = typer.Typer(help="Materialise Peagen workspaces from URIs.")

# ───────────────────────── helpers ─────────────────────────


def _collect_args(
    workspaces: List[str],
    no_source: bool,
    install_template_sets_flag: bool,
    repo: Optional[str] = None,
    ref: str = "HEAD",
) -> dict:
    if repo:
        workspaces = [f"git+{repo}@{ref}"]

    return {
        "workspaces": workspaces,
        "out_dir": str(Path.cwd()),
        "no_source": no_source,
        "install_template_sets": install_template_sets_flag,
    }


# ───────────────────────── local run ───────────────────────
@fetch_app.command("fetch")
def run(
    ctx: typer.Context,
    workspaces: Optional[List[str]] = typer.Argument(None, help="Workspace URI(s)"),
    no_source: bool = typer.Option(
        False, "--no-source/--with-source", help="Skip cloning source packages"
    ),
    install_template_sets_flag: bool = typer.Option(
        True,
        "--install-template-sets/--no-install-template-sets",
        help="Install template sets referenced by the workspace descriptor",
    ),
    repo: Optional[str] = typer.Option(None, "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Synchronously build the workspace on this machine."""
    args = _collect_args(
        workspaces or [],
        no_source,
        install_template_sets_flag,
        repo,
        ref,
    )
    pool = "default"
    if ctx is not None and getattr(ctx, "obj", None):
        pool = ctx.obj.get("pool", "default")
    task = build_task("fetch", args, pool=pool, status=Status.WAITING)

    result = asyncio.run(fetch_handler(task))
    typer.echo(json.dumps(result, indent=2))
