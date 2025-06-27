# peagen/commands/init.py
"""
peagen init – scaffolding helpers for every first-class artefact.

Templates are rendered via :mod:`peagen.core.init_core` and can be
provided by entry-point plugins registered under ``peagen.template_sets``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, List

import typer

from peagen._utils._init import _call_handler, _submit_task, _summary
from peagen.errors import PATNotAllowedError
from peagen._utils.git_filter import add_filter, init_git_filter
from swarmauri_standard.loggers.Logger import Logger


def _parse_remotes(values: Optional[List[str]]) -> Dict[str, str]:
    """Return a name→url mapping from ``--git-remote`` options."""
    remotes: Dict[str, str] = {}
    if not values:
        return remotes
    for idx, item in enumerate(values):
        if "=" in item:
            name, url = item.split("=", 1)
        else:
            name = "origin" if idx == 0 else "upstream" if idx == 1 else f"r{idx}"
            url = item
        remotes[name] = url
    return remotes


# ── Typer root ───────────────────────────────────────────────────────────────
local_init_app = typer.Typer(
    help="Bootstrap Peagen artefacts (project, template-set …) locally"
)
remote_init_app = typer.Typer(
    help="Bootstrap Peagen artefacts (project, template-set …) via JSON-RPC",
)


@local_init_app.command("filter")
def local_init_filter(
    uri: str | None = None,
    name: str = "default",
    config: Path = Path(".peagen.toml"),
    repo: Path = Path("."),
    add_config: bool = typer.Option(
        False, "--add-config", help="Write filter settings to config"
    ),
) -> None:
    """Configure *repo* with a git filter.

    If *uri* is omitted, ``s3://peagen`` is used. Use ``--add-config`` to update
    ``config`` with the filter entry.
    """
    init_git_filter(repo, uri, name=name)
    if add_config:
        add_filter(uri, name=name, config=config)
        typer.echo(f"Configured filter '{name}' -> {uri or 's3://peagen'} in {config}")
    else:
        typer.echo(f"Configured filter '{name}' -> {uri or 's3://peagen'}")


@local_init_app.command("repo")
def local_init_repo(
    repo: str = typer.Argument(..., help="tenant/repo"),
    pat: str = typer.Option(..., envvar="GITHUB_PAT", help="GitHub PAT"),
    description: str = typer.Option("", help="Repository description"),
    deploy_key: Path = typer.Option(None, "--deploy-key", help="Existing private key"),
    path: Path = typer.Option(None, "--path", help="Existing repository to configure"),
    origin: str = typer.Option(None, "--origin", help="Origin remote URL"),
    upstream: str = typer.Option(None, "--upstream", help="Upstream remote URL"),
) -> None:
    """Create a GitHub repository and register a deploy key."""
    self = Logger(name="init_repo")
    self.logger.info("Entering local init_repo command")
    args: Dict[str, Any] = {
        "kind": "repo",
        "repo": repo,
        "pat": pat,
        "description": description,
        "deploy_key": str(deploy_key) if deploy_key else None,
    }
    if path is not None:
        args["path"] = str(path)
    if origin or upstream:
        remotes: Dict[str, str] = {}
        if origin:
            remotes["origin"] = origin
        if upstream:
            remotes["upstream"] = upstream
        args["remotes"] = remotes
    result = _call_handler(args)
    _summary(Path("."), result["next"])
    self.logger.info("Exiting local init_repo command")


@local_init_app.command("repo-config")
def local_init_repo_config(
    path: Path = Path("."),
    git_remote: Optional[List[str]] = typer.Option(
        None,
        "--git-remote",
        help="Git remote in name=url format. Use multiple times for several remotes",
        multiple=True,
    ),
) -> None:
    """Configure Git remotes for an existing repository."""
    self = Logger(name="init_repo_config")
    self.logger.info("Entering local init_repo_config command")
    args: Dict[str, Any] = {
        "kind": "repo-config",
        "path": str(path),
        "remotes": _parse_remotes(git_remote),
    }
    _call_handler(args)
    _summary(path, "git remotes configured")
    self.logger.info("Exiting local init_repo_config command")


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
    git_remote: Optional[List[str]] = typer.Option(
        None,
        "--git-remote",
        help="Git remote in name=url format. Use multiple times for several remotes",
        multiple=True,
    ),
    filter_uri: str = typer.Option(
        None, "--filter-uri", help="Configure git filter with this URI"
    ),
    add_filter_config: bool = typer.Option(
        False,
        "--add-filter-config",
        help="Also record filter in .peagen.toml",
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
        "git_remotes": _parse_remotes(git_remote),
        "filter_uri": filter_uri,
        "add_filter_config": add_filter_config,
    }

    result = _call_handler(args)
    _summary(path, result["next"])
    if filter_uri and add_filter_config:
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
    git_remote: Optional[List[str]] = typer.Option(
        None,
        "--git-remote",
        help="Git remote in name=url format. Use multiple times for several remotes",
        multiple=True,
    ),
    filter_uri: str = typer.Option(
        None, "--filter-uri", help="Configure git filter with this URI"
    ),
    add_filter_config: bool = typer.Option(
        False, "--add-filter-config", help="Also record filter in .peagen.toml"
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
        "git_remotes": _parse_remotes(git_remote),
        "filter_uri": filter_uri,
    }
    try:
        _submit_task(args, ctx.obj.get("gateway_url"), "init project")
    except PATNotAllowedError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@remote_init_app.command("repo-config")
def remote_init_repo_config(
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    git_remote: Optional[List[str]] = typer.Option(
        None,
        "--git-remote",
        help="Git remote in name=url format. Use multiple times for several remotes",
        multiple=True,
    ),
) -> None:
    """Submit a repo configuration task via JSON-RPC."""
    args = {
        "kind": "repo-config",
        "path": str(path),
        "remotes": _parse_remotes(git_remote),
    }
    try:
        _submit_task(args, ctx.obj.get("gateway_url"), "init repo-config")
    except PATNotAllowedError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


# ── init template-set ────────────────────────────────────────────────────────
@local_init_app.command("template-set")
def local_init_template_set(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Location for the new package"
    ),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set identifier"),
    org: Optional[str] = typer.Option(None, "--org", help="Organisation or namespace"),
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
    name: Optional[str] = typer.Option(None, "--name", help="Template-set identifier"),
    org: Optional[str] = typer.Option(None, "--org", help="Organisation or namespace"),
    use_uv: bool = typer.Option(
        True, "--uv/--no-uv", help="Use uv for installing dependencies"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
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
    try:
        _submit_task(args, ctx.obj.get("gateway_url"), "init template-set")
    except PATNotAllowedError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


# ── init doe-spec ────────────────────────────────────────────────────────────
@local_init_app.command("doe-spec")
def local_init_doe_spec(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".", dir_okay=True, file_okay=False, help="Directory for the spec"
    ),
    name: Optional[str] = typer.Option(None, "--name", help="DOE spec identifier"),
    org: Optional[str] = typer.Option(None, "--org", help="Organisation or namespace"),
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
    name: Optional[str] = typer.Option(None, "--name", help="DOE spec identifier"),
    org: Optional[str] = typer.Option(None, "--org", help="Organisation or namespace"),
    force: bool = typer.Option(
        False, "--force", help="Overwrite destination if not empty"
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
    try:
        _submit_task(args, ctx.obj.get("gateway_url"), "init doe-spec")
    except PATNotAllowedError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


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
):
    """Submit a CI pipeline scaffold task via JSON-RPC."""
    args = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    try:
        _submit_task(args, ctx.obj.get("gateway_url"), "init ci")
    except PATNotAllowedError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@remote_init_app.command("repo")
def remote_init_repo(
    ctx: typer.Context,
    repo: str = typer.Argument(..., help="tenant/repo"),
    pat: str = typer.Option(..., envvar="GITHUB_PAT", help="GitHub PAT"),
    description: str = typer.Option("", help="Repository description"),
    deploy_key: Path = typer.Option(None, "--deploy-key", help="Existing private key"),
    path: Path = typer.Option(None, "--path", help="Existing repository to configure"),
    origin: str = typer.Option(None, "--origin", help="Origin remote URL"),
    upstream: str = typer.Option(None, "--upstream", help="Upstream remote URL"),
) -> None:
    """Create a GitHub repository via JSON-RPC."""
    args = {
        "kind": "repo",
        "repo": repo,
        "pat": pat,
        "description": description,
        "deploy_key": str(deploy_key) if deploy_key else None,
    }
    if path is not None:
        args["path"] = str(path)
    if origin or upstream:
        remotes: Dict[str, str] = {}
        if origin:
            remotes["origin"] = origin
        if upstream:
            remotes["upstream"] = upstream
        args["remotes"] = remotes
    try:
        _submit_task(args, ctx.obj.get("gateway_url"), "init repo", allow_pat=True)
    except PATNotAllowedError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
