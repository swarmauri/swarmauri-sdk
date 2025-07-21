"""
auth_authn_idp.cli
==================
Administration command‑line for the Auth‑AuthN IdP.

Usage examples
--------------
    # Create a new tenant and initial admin user
    auth-authn tenants create acme --issuer https://login.acme.com
    auth-authn users add --tenant acme --username alice --email alice@acme.com

    # Rotate signing keys for all tenants
    auth-authn tenants rotate-keys --grace 7776000   # 90 days

    # List registered RPs for a tenant
    auth-authn clients list --tenant acme
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from typing import Optional

import typer

from ..config import Settings, settings as _settings

###############################################################################
# Banner & Logging helpers                                                    #
###############################################################################

_BANNER = r"""
     _          _   _       _   _       _   _  _   _ 
    /_\   _ __ | |_(_) __ _| |_(_) ___ | |_| || | (_)
   //_\\ | '_ \| __| |/ _` | __| |/ _ \| __| || |_| |
  /  _  \| | | | |_| | (_| | |_| | (_) | |_|__   _| |
  \_/ \_/|_| |_|\__|_|\__,_|\__|_|\___/ \__|  |_| |_|

"""


def _print_banner() -> None:
    if sys.stdout.isatty():
        typer.echo(typer.style(_BANNER, fg=typer.colors.CYAN, bold=True))
        typer.echo(
            f"Auth‑AuthN IdP · Version {_settings.project_name} ({_settings.environment})\n"
        )


def _configure_logging(level: str) -> None:
    root = logging.getLogger()
    if root.handlers:
        # preserve existing handlers (uvicorn etc.) but honour new level
        root.setLevel(level)
        return

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")


###############################################################################
# Typer root                                                                  #
###############################################################################

app = typer.Typer(
    add_completion=False,
    help="Administrative CLI for the Auth‑AuthN Identity‑Provider.",
    invoke_without_command=True,
)


@app.callback(invoke_without_command=True)
def _main(
    ctx: typer.Context,
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress startup banner.",
    ),
    log_level: str = typer.Option(
        _settings.log_level,
        "--log-level",
        "-l",
        help="Python logging level.",
        metavar="LEVEL",
        case_sensitive=False,
    ),
    db_url: Optional[str] = typer.Option(
        None,
        "--db-url",
        help="Override the DB URL for this invocation only.",
        metavar="URL",
    ),
) -> None:
    """
    Global options shared by every sub‑command.
    """

    # 1. logging first – banner uses typer.echo (TTY only)
    _configure_logging(log_level.upper())

    # 2. banner
    if not quiet:
        _print_banner()

    # 3. optional DB override (useful for ad‑hoc maintenance)
    if db_url:
        os.environ["AUTH_AUTHN_DATABASE_URL"] = db_url
        # Re‑load settings object lazily for sub‑commands
        Settings.model_rebuild(force=True)

    if ctx.invoked_subcommand is None:  # pragma: no cover
        typer.echo(ctx.get_help())


###############################################################################
# Lazy‑import sub‑command modules                                             #
###############################################################################

_SUB_COMMANDS = {
    "tenants": ".tenants",
    "clients": ".clients",
    "users": ".users",
    "keys": ".keys",
}

for _name, _rel_import in _SUB_COMMANDS.items():
    try:
        _module = importlib.import_module(__package__ + _rel_import)
        app.add_typer(_module.app, name=_name)
    except Exception as exc:  # pragma: no cover
        # Do not crash whole CLI if optional plugin missing
        logging.getLogger(__name__).warning(
            "Failed loading CLI cmd '%s': %s", _name, exc
        )


###############################################################################
# Entrypoint                                                                  #
###############################################################################


def _entry() -> None:  # pragma: no cover
    """
    Console‑script entry‑point defined in `pyproject.toml`:

        [project.scripts]
        auth-authn = "auth_authn_idp.cli.__init__:_entry"
    """
    app()


if __name__ == "__main__":  # pragma: no cover
    _entry()
