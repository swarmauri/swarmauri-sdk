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

DEFAULT_GATEWAY = "http://localhost:8000/rpc"

# ── Typer root ───────────────────────────────────────────────────────────────
init_app = typer.Typer(help="Bootstrap Peagen artefacts (project, template-set …)")

# create sub-apps mirroring the pattern used by the sort command
project_app = typer.Typer(help="Manage project scaffolding.")
template_set_app = typer.Typer(help="Manage template-set scaffolding.")
doe_spec_app = typer.Typer(help="Manage DOE-spec scaffolding.")
ci_app = typer.Typer(help="Manage CI scaffolding.")

# register sub-apps
init_app.add_typer(project_app, name="project")
init_app.add_typer(template_set_app, name="template-set")
init_app.add_typer(doe_spec_app, name="doe-spec")
init_app.add_typer(ci_app, name="ci")


# ── utilities ────────────────────────────────────────────────────────────────
def _call_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke ``init_handler`` synchronously."""
    task = Task(
        id=str(uuid.uuid4()),
        pool="default",
        payload={"action": "init", "args": args},
    )
    return asyncio.run(init_handler(task))


def _submit_task(args: Dict[str, Any], gateway_url: str, tag: str) -> None:
    """Send *args* to a JSON-RPC worker."""
    task = Task(
        id=str(uuid.uuid4()), pool="default", payload={"action": "init", "args": args}
    )
    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"pool": task.pool, "payload": task.payload},
    }

    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted {tag} → taskId={data['id']}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )


# ── init project ─────────────────────────────────────────────────────────────
@project_app.command("run", help="Create a new Peagen project skeleton locally.")
def run_project(
    path: Path = typer.Argument(".", exists=False, dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
):
    self = Logger(name="init_project")
    self.logger.info("Entering init_project command")
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


@project_app.command("submit", help="Submit a project scaffold task.")
def submit_project(
    path: Path = typer.Argument(".", exists=False, dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {
        "kind": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
    }
    _submit_task(args, gateway_url, "init project")


# ── init template-set ────────────────────────────────────────────────────────
@template_set_app.command("run", help="Create a template-set wheel skeleton locally.")
def run_template_set(
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


@template_set_app.command("submit", help="Submit a template-set scaffold task.")
def submit_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set ID."),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {
        "kind": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    _submit_task(args, gateway_url, "init template-set")


# ── init doe-spec ────────────────────────────────────────────────────────────
@doe_spec_app.command("run", help="Create a DOE-spec stub locally.")
def run_doe_spec(
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


@doe_spec_app.command("submit", help="Submit a DOE-spec scaffold task.")
def submit_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    _submit_task(args, gateway_url, "init doe-spec")


# ── init ci ─────────────────────────────────────────────────────────────────
@ci_app.command("run", help="Drop a CI pipeline file locally for GitHub or GitLab.")
def run_ci(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_ci")
    self.logger.info("Entering init_ci command")
    args: Dict[str, Any] = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    _call_handler(args)
    typer.echo("✅  CI file written.  Commit it to enable automatic runs.")
    self.logger.info("Exiting init_ci command")


@ci_app.command("submit", help="Submit a CI pipeline scaffold task.")
def submit_ci(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    args = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    _submit_task(args, gateway_url, "init ci")
