# peagen/cli/commands/init.py
"""
peagen init – scaffolding helpers for every first-class artefact.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional, List

import typer
from swarmauri_standard.loggers.Logger import Logger
from autoapi.v2 import AutoAPI

from peagen._utils._init import _call_handler, _summary
from peagen._utils.git_filter import add_filter, init_git_filter
from peagen.cli.task_helpers import build_task, submit_task
from peagen.errors import PATNotAllowedError
from peagen.defaults import (
    DEFAULT_POOL_ID,
    DEFAULT_SUPER_USER_ID,
    DEFAULT_TENANT_ID,
)
from peagen.orm import Repository


# --------------------------------------------------------------------- helpers
def _parse_remotes(values: Optional[List[str]]) -> Dict[str, str]:
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
    help="Bootstrap Peagen artifacts (project, template-set …) locally"
)
remote_init_app = typer.Typer(
    help="Bootstrap Peagen artifacts (project, template-set …) via JSON-RPC",
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
    path: Path = typer.Option(
        Path("."), "--path", help="Existing repository to configure"
    ),
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
        "path": str(path),
    }
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
    force: bool = typer.Option(False, "--force", help="Overwrite if dir not empty."),
    git_remote: Optional[List[str]] = typer.Option(
        None,
        "--git-remote",
        help="Git remote in name=url format. Use multiple times for several remotes",
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


# ───────────────────────────── LOCAL COMMANDS (unchanged) ────────────────────
#   … all local_* functions stay exactly the same – they call _call_handler …
#   (see end of file for unchanged local implementations)


# ───────────────────────────── REMOTE HELPERS ───────────────────────────────
def _remote_task(
    action: str,
    args: Dict[str, Any],
    ctx: typer.Context,
    repo: str,
    ref: str,
):
    """Build & submit a remote init Task, handling PAT errors nicely."""
    task = build_task(
        action=action,
        args=args,
        tenant_id=str(DEFAULT_TENANT_ID),
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )
    reply = submit_task(ctx.obj["rpc"], task)
    if "error" in reply:
        raise PATNotAllowedError(reply["error"]["message"])


# --------------------------------------------------------------------- REMOTE COMMANDS
@remote_init_app.command("project")
def remote_init_project(  # noqa: PLR0913
    ctx: typer.Context,
    path: Path = typer.Argument(".", exists=False),
    force: bool = typer.Option(False, "--force"),
    git_remote: Optional[List[str]] = typer.Option(None, "--git-remote"),
    filter_uri: str = typer.Option(None, "--filter-uri"),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref"),
):
    """Submit a project scaffold task via JSON-RPC."""
    args = {
        "kind": "project",
        "path": str(path),
        "force": force,
        "git_remotes": _parse_remotes(git_remote),
        "filter_uri": filter_uri,
    }
    _remote_task("init", args, ctx, repo, ref)


@remote_init_app.command("repo-config")
def remote_init_repo_config(  # noqa: PLR0913
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    git_remote: Optional[List[str]] = typer.Option(None, "--git-remote"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
):
    args = {
        "kind": "repo-config",
        "path": str(path),
        "remotes": _parse_remotes(git_remote),
    }
    _remote_task("init", args, ctx, repo, ref)


@remote_init_app.command("template-set")
def remote_init_template_set(  # noqa: PLR0913
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
):
    args = {
        "kind": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    _remote_task("init", args, ctx, repo, ref)


@remote_init_app.command("doe-spec")
def remote_init_doe_spec(  # noqa: PLR0913
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
):
    args = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    _remote_task("init", args, ctx, repo, ref)


@remote_init_app.command("ci")
def remote_init_ci(  # noqa: PLR0913
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
):
    args = {
        "kind": "ci",
        "path": str(path),
        "github": github,
        "force": force,
    }
    _remote_task("init", args, ctx, repo, ref)


@remote_init_app.command("repo")
def remote_init_repo(
    ctx: typer.Context,
    repo_slug: str = typer.Argument(..., help="tenant/repo"),
    url: str = typer.Option(None, "--url", help="Repository URL"),
    default_branch: str = typer.Option("main", "--default-branch"),
    remote_name: str = typer.Option("origin", "--remote-name"),
) -> None:
    """Register *repo_slug* with the gateway via JSON-RPC."""
    self = Logger(name="init_repo")
    self.logger.info("Entering remote init_repo command")
    try:
        tenant, name = repo_slug.split("/", 1)
    except ValueError:
        typer.echo("❌  repo must be in 'tenant/name' format", err=True)
        raise typer.Exit(1)
    repo_url = url or f"https://github.com/{tenant}/{name}"
    SCreate = AutoAPI.get_schema(Repository, "create")
    SRead = AutoAPI.get_schema(Repository, "read")
    params = SCreate(
        name=name,
        url=repo_url,
        default_branch=default_branch,
        remote_name=remote_name,
        tenant_id=str(DEFAULT_TENANT_ID),
        owner_id=str(DEFAULT_SUPER_USER_ID),
        status="queued",
    )
    rpc = ctx.obj["rpc"]
    try:
        res = rpc.call("Repositories.create", params=params, out_schema=SRead)
        typer.echo(f"✅  registered repository '{res.name}' ({res.url})")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)
    self.logger.info("Exiting remote init_repo command")
