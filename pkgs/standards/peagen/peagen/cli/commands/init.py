# peagen/commands/init.py
"""
peagen init – scaffolding helpers for every first-class artefact.

Templates are rendered via :mod:`peagen.core.init_core` and can be
provided by entry-point plugins registered under ``peagen.template_sets``.
"""

from __future__ import annotations

import asyncio
import textwrap
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from swarmauri_standard.loggers.Logger import Logger

import typer
from peagen.handlers.init_handler import init_handler
from peagen.models import Task

# ── Typer root ───────────────────────────────────────────────────────────────
init_app = typer.Typer(help="Bootstrap Peagen artefacts (project, template-set …)")



# ── utilities ────────────────────────────────────────────────────────────────
def _call_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke ``init_handler`` synchronously."""
    task = Task(
        id=str(uuid.uuid4()),
        pool="default",
        payload={"args": args},
    )
    return asyncio.run(init_handler(task))


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )


# ── init project ─────────────────────────────────────────────────────────────
@init_app.command("project", help="Create a new Peagen project skeleton.")
def init_project(
    path: Path = typer.Argument(".", exists=False, dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
):
    self = Logger(name="init_project")
    self.logger.info("Entering init_project command")
    project_root = path if isinstance(path, str) else path.name
    args: Dict[str, Any] = {
        "kind": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
    }

    result = _call_handler(args)
    _summary(path, result["next"])
    self.logger.info("Exiting init_project command")


# ── init template-set ────────────────────────────────────────────────────────
@init_app.command("template-set", help="Create a template-set wheel skeleton.")
def init_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set ID."),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_template_set")
    self.logger.info("Entering init_template_set command")
    args: Dict[str, Any] = {
        "kind": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }

    result = _call_handler(args)
    _summary(path, result["next"])
    self.logger.info("Exiting init_template_set command")


# ── init doe-spec ────────────────────────────────────────────────────────────
@init_app.command("doe-spec", help="Create a DOE-spec stub.")
def init_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_doe_spec")
    self.logger.info("Entering init_doe_spec command")
    args: Dict[str, Any] = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    result = _call_handler(args)
    _summary(path, result["next"])
    self.logger.info("Exiting init_doe_spec command")


# ── init ci ─────────────────────────────────────────────────────────────────
@init_app.command("ci", help="Drop a CI pipeline file for GitHub or GitLab.")
def init_ci(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_ci")
    self.logger.info("Entering init_ci command")
    kind = "ci-github" if github else "ci-gitlab"
    args: Dict[str, Any] = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    _call_handler(args)
    typer.echo("✅  CI file written.  Commit it to enable automatic runs.")
    self.logger.info("Exiting init_ci command")
