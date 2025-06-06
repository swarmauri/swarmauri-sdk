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

from peagen.plugins import registry


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_empty_or_force(dst: Path, force: bool) -> None:
    """Create *dst* if empty or *force* is True."""
    if dst.exists() and any(dst.iterdir()) and not force:
        raise FileExistsError(f"Directory '{dst}' is not empty.")
    dst.mkdir(parents=True, exist_ok=True)


def _render_scaffold(src_root: Path, dst: Path, context: Dict[str, Any], force: bool) -> None:
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
    template_set: str = "default",
    provider: Optional[str] = None,
    with_doe: bool = False,
    with_eval_stub: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """Create a new Peagen project skeleton."""
    tmpl_mod = registry["template_sets"].get("init-project")
    if tmpl_mod is None:
        raise ValueError("Template-set 'init-project' not found.")

    src_root = Path(list(tmpl_mod.__path__)[0])
    project_root = path.name
    context = {
        "PROJECT_ROOT": project_root,
        "template_set": template_set,
        "provider": provider or "",
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "peagen_version": "0.0.0",
    }

    _render_scaffold(src_root, path, context, force)
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
    return {"created": str(path), "next": "peagen experiment --spec ... --template project.yaml"}


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
