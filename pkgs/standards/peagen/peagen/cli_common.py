"""
peagen.cli_common
─────────────────────────────────────────────────────────────────────────────
Shared helpers for every Typer command in the v2 CLI surface.
"""

from __future__ import annotations

import os
import pathlib
import types
from typing import Any, Callable, Optional

import click
import typer


# ─────────────────────────────────────────────────────────────────────────────
# 1. PathOrURI
# ─────────────────────────────────────────────────────────────────────────────
class PathOrURI(str):
    """
    A very thin wrapper that normalises user input:

        * '~/foo'      -> 'file:///home/user/foo'
        * 'C:\\bar'    -> 'file:///C:/bar'
        * 's3://...'   -> unchanged
        * 'file://...' -> unchanged
    """

    def __new__(cls, value: str | os.PathLike) -> "PathOrURI":
        return super().__new__(cls, cls._normalise(value))

    # ---------------------------------------------------------------- private
    @staticmethod
    def _normalise(value: str | os.PathLike) -> str:
        value = str(value)

        # already a URI?
        if "://" in value:
            return value

        # expand user and resolve relative path, return the *plain* path
        p = pathlib.Path(value).expanduser().resolve()
        return str(p)          # no file:// prefix

# ─────────────────────────────────────────────────────────────────────────────
# 2. common_peagen_options decorator
# ─────────────────────────────────────────────────────────────────────────────
def common_peagen_options(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Injects the shared CLI flags and stashes their values in `ctx.obj`.

    The decorated function **must** declare the following parameters
    (with *any* default values you like):

        workers: int
        truncate: bool
        artifacts: PathOrURI
        org: Optional[str]
        provider: Optional[str]
        template_set: Optional[str]
        additional_package_dirs: Optional[str]
        notify: Optional[str]

    Example:

    ```python
    @process_app.command()
    @common_peagen_options
    def process_cmd(
        ctx: typer.Context,
        workers: int = 4,
        truncate: bool = False,
        artifacts: PathOrURI = PathOrURI("./peagen_out"),
        org: Optional[str] = typer.Option(None, "--org"),
        provider: Optional[str] = typer.Option(None, "--provider"),
        template_set: Optional[str] = typer.Option(None, "--template-set"),
        additional_package_dirs: Optional[str] = typer.Option(None, "--additional-package-dirs"),
        notify: Optional[str] = typer.Option(None, "--notify"),
        # ... your own flags below ...
    ):
        ...
    ```
    """

    import functools

    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        ctx: typer.Context = click.get_current_context()
        if ctx.obj is None:
            ctx.obj = types.SimpleNamespace()

        # copy recognised kwargs into ctx.obj
        for key in (
            "workers",
            "truncate",
            "artifacts",
            "org",
            "provider",
            "template_set",
            "additional_package_dirs",
            "notify",
        ):
            if key in kwargs:
                setattr(ctx.obj, key, kwargs[key])

        return fn(*args, **kwargs)

    return _wrapper
