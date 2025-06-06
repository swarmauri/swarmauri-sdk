#!/usr/bin/env python3
"""Entry point for the Peagen command-line interface."""

from __future__ import annotations
import logging, sys, os
from pathlib import Path
import typer

# ─── Sub-command apps ──────────────────────────────────────────────────────
from .commands import (
    local_doe_app, remote_doe_app,
    local_eval_app, remote_eval_app,
    local_extras_app,
    local_fetch_app, remote_fetch_app,
    local_init_app,
    local_process_app, remote_process_app,
    local_sort_app, remote_sort_app,
    local_validate_app,
    remote_task_app,
    local_template_sets_app,
)

# ─── Banner helper (printed unless –quiet) ────────────────────────────────
from ._banner import _print_banner

app = typer.Typer(help="CLI tool for processing project files using Peagen.")
local_app    = typer.Typer()      # will host all *run* commands
remote_app   = typer.Typer()      # will host all *submit* commands
# ───────────────────── LOCAL GLOBAL CALLBACK ───────────────────────────────
@local_app.callback()
def __global_local_ctx(           # noqa: D401
    ctx: typer.Context,
    verbose: int = typer.Option(0, "-v", "--verbose", count=True),
    directory: Path = typer.Option(
        ".", "-d", "--directory", dir_okay=True, exists=True,
        help="Treat this directory as CWD before running."
    ),
    config: Path = typer.Option(
        None, "-c", "--config",
        exists=True, file_okay=True, dir_okay=True, resolve_path=True,
        help="Override .peagen.toml for THIS run."
    ),
    quiet: bool = typer.Option(False, "-q", "--quiet"),
) -> None:
    """
    Runs **once** before any sub-command.

    * Sets the root logging level.
    * Stores ``config`` path & ``verbosity`` in ``ctx.obj`` so every command
      can reuse them.
    """
    # 0) Banner -------------------------------------------------------------
    if not quiet:
        _print_banner()

    # 1) Logging setup ------------------------------------------------------
    level = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}.get(
        min(verbose, 2), logging.NOTSET
    )
    logging.basicConfig(
        level=level,
        format="%(levelname)7s  %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if verbose >= 3:                                   # TRACE
        logging.getLogger().setLevel(5)

    # 2) Make sure ctx.obj exists and stash globals ------------------------
    ctx.ensure_object(dict)
    ctx.obj.update(
        verbosity = verbose,
        cwd       = directory,
        config_path = config,        # may be None
        quiet     = quiet,
    )
    os.chdir(directory)             # one line, now every *run* sees CWD

# ─────────────────────── GLOBAL REMOTE CALLBACK ───────────────────────────────
@remote_app.callback(invoke_without_command=True)
def _global_remote_ctx(            # noqa: D401
    ctx: typer.Context,
    gateway_url: str = typer.Option(
        "http://localhost:8000/rpc", "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
    override: str = typer.Option(
        None, "--override", help="JSON string to merge into cfg on the worker."
    ),
    override_file: Path = typer.Option(
        None, "--override-file",
        exists=True, file_okay=True, resolve_path=True,
        help="Path to a *second* .peagen.toml that is sent to the worker."
    ),
    verbose: int = typer.Option(0, "-v", "--verbose", count=True),
    quiet: bool = typer.Option(False, "-q", "--quiet"),

) -> None:
    if not quiet:
        _print_banner()
    ctx.ensure_object(dict)
    ctx.obj.update(
        verbosity = verbose,
        gateway_url = gateway_url,
        task_override_inline = override,
        task_override_file   = override_file,
        quiet     = quiet,
    )

# ─────────────────────────── SUB-COMMAND REGISTRY ───────────────────────────

app.add_typer(local_app, name="local")
app.add_typer(remote_app, name="remote")


local_app.add_typer(local_doe_app,)
local_app.add_typer(local_eval_app,)
local_app.add_typer(local_extras_app, name="extras-schemas")
local_app.add_typer(local_fetch_app,)
local_app.add_typer(local_init_app,          name="init")
local_app.add_typer(local_process_app)
local_app.add_typer(local_sort_app,)
local_app.add_typer(local_template_sets_app, name="template-set")
local_app.add_typer(local_validate_app)


remote_app.add_typer(remote_doe_app,)
remote_app.add_typer(remote_eval_app,)
remote_app.add_typer(remote_fetch_app,)
remote_app.add_typer(remote_process_app,)
remote_app.add_typer(remote_sort_app,)
remote_app.add_typer(remote_task_app,        name="task")

if __name__ == "__main__":
    app()

