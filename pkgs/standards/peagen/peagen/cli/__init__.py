#!/usr/bin/env python3
"""Entry point for the Peagen command-line interface."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import httpx
from peagen import defaults
import typer

try:  # pragma: no cover - keyring may be unavailable
    import keyring
except Exception:  # noqa: BLE001
    keyring = None

from autoapi_client import AutoAPIClient

# ─── Banner helper (printed unless –quiet) ────────────────────────────────
from peagen.cli._banner import _print_banner

# ─── Sub-command apps ──────────────────────────────────────────────────────
from peagen.cli.commands import (
    local_doe_app,
    local_eval_app,
    local_extras_app,
    fetch_app,
    local_db_app,
    local_init_app,
    local_process_app,
    local_mutate_app,
    local_evolve_app,
    local_sort_app,
    local_template_sets_app,
    local_validate_app,
    local_publickey_app,
    local_deploykey_app,
    local_secrets_app,
    show_app,
    remote_doe_app,
    remote_eval_app,
    remote_process_app,
    remote_db_app,
    remote_mutate_app,
    remote_evolve_app,
    remote_sort_app,
    remote_task_app,
    remote_template_sets_app,
    remote_validate_app,
    remote_publickey_app,
    remote_deploykey_app,
    remote_secrets_app,
    local_analysis_app,
    remote_analysis_app,
    dashboard_app,
    remote_init_app,
)

app = typer.Typer(help="CLI tool for processing project files using Peagen.")
local_app = typer.Typer(help="Commands executed locally on this machine.")
remote_app = typer.Typer(help="Commands that submit tasks to a JSON-RPC gateway.")


# ───────────────────── LOCAL GLOBAL CALLBACK ───────────────────────────────
@local_app.callback()
def __global_local_ctx(  # noqa: D401
    ctx: typer.Context,
    verbose: int = typer.Option(0, "-v", "--verbose", count=True),
    directory: Path = typer.Option(
        ".",
        "-d",
        "--directory",
        dir_okay=True,
        exists=True,
        help="Treat this directory as CWD before running.",
    ),
    config: Path = typer.Option(
        None,
        "-c",
        "--config",
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True,
        help="Override .peagen.toml for THIS run.",
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
    if verbose >= 3:  # TRACE
        logging.getLogger().setLevel(5)

    # 2) Make sure ctx.obj exists and stash globals ------------------------
    ctx.ensure_object(dict)
    ctx.obj.update(
        verbosity=verbose,
        cwd=directory,
        config_path=config,  # may be None
        quiet=quiet,
    )
    os.chdir(directory)  # one line, now every *run* sees CWD


# ─────────────────────── GLOBAL REMOTE CALLBACK ───────────────────────────────
@remote_app.callback(invoke_without_command=True)
def _global_remote_ctx(  # noqa: D401
    ctx: typer.Context,
    gateway_url: str = typer.Option(
        "http://localhost:8000/rpc", "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="PEAGEN_API_KEY",
        help="API key for authenticated gateway access",
    ),
    override: str = typer.Option(
        None, "--override", help="JSON string to merge into cfg on the worker."
    ),
    override_file: Path = typer.Option(
        None,
        "--override-file",
        exists=True,
        file_okay=True,
        resolve_path=True,
        help="Path to a *second* .peagen.toml that is sent to the worker.",
    ),
    pool: str = typer.Option(
        os.getenv("PEAGEN_POOL", defaults.DEFAULT_POOL),
        "--pool",
        help="Tenant or pool for multi-tenant deployments",
    ),
    repo: str = typer.Option(None, "--repo", help="repository URL"),
    ref: str = typer.Option(None, "--ref", help="branch/tag/SHA (default: HEAD)"),
    verbose: int = typer.Option(0, "-v", "--verbose", count=True),
    quiet: bool = typer.Option(False, "-q", "--quiet"),
) -> None:
    """Set remote command defaults and stash them in ``ctx.obj``."""
    if not quiet:
        _print_banner()
    ctx.ensure_object(dict)
    gw_url = gateway_url.rstrip("/")
    if not gw_url.endswith("/rpc"):
        gw_url += "/rpc"

    if api_key is None and keyring is not None:  # pragma: no branch
        try:
            api_key = keyring.get_password("auto_authn-api-key", "default")
        except Exception:  # noqa: BLE001
            api_key = None

    rpc_client = AutoAPIClient(
        gw_url,
        client=httpx.Client(timeout=defaults.RPC_TIMEOUT),
        api_key=api_key,
    )
    ctx.obj.update(
        verbosity=verbose,
        gateway_url=gw_url,
        task_override_inline=override,
        task_override_file=override_file,
        pool=pool,
        repo=repo,
        ref=ref,
        quiet=quiet,
        api_key=api_key,
        rpc=rpc_client,
    )
    ctx.call_on_close(rpc_client.close)


# ─────────────────────────── SUB-COMMAND REGISTRY ───────────────────────────

app.add_typer(fetch_app)
app.add_typer(local_app, name="local")
app.add_typer(remote_app, name="remote")
app.add_typer(dashboard_app)


local_app.add_typer(local_doe_app, name="doe")
local_app.add_typer(
    local_eval_app,
)
local_app.add_typer(local_extras_app, name="extras-schemas")
local_app.add_typer(local_db_app, name="db")
local_app.add_typer(local_process_app)
local_app.add_typer(local_mutate_app)
local_app.add_typer(local_evolve_app)
local_app.add_typer(local_sort_app)
local_app.add_typer(local_analysis_app)
local_app.add_typer(local_template_sets_app, name="template-set")
local_app.add_typer(local_validate_app)
local_app.add_typer(local_secrets_app, name="secrets")
local_app.add_typer(local_publickey_app, name="publickey")
local_app.add_typer(local_deploykey_app, name="deploykey")
local_app.add_typer(show_app, name="git")
local_app.add_typer(local_init_app, name="init")


remote_app.add_typer(remote_doe_app, name="doe")
remote_app.add_typer(remote_eval_app)
remote_app.add_typer(remote_db_app, name="db")
remote_app.add_typer(remote_process_app)
remote_app.add_typer(remote_mutate_app)
remote_app.add_typer(remote_evolve_app)
remote_app.add_typer(remote_sort_app)
remote_app.add_typer(remote_task_app, name="task")
remote_app.add_typer(remote_analysis_app, name="analysis")
remote_app.add_typer(remote_template_sets_app, name="template-set")
remote_app.add_typer(remote_validate_app)
remote_app.add_typer(remote_secrets_app, name="secrets")
remote_app.add_typer(remote_publickey_app, name="publickey")
remote_app.add_typer(remote_deploykey_app, name="deploykey")
remote_app.add_typer(remote_init_app, name="init")

if __name__ == "__main__":
    app()
