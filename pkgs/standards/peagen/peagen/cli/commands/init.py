# peagen/cli/commands/init.py
"""
peagen init – scaffolding helpers for every first-class artefact.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional, List

import typer
from swarmauri_standard.loggers.Logger import Logger

from peagen._utils._init import _call_handler, _summary
from peagen._utils.git_filter import add_filter, init_git_filter
from peagen.cli.task_helpers import build_task, submit_task
from peagen.errors import PATNotAllowedError
from peagen.defaults import (
    DEFAULT_POOL_ID,
    GIT_SHADOW_BASE,
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
    repo: str = typer.Argument(..., help="principal/repo"),
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
    principal, name = repo.split("/", 1)
    if origin:
        remotes["origin"] = origin
    else:
        remotes["origin"] = f"git@github.com:{principal}/{name}.git"
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
    repo: str = typer.Argument(..., help="owner/name"),
    pat: str = typer.Option(..., envvar="GITHUB_PAT"),
    path: str = typer.Option(".", "--path", help="Local repository path"),
    default_branch: str = typer.Option("main", "--default-branch"),
) -> None:
    """
    Register *repo* with the gateway (provisions origin on git-shadow and mirror on GitHub),
    then push the local repo at --path to both remotes.
    """
    self = Logger(name="init_repo")
    self.logger.info("Entering remote init_repo command")

    # Parse slug
    try:
        owner, name = repo.split("/", 1)
    except ValueError:
        typer.echo("❌  repo must be in 'owner/name' format", err=True)
        raise typer.Exit(1)

    # Remote URLs

    origin_url = f"{GIT_SHADOW_BASE.rstrip('/')}/{owner}/{name}.git"
    upstream_url = f"https://github.com/{owner}/{name}.git"

    # Build RPC params using the GitHub URL
    from autoapi.v3 import get_schema

    SCreate = get_schema(Repository, "create")
    SRead = get_schema(Repository, "read")

    params = SCreate(
        name=name,
        url=upstream_url,  # server derives owner/name from GitHub URL
        default_branch=default_branch,
        github_pat=pat,  # MUST be present; schema must not exclude it
    )

    rpc = ctx.obj["rpc"]
    try:
        res = rpc.call("Repositories.create", params=params, out_schema=SRead)
        typer.echo(f"✅  registered repository '{res.name}' ({res.url})")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌  {exc}", err=True)
        raise typer.Exit(1)

    # ---- Configure local repo and push content ----
    try:
        from peagen.core.init_core import configure_repo
        from peagen.core.git_repo_core import open_repo
    except Exception as exc:
        typer.echo(f"❌  missing VCS plumbing: {exc}", err=True)
        raise typer.Exit(1)

    # Configure remotes in the client’s workspace
    try:
        configure_repo(
            path=Path(path), remotes={"origin": origin_url, "upstream": upstream_url}
        )
    except Exception as exc:
        typer.echo(f"❌  failed configuring remotes: {exc}", err=True)
        raise typer.Exit(1)

    # Open repo and push
    try:
        vcs = open_repo(
            Path(path), remotes={"origin": origin_url, "upstream": upstream_url}
        )

        # Ensure a commit exists
        try:
            if not getattr(vcs, "has_commits", None) or not vcs.has_commits():
                vcs.commit(["."], "initial commit")
        except Exception:
            # Fallback: try to commit blindly (no-op if clean)
            try:
                vcs.commit(["."], "initial commit")
            except Exception:
                pass

        # Ensure branch
        try:
            # Common VCS adapters support checkout; ignore if already on branch
            vcs.checkout(default_branch, create=True)
        except Exception:
            pass

        # Push HEAD to both remotes
        for remote in ("origin", "upstream"):
            try:
                vcs.push("HEAD", remote=remote)
                typer.echo(f"↗️  pushed HEAD to {remote}")
            except Exception as exc:
                typer.echo(f"⚠️  push to {remote} failed: {exc}", err=True)

        typer.echo("✅  remote init complete")

    except Exception as exc:
        typer.echo(f"❌  local push stage failed: {exc}", err=True)
        raise typer.Exit(1)

    self.logger.info("Exiting remote init_repo command")
