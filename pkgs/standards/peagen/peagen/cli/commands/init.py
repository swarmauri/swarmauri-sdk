# peagen/commands/init.py
"""
peagen init – scaffolding helpers for every first-class artefact.

The real templates live in:
    peagen/scaffolding/
        ├── project/
        ├── template-set/
        ├── doe-spec/
        └── ci/

Each folder may contain plain files or Jinja-2 templates
(`*.j2`).  Placeholders are rendered with the `context`
dict passed to `_render_scaffold`.
"""

from __future__ import annotations

import shutil
import textwrap
from pathlib import Path
from typing import Optional
from swarmauri_standard.loggers.Logger import Logger

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from peagen.plugins import registry

# ── Typer root ───────────────────────────────────────────────────────────────
local_init_app = typer.Typer(help="Bootstrap Peagen artefacts (project, template-set …)")



# ── utilities ────────────────────────────────────────────────────────────────
def _ensure_empty_or_force(dst: Path, force: bool) -> None:
    if dst.exists() and any(dst.iterdir()) and not force:
        typer.echo(f"❌  Directory '{dst}' is not empty.  Use --force to overwrite.")
        raise typer.Exit(code=1)
    dst.mkdir(parents=True, exist_ok=True)


def _render_scaffold(kind: str, dst: Path, context: dict, force: bool) -> None:
    src_root = kind
    if not src_root.exists():
        typer.echo(f"❌  Internal error: scaffold folder '{kind}' missing.")
        raise typer.Exit(code=1)

    _ensure_empty_or_force(dst, force)

    env = Environment(
        loader=FileSystemLoader(str(src_root)),
        autoescape=select_autoescape,
        keep_trailing_newline=True,
    )

    # ------------------------------------------------------------------------
    for path in src_root.rglob("*"):
        rel = path.relative_to(src_root)

        # 1️⃣  Render *every* path segment (enables {{ var }} in folder names)
        rendered_parts = [Template(part).render(**context) for part in rel.parts]
        target = dst.joinpath(*rendered_parts)

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        # 2️⃣  File handling
        if path.suffix == ".j2":
            template_key = rel.as_posix()  # POSIX path for Jinja
            template = env.get_template(template_key)

            target = target.with_suffix("")  # strip .j2
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(template.render(**context), encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )


# ── init project ─────────────────────────────────────────────────────────────
@local_init_app.command("project", help="Create a new Peagen project skeleton.")
def init_project(
    ctx: typer.Context,
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
    context = {
        "PROJECT_ROOT": project_root,
        "template_set": template_set,
        "provider": provider or "",
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "peagen_version": "0.0.0",  # optionally inject via importlib.metadata
    }

    _render_scaffold("project", path, context, force)
    _summary(path, "peagen process")
    self.logger.info("Exiting init_project command")


# ── init template-set ────────────────────────────────────────────────────────
@local_init_app.command("template-set", help="Create a template-set wheel skeleton.")
def init_template_set(
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set ID."),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_template_set")
    self.logger.info("Entering init_template_set command")
    self.logger.info(name)
    tmpl_mod = registry["template_sets"].get("init-template-set")
    if tmpl_mod is None:
        typer.echo("❌  Template-set 'init-template-set' not found.")
        raise typer.Exit(code=1)

    src_root = Path(list(tmpl_mod.__path__)[0])
    self.logger.info(src_root)

    context = {
        "PROJECT_ROOT": name,
        "org": org or "org",
        "use_uv": use_uv,
    }


    _render_scaffold(src_root, path, context, force)
    _summary(path, f"peagen template-sets add {path}")
    self.logger.info("Exiting init_template_set command")


# ── init doe-spec ────────────────────────────────────────────────────────────
@local_init_app.command("doe-spec", help="Create a DOE-spec stub.")
def init_doe_spec(
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_doe_spec")
    self.logger.info("Entering init_doe_spec command")
    context = {
        "spec_name": name or path.name,
        "org": org or "org",
        "version": "v1",
    }
    _render_scaffold("doe_spec", path, context, force)
    _summary(path, "peagen experiment --spec ... --template project.yaml")
    self.logger.info("Exiting init_doe_spec command")


# ── init ci ─────────────────────────────────────────────────────────────────
@local_init_app.command("ci", help="Drop a CI pipeline file for GitHub or GitLab.")
def init_ci(
    ctx: typer.Context,
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
):
    self = Logger(name="init_ci")
    self.logger.info("Entering init_ci command")
    kind = "ci-github" if github else "ci-gitlab"
    dst = Path(".")
    _render_scaffold("ci/" + kind, dst, {}, force)
    typer.echo("✅  CI file written.  Commit it to enable automatic runs.")
    self.logger.info("Exiting init_ci command")
