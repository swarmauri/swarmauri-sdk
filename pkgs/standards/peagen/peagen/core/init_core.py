"""peagen.core.init_core
=======================

Business logic for initializing Peagen scaffolds.

This module exposes helper functions that write project skeletons
and other artefacts without any CLI dependencies.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from github import Github

from peagen.core.git_repo_core import open_repo

from peagen.plugins import (
    PluginManager,
    discover_and_register_plugins,
    registry,
)
from peagen._utils.config_loader import resolve_cfg
from peagen.core.doe_core import _sha256


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_empty_or_force(dst: Path, force: bool) -> None:
    """Create *dst* if empty or *force* is True."""
    if dst.exists() and any(dst.iterdir()) and not force:
        raise FileExistsError(f"Directory '{dst}' is not empty.")
    dst.mkdir(parents=True, exist_ok=True)


def _render_scaffold(
    src_root: Path, dst: Path, context: Dict[str, Any], force: bool
) -> None:
    """Render a scaffold tree from *src_root* into *dst* using *context*."""
    if not src_root.exists():
        raise FileNotFoundError(f"Scaffold folder '{src_root}' missing.")

    _ensure_empty_or_force(dst, force)

    env = Environment(
        loader=FileSystemLoader(str(src_root)),
        autoescape=select_autoescape,
        keep_trailing_newline=True,
    )

    for path in src_root.rglob("*"):
        rel = path.relative_to(src_root)
        rendered_parts = [Template(part).render(**context) for part in rel.parts]
        target = dst.joinpath(*rendered_parts)

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        if path.suffix == ".j2":
            template_key = rel.as_posix()
            template = env.get_template(template_key)
            target = target.with_suffix("")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(template.render(**context), encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def init_project(
    *,
    path: Path,
    force: bool = False,
    git_remotes: dict[str, str] | None = None,
    filter_uri: str | None = None,
    add_filter_config: bool = False,
) -> Dict[str, Any]:
    """Create a new Peagen project skeleton."""
    tmpl_mod = registry["template_sets"].get("init-project")
    if tmpl_mod is None:
        raise ValueError("Template-set 'init-project' not found.")

    src_root = Path(list(tmpl_mod.__path__)[0])
    project_root = path.name
    context = {
        "PROJECT_ROOT": project_root,
        "peagen_version": "0.0.0",
    }

    _render_scaffold(src_root, path, context, force)

    pm = PluginManager({})
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        vcs = None
    if vcs:
        vcs.commit(["."], "initial commit")

    if filter_uri:
        from peagen._utils.git_filter import add_filter, init_git_filter

        init_git_filter(vcs.repo, filter_uri)
        if add_filter_config:
            add_filter(filter_uri, config=path / ".peagen.toml")

    return {"created": str(path), "next": "peagen process"}


def init_template_set(
    *,
    path: Path,
    name: Optional[str] = None,
    org: Optional[str] = None,
    use_uv: bool = True,
    force: bool = False,
) -> Dict[str, Any]:
    """Create a template-set wheel skeleton."""
    tmpl_mod = registry["template_sets"].get("init-template-set")
    if tmpl_mod is None:
        raise ValueError("Template-set 'init-template-set' not found.")

    src_root = Path(list(tmpl_mod.__path__)[0])
    context = {
        "PROJECT_ROOT": name,
        "org": org or "org",
        "use_uv": use_uv,
    }

    _render_scaffold(src_root, path, context, force)
    return {"created": str(path), "next": f"peagen template-sets add {path}"}


def init_doe_spec(
    *,
    path: Path,
    name: Optional[str] = None,
    org: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """Create a DOE-spec stub."""
    discover_and_register_plugins()
    tmpl_mod = registry["template_sets"].get("init-doe-spec")
    if tmpl_mod is None:
        raise ValueError("Template-set 'init-doe-spec' not found.")

    src_root = Path(list(tmpl_mod.__path__)[0])
    context = {
        "spec_name": name or path.name,
        "org": org or "org",
        "version": "v1",
    }

    _render_scaffold(src_root, path, context, force)

    spec_file = path / "doe_spec.yml"
    checksum = _sha256(spec_file)
    meta_file = path / "spec.yaml"
    if meta_file.exists():
        import yaml

        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
        meta["checksum"] = checksum
        meta_file.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")

    return {
        "created": str(path),
        "next": "peagen experiment --spec ... --template project.yaml",
    }


def init_ci(
    *,
    path: Path,
    github: bool = True,
    force: bool = False,
) -> Dict[str, Any]:
    """Drop a CI pipeline file for GitHub or GitLab."""
    tmpl_mod = registry["template_sets"].get("init-ci")
    if tmpl_mod is None:
        raise ValueError("Template-set 'init-ci' not found.")

    src_root = Path(list(tmpl_mod.__path__)[0])
    kind = "ci-github" if github else "ci-gitlab"
    _render_scaffold(src_root / kind, path, {}, force)
    return {"created": str(path), "next": "commit the CI file"}


def init_repo(
    *,
    repo: str,
    pat: str,
    description: str = "",
    deploy_key: Path | None = None,
    path: Path | None = None,
    remotes: dict[str, str] | None = None,
) -> Dict[str, Any]:
    """Create a GitHub repository and optionally configure a local repo."""
    import subprocess
    import tempfile

    principal, name = repo.split("/", 1)
    gh = Github(pat)

    try:
        owner = gh.get_organization(principal)
    except Exception:
        auth_user = gh.get_user()
        if auth_user.login.lower() == principal.lower():
            owner = auth_user
        else:
            owner = gh.get_user(principal)

    try:
        repo_obj = owner.create_repo(name, private=True, description=description)
    except Exception:
        repo_obj = gh.get_repo(repo)

    if deploy_key is None:
        tmp = Path(tempfile.mkdtemp())
        deploy_key = tmp / f"{name}_deploy"
        subprocess.run(
            [
                "ssh-keygen",
                "-q",
                "-t",
                "ed25519",
                "-N",
                "",
                "-C",
                f"{name}-worker",
                "-f",
                str(deploy_key),
            ],
            check=True,
        )

    pub_key = deploy_key.with_suffix(".pub")
    with pub_key.open() as fh:
        repo_obj.create_key(title="peagen-worker", key=fh.read(), read_only=False)

    result = {
        "created": repo,
        "deploy_key": str(deploy_key),
        "next": "configure DEPLOY_KEY_SECRET",
    }

    if path is None:
        path = Path(".")

    final_remotes = remotes.copy() if remotes else {}
    if not remotes:
        from peagen.defaults import (
            GIT_SHADOW_BASE,
        )  # update this such that the server uses their runtime_cfg

        shadow = GIT_SHADOW_BASE.rstrip("/")
        final_remotes["origin"] = f"{shadow}/{principal}/{name}.git"
        final_remotes["upstream"] = repo_obj.ssh_url
    else:
        final_remotes.setdefault("origin", repo_obj.ssh_url)
    configure_repo(path=path, remotes=final_remotes)
    vcs = open_repo(path, remotes=final_remotes)
    for remote_name in final_remotes:
        vcs.push("HEAD", remote=remote_name)

    result.update({"configured": str(path), "remotes": final_remotes})
    return result


def configure_repo(*, path: Path, remotes: dict[str, str]) -> Dict[str, Any]:
    """Configure an existing repository with additional remotes."""
    cfg = resolve_cfg()
    vcs_cfg = cfg.setdefault("vcs", {})
    adapters = vcs_cfg.setdefault("adapters", {})
    default = vcs_cfg.get("default_vcs", "git")
    adapter_cfg = adapters.setdefault(default, {})
    adapter_cfg["path"] = str(path)
    if remotes:
        adapter_cfg.setdefault("remotes", {})
        adapter_cfg["remotes"].update(remotes)
    pm = PluginManager(cfg)
    pm.get("vcs", default)
    return {"configured": str(path), "remotes": remotes}
