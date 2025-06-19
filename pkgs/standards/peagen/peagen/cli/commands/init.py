# peagen/commands/init.py
"""
peagen init – scaffolding helpers for every first-class artefact.

Templates are rendered via :mod:`peagen.core.init_core` and can be
provided by entry-point plugins registered under ``peagen.template_sets``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import typer

from peagen._utils._init import _call_handler, _submit_task, _summary
from peagen._utils.git_filter import add_filter, init_git_filter
from swarmauri_standard.loggers.Logger import Logger

DEFAULT_GATEWAY = "http://localhost:8000/rpc"

# ── Typer root ───────────────────────────────────────────────────────────────
local_init_app = typer.Typer(
    help="Bootstrap Peagen artefacts (project, template-set …) locally"
)
remote_init_app = typer.Typer(
    help="Bootstrap Peagen artefacts (project, template-set …) via JSON-RPC",
)


@local_init_app.command("filter")
def local_init_filter(
    uri: str,
    name: str = "default",
    config: Path = Path(".peagen.toml"),
    repo: Path = Path("."),
) -> None:
    """Add a git filter entry and configure the repository."""
    add_filter(uri, name=name, config=config)
    init_git_filter(repo, uri, name=name)
    typer.echo(f"Configured filter '{name}' -> {uri} in {config}")


# ── init project ─────────────────────────────────────────────────────────────
@local_init_app.command("project")
def local_init_project(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", exists=False, dir_okay=True, file_okay=False, help="Target directory"
    ),
    template_set: str = typer.Option(
        "default", "--template-set", help="Template-set to initialise with"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="LLM provider slug for the project"
    ),
    with_doe: bool = typer.Option(
        False, "--with-doe", help="Also create a DOE specification stub"
    ),
    with_eval_stub: bool = typer.Option(
        False, "--with-eval-stub", help="Add an evaluation harness"
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
    git_remote: str = typer.Option(
        None, "--git-remote", help="Initial Git remote URL"
    ),
    filter_uri: str = typer.Option(
        None, "--filter-uri", help="Configure git filter with this URI"
    ),
):
    """Create a new Peagen project skeleton locally."""
    self = Logger(name="init_project")
    self.logger.info("Entering local init_project command")
    args: Dict[str, Any] = {
        "kind": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
        "git_remote": git_remote,
        "filter_uri": filter_uri,
    }

    result = _call_handler(args)
    _summary(path, result["next"])
    if filter_uri:
        add_filter(filter_uri, config=path / ".peagen.toml")
    self.logger.info("Exiting local init_project command")


@remote_init_app.command("project")
def remote_init_project(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", exists=False, dir_okay=True, file_okay=False, help="Target directory"
    ),
    template_set: str = typer.Option(
        "default", "--template-set", help="Template-set to initialise with"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="LLM provider slug for the project"
    ),
    with_doe: bool = typer.Option(
        False, "--with-doe", help="Also create a DOE specification stub"
    ),
    with_eval_stub: bool = typer.Option(
        False, "--with-eval-stub", help="Add an evaluation harness"
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
    git_remote: str = typer.Option(
        None, "--git-remote", help="Initial Git remote URL"
    ),
    filter_uri: str = typer.Option(
        None, "--filter-uri", help="Configure git filter with this URI"
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """Submit a project scaffold task via JSON-RPC."""
    args = {
        "kind": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
        "git_remote": git_remote,
        "filter_uri": filter_uri,
    }
    _submit_task(args, gateway_url, "init project")


# ── init template-set ────────────────────────────────────────────────────────
@local_init_app.command("template-set")
def local_init_template_set(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Location for the new package"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="Template-set identifier"
    ),
    org: Optional[str] = typer.Option(
        None, "--org", help="Organisation or namespace"
    ),
    use_uv: bool = typer.Option(
        True, "--uv/--no-uv", help="Use uv for installing dependencies"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
    ),
):
    """Create a template-set wheel skeleton locally."""
    self = Logger(name="init_template_set")
    self.logger.info("Entering local init_template_set command")
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
    self.logger.info("Exiting local init_template_set command")


@remote_init_app.command("template-set")
def remote_init_template_set(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Location for the new package"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="Template-set identifier"
    ),
    org: Optional[str] = typer.Option(
        None, "--org", help="Organisation or namespace"
    ),
    use_uv: bool = typer.Option(
        True, "--uv/--no-uv", help="Use uv for installing dependencies"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """Submit a template-set scaffold task via JSON-RPC."""
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
@local_init_app.command("doe-spec")
def local_init_doe_spec(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Directory for the spec"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="DOE spec identifier"
    ),
    org: Optional[str] = typer.Option(
        None, "--org", help="Organisation or namespace"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
    ),
):
    """Create a DOE-spec stub locally."""
    self = Logger(name="init_doe_spec")
    self.logger.info("Entering local init_doe_spec command")
    args: Dict[str, Any] = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    result = _call_handler(args)
    _summary(path, result["next"])
    self.logger.info("Exiting local init_doe_spec command")


@remote_init_app.command("doe-spec")
def remote_init_doe_spec(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Directory for the spec"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="DOE spec identifier"
    ),
    org: Optional[str] = typer.Option(
        None, "--org", help="Organisation or namespace"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """Submit a DOE-spec scaffold task via JSON-RPC."""
    args = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    _submit_task(args, gateway_url, "init doe-spec")


# ── init ci ─────────────────────────────────────────────────────────────────
@local_init_app.command("ci")
def local_init_ci(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Directory for the CI file"
    ),
    github: bool = typer.Option(
        True, "--github/--gitlab", help="Generate config for GitHub or GitLab"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
    ),
):
    """Drop a CI pipeline file for GitHub or GitLab locally."""
    self = Logger(name="init_ci")
    self.logger.info("Entering local init_ci command")
    args: Dict[str, Any] = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    _call_handler(args)
    typer.echo("✅  CI file written.  Commit it to enable automatic runs.")
    self.logger.info("Exiting local init_ci command")


@remote_init_app.command("ci")
def remote_init_ci(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Directory for the CI file"
    ),
    github: bool = typer.Option(
        True, "--github/--gitlab", help="Generate config for GitHub or GitLab"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """Submit a CI pipeline scaffold task via JSON-RPC."""
    args = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    _submit_task(args, gateway_url, "init ci")
