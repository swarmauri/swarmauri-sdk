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

import httpx
import typer
from peagen.handlers.init_handler import init_handler
from peagen.models import Status, Task

# ── Typer root ───────────────────────────────────────────────────────────────
init_app = typer.Typer(help="Bootstrap Peagen artefacts (project, template-set …)")


# ── helpers ─────────────────────────────────────────────────────────────────-
DEFAULT_GATEWAY = "http://localhost:8000/rpc"


def _build_task(args: Dict[str, Any]) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        status=Status.pending,
        payload={"action": "init", "args": args},
    )


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(
            f"""
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """
        )
    )


# ── project ─────────────────────────────────────────────────────────────────
project_app = typer.Typer(help="Create a new Peagen project skeleton.")


@project_app.command("run")
def run_project(
    path: Path = typer.Argument(".", exists=False, dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
):
    logger = Logger(name="init_project_run")
    logger.logger.info("Entering init_project run")
    args: Dict[str, Any] = {
        "kind": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    _summary(path, result["next"])
    logger.logger.info("Exiting init_project run")


@project_app.command("submit")
def submit_project(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
):
    logger = Logger(name="init_project_submit")
    logger.logger.info("Entering init_project submit")
    args: Dict[str, Any] = {
        "kind": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
    }
    task = _build_task(args)
    envelope = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    try:
        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted init → taskId={task.id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
    logger.logger.info("Exiting init_project submit")


# ── template-set ────────────────────────────────────────────────────────────
template_set_app = typer.Typer(help="Create a template-set wheel skeleton.")


@template_set_app.command("run")
def run_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set ID."),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
):
    logger = Logger(name="init_template_set_run")
    logger.logger.info("Entering init_template_set run")
    args: Dict[str, Any] = {
        "kind": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    _summary(path, result["next"])
    logger.logger.info("Exiting init_template_set run")


@template_set_app.command("submit")
def submit_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set ID."),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
):
    logger = Logger(name="init_template_set_submit")
    logger.logger.info("Entering init_template_set submit")
    args: Dict[str, Any] = {
        "kind": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    task = _build_task(args)
    envelope = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    try:
        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted init → taskId={task.id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
    logger.logger.info("Exiting init_template_set submit")


# ── doe-spec ────────────────────────────────────────────────────────────────
doe_spec_app = typer.Typer(help="Create a DOE-spec stub.")


@doe_spec_app.command("run")
def run_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
):
    logger = Logger(name="init_doe_spec_run")
    logger.logger.info("Entering init_doe_spec run")
    args: Dict[str, Any] = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    _summary(path, result["next"])
    logger.logger.info("Exiting init_doe_spec run")


@doe_spec_app.command("submit")
def submit_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
):
    logger = Logger(name="init_doe_spec_submit")
    logger.logger.info("Entering init_doe_spec submit")
    args: Dict[str, Any] = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    task = _build_task(args)
    envelope = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    try:
        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted init → taskId={task.id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
    logger.logger.info("Exiting init_doe_spec submit")


# ── ci ─────────────────────────────────────────────────────────────────────--
ci_app = typer.Typer(help="Drop a CI pipeline file for GitHub or GitLab.")


@ci_app.command("run")
def run_ci(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
):
    logger = Logger(name="init_ci_run")
    logger.logger.info("Entering init_ci run")
    args: Dict[str, Any] = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    task = _build_task(args)
    asyncio.run(init_handler(task))
    typer.echo("✅  CI file written.  Commit it to enable automatic runs.")
    logger.logger.info("Exiting init_ci run")


@ci_app.command("submit")
def submit_ci(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
):
    logger = Logger(name="init_ci_submit")
    logger.logger.info("Entering init_ci submit")
    args: Dict[str, Any] = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    task = _build_task(args)
    envelope = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    try:
        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted init → taskId={task.id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
    logger.logger.info("Exiting init_ci submit")


# ── attach sub-apps ----------------------------------------------------------
init_app.add_typer(project_app, name="project")
init_app.add_typer(template_set_app, name="template-set")
init_app.add_typer(doe_spec_app, name="doe-spec")
init_app.add_typer(ci_app, name="ci")
