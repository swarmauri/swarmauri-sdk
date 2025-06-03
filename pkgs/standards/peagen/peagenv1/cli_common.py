"""Shared helpers for Typer commands."""

from __future__ import annotations

import os
import pathlib
import tempfile
from contextlib import contextmanager
import shutil
import types
from typing import Any, Callable

import click
import typer
import logging


# ─────────────────────────────────────────────────────────────────────────────
# 0. temp_workspace
# ─────────────────────────────────────────────────────────────────────────────
@contextmanager
def temp_workspace(prefix: str = "peagen_"):
    """Yield a temporary directory that is removed on exit."""
    dirpath = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield dirpath  # ←  every path you write will be under here
    finally:
        try:
            shutil.rmtree(dirpath)
        except FileNotFoundError:
            # Already removed – fine.
            pass
        except OSError as exc:
            logging.warning(f"Workspace cleanup failed: {exc}")


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
        return str(p)  # no file:// prefix


# ─────────────────────────────────────────────────────────────────────────────
# 2. load .peagen.toml
# ─────────────────────────────────────────────────────────────────────────────
def load_peagen_toml(
    start_dir: pathlib.Path = pathlib.Path.cwd(), path: pathlib.Path | None = None
) -> dict[str, Any]:
    """Locate and load ``.peagen.toml`` starting from ``start_dir`` or an explicit ``path``."""
    if path:
        cfg_path = path.expanduser().resolve()
        if cfg_path.is_file():
            import tomllib

            return tomllib.loads(cfg_path.read_text("utf-8"))
        return {}

    for folder in [start_dir, *start_dir.parents]:
        cfg_path = folder / ".peagen.toml"
        if cfg_path.is_file():
            import tomllib  # tomli for 3.10

            res = tomllib.loads(cfg_path.read_text("utf-8"))
            return res
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# 3. common_peagen_options decorator
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
        plugin_mode: Optional[str]

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
        # before first CLI option is copied:
        if ctx.obj is None:
            cfg = load_peagen_toml()
            ctx.obj = types.SimpleNamespace(**cfg)
            ctx.obj.plugin_mode = cfg.get("plugins", {}).get("mode")

        # print(ctx.obj)
        # copy recognised kwargs into ctx.obj
        for key in (
            "workers",
            "truncate",
            "artifacts",
            "org",
            "default_provider",
            "default_model_name",
            "default_temperature",
            "default_max_tokens",
            "template_set",
            "additional_package_dirs",
            "notify",
            "plugin_mode",
        ):
            if key in kwargs:
                setattr(ctx.obj, key, kwargs[key])

        return fn(*args, **kwargs)

    return _wrapper
