# peagen/commands/program.py
"""
`peagen program` – workspace manipulation & utilities.

Sub-commands
------------
fetch    : reconstruct a workspace from one or more v3 manifests
patch    : overlay a second workspace or program_apply JSON-Patch files
inspect  : show tree / LOC / manifest info
diff     : file-level diff between two workspaces or manifests
validate : schema + license compliance checks
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse, urlunparse
import hashlib
import jsonpatch

import typer
from jsonschema import ValidationError, validate as json_validate
from rich import print as rprint
from rich.tree import Tree

from peagen._source_packages import _materialise_source_pkg
from peagen.schemas import MANIFEST_V3_SCHEMA  # JSON-Schema dict
from peagen.storage_adapters import make_adapter_for_uri
from swarmauri_standard.loggers.Logger import Logger

program_app = typer.Typer(
    name="program",
    help="Reconstruct, patch, inspect, diff, and validate Peagen workspaces.",
    no_args_is_help=True,
)


# ───────────────────────────────────────── helper ──────────────────────────
def _install_template_sets(specs: List[dict], base_dir: Optional[Path] = None) -> None:
    """
    Install template-sets declared in a manifest.

    Supports Git repositories (`type: git`) and PyPI packages (`type: pip`).

    Args:
        specs: List of template-set specification dictionaries.
        base_dir: Directory where Git template-sets are cloned.
                  Defaults to ~/.peagen/template_sets
    """
    base_dir = base_dir or (Path.home() / ".peagen" / "template_sets")
    base_dir.mkdir(parents=True, exist_ok=True)

    for spec in specs:
        kind = spec.get("type", "git")
        if kind == "git":
            dest = base_dir / spec["name"]
            if dest.exists():
                continue  # already present
            repo = spec["uri"]
            subprocess.check_call(["git", "clone", "--depth", "1", repo, str(dest)])
            if ref := spec.get("ref"):
                subprocess.check_call(["git", "-C", str(dest), "checkout", ref])
        elif kind == "pip":
            pkg = spec["uri"]
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        else:
            raise ValueError(f"Unknown template-set type: {kind}")


# ───────────────────────────────────────────────────────────── fetch ──
@program_app.command()
def fetch(
    manifests: List[str] = typer.Argument(..., help="Manifest JSON URI(s)"),
    out_dir: Path = typer.Option(
        None, "--out", "-o", help="Destination folder (temp dir if omitted)"
    ),
    no_source: bool = typer.Option(
        False, help="Skip cloning/copying `source_packages` (debug only)"
    ),
    install_template_sets_flag: bool = typer.Option(
        True,
        "--install-template-sets/--no-install-template-sets",
        help="Install template sets before fetching",
    ),
):
    """
    Reconstruct a complete workspace from manifest(s).
    """
    self = Logger(name="fetch")
    self.logger.info("Entering fetch command")
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp(prefix="peagen_ws_")).resolve()
    else:
        out_dir = out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

    for m_uri in manifests:
        manifest = _download_manifest(m_uri)

        if install_template_sets_flag and manifest.get("template_sets"):
            _install_template_sets(manifest["template_sets"])

        if not no_source:
            for spec in manifest["source_packages"]:
                _materialise_source_pkg(spec, out_dir, upload=False)

        _materialise_workspace(manifest, out_dir)

    typer.echo(f"workspace: {out_dir}")
    self.logger.info("Exiting fetch command")


# ───────────────────────────────────────────────────────────── patch ──
@program_app.command()
def patch(
    workspace: Path = typer.Argument(..., exists=True),
    overlay: Optional[Path] = typer.Option(
        None, help="Second workspace whose files overlay the first."
    ),
    patch: Optional[Path] = typer.Option(
        None, help="RFC-6902 JSON-Patch file to program_apply."
    ),
):
    """
    Overlay another workspace and/or program_apply JSON-Patch in-place.
    """
    self = Logger(name="patch")
    self.logger.info("Entering patch command")
    workspace = workspace.resolve()

    if overlay:
        _overlay_dir(overlay.resolve(), workspace)
        typer.echo("overlay program_applied")

    if patch:
        doc = _tree_to_json(workspace)
        patch_ops = json.loads(patch.read_text())
        doc = jsonpatch.apply_patch(doc, patch_ops, in_place=False)
        _json_to_tree(doc, workspace)
        typer.echo("json-patch program_applied")

    self.logger.info("Exiting patch command")


# ─────────────────────────────────────────────────────────── inspect ──
@program_app.command()
def inspect(
    workspace: Path = typer.Argument(..., exists=True),
    tree: bool = typer.Option(False, help="Show directory tree"),
    loc: bool = typer.Option(False, help="Count LOC per language"),
    manifest: bool = typer.Option(False, help="Pretty-print manifest(s) found"),
):
    """
    Display information about a workspace.
    """
    self = Logger(name="inspect")
    self.logger.info("Entering inspect command")
    workspace = workspace.resolve()
    if tree:
        _print_tree(workspace)
    if loc:
        _print_loc(workspace)
    if manifest:
        for mf in (workspace / ".peagen").glob("*_manifest.json"):
            rprint(json.loads(mf.read_text()))

    self.logger.info("Exiting inspect command")


# ───────────────────────────────────────────────────────────── diff ──
@program_app.command()
def diff(
    left: Path = typer.Argument(...),
    right: Path = typer.Argument(...),
    md: Optional[Path] = typer.Option(None, help="Write Markdown diff table here"),
):
    """
    File-level diff between two workspaces OR two manifest URIs.
    """
    self = Logger(name="diff")
    self.logger.info("Entering diff command")
    left_dir = _ensure_workspace(left)
    right_dir = _ensure_workspace(right)

    added, removed, modified = _file_diff(left_dir, right_dir)

    table_md = _format_diff_md(added, removed, modified)
    if md:
        md.write_text(table_md, encoding="utf-8")
    else:
        typer.echo(table_md)

    self.logger.info("Exiting diff command")


# ─────────────────────────────────────────────────────────── validate ──
@program_app.command()
def validate(
    target: Path = typer.Argument(...),
    license_allow: List[str] = typer.Option(
        None, help="Comma-separated SPDX licenses allowed"
    ),
    license_deny: List[str] = typer.Option(
        None, help="Comma-separated SPDX licenses denied"
    ),
    schema_only: bool = typer.Option(False, help="Only run manifest JSON-Schema check"),
):
    """
    JSON-Schema + (optional) license compliance validation.
    """
    self = Logger(name="validate")
    self.logger.info("Entering validate command")
    man_paths = (
        [target]
        if target.suffix == ".json"
        else list((target / ".peagen").glob("*_manifest.json"))
    )

    for mp in man_paths:
        mf = json.loads(mp.read_text())
        try:
            json_validate(mf, MANIFEST_V3_SCHEMA)
        except ValidationError as e:
            typer.echo(f"[ERROR] {mp.name}: {e.message}")
            raise typer.Exit(1)

    typer.echo("schema ✅")

    if schema_only:
        return

    detected = _scan_licenses(target)
    if license_allow:
        bad = [lic for lic in detected if not _match_any(lic, license_allow)]
        if bad:
            typer.echo(f"[ERROR] licenses not allowed: {bad}")
            raise typer.Exit(1)
    if license_deny:
        bad = [lic for lic in detected if _match_any(lic, license_deny)]
        if bad:
            typer.echo(f"[ERROR] licenses explicitly denied: {bad}")
            raise typer.Exit(1)

    typer.echo("license ✅")
    self.logger.info("Exiting validate command")


# ───────────────────────────────────── helper implementations ──
def _download_manifest(uri: str) -> dict:
    """
    Fetch *one* manifest JSON from *uri*.

    Fix 2025-05-20: scopes the storage-adapter to the **directory
    containing** the manifest (instead of the object itself).
    """
    if "://" not in uri:  # local file
        return json.loads(pathlib.Path(uri).read_text())

    p = urlparse(uri)
    dir_path, key_name = p.path.rsplit("/", 1)
    dir_uri = urlunparse((p.scheme, p.netloc, dir_path, "", "", ""))

    adapter = make_adapter_for_uri(dir_uri)
    data = adapter.download(key_name)
    return json.load(data)


def _materialise_workspace(manifest: dict, dest: Path):
    uri = manifest["workspace_uri"]
    adapter = make_adapter_for_uri(uri)
    prefix = getattr(adapter, "_prefix", "")
    adapter.download_prefix(prefix, dest)


def _overlay_dir(src: Path, dst: Path):
    delete_list = src / ".peagen-delete"
    if delete_list.exists():
        for rel in delete_list.read_text().splitlines():
            (dst / rel).unlink(missing_ok=True)

    for path in src.rglob("*"):
        rel = path.relative_to(src)
        tgt = dst / rel
        if path.is_dir():
            tgt.mkdir(parents=True, exist_ok=True)
        else:
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, tgt)


def _tree_to_json(root: Path) -> dict:
    tree = {}
    for p in root.rglob("*"):
        if p.is_file():
            tree[str(p.relative_to(root))] = p.read_text()
    return tree


def _json_to_tree(tree: dict, root: Path):
    for rel, content in tree.items():
        fp = root / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)


def _print_tree(root: Path):
    tree = Tree(f"[bold]{root.name}")
    for path in sorted(root.rglob("*")):
        tree.add(str(path.relative_to(root)))
    rprint(tree)


def _print_loc(root: Path):
    totals = {}
    for p in root.rglob("*.*"):
        if p.is_file():
            lang = p.suffix.lstrip(".") or "noext"
            totals[lang] = totals.get(lang, 0) + len(p.read_text().splitlines())
    for lang, loc in sorted(totals.items(), key=lambda x: -x[1]):
        typer.echo(f"{loc:>6}  {lang}")


def _ensure_workspace(arg: Path) -> Path:
    if arg.is_dir():
        return arg.resolve()
    tmp = Path(tempfile.mkdtemp(prefix="peagen_diff_"))
    manifest = _download_manifest(str(arg))
    _materialise_workspace(manifest, tmp)
    for spec in manifest["source_packages"]:
        _materialise_source_pkg(spec, tmp, upload=False)
    return tmp


def _file_diff(a: Path, b: Path):
    files_a = {str(p.relative_to(a)) for p in a.rglob("*") if p.is_file()}
    files_b = {str(p.relative_to(b)) for p in b.rglob("*") if p.is_file()}
    added = sorted(files_b - files_a)
    removed = sorted(files_a - files_b)
    modified = sorted(
        f
        for f in files_a & files_b
        if hashlib.sha256((a / f).read_bytes()).digest()
        != hashlib.sha256((b / f).read_bytes()).digest()
    )
    return added, removed, modified


def _format_diff_md(added, removed, modified) -> str:
    lines = ["| Path | Change |", "|------|--------|"]
    lines += [f"| {p} | added |" for p in added]
    lines += [f"| {p} | removed |" for p in removed]
    lines += [f"| {p} | modified |" for p in modified]
    return "\n".join(lines)


def _scan_licenses(workspace: Path) -> set[str]:
    detected = set()
    for p in workspace.rglob("*"):
        if p.is_file() and p.stat().st_size < 1_000_000:
            txt = p.read_text(errors="ignore")
            if "SPDX-License-Identifier:" in txt:
                lic = txt.split("SPDX-License-Identifier:", 1)[1].split()[0]
                detected.add(lic.strip())
    return detected


def _match_any(lic: str, patterns: List[str]) -> bool:
    from fnmatch import fnmatch

    return any(fnmatch(lic, pat) for pat in patterns)


# ---------------------------------------------------------------------
if __name__ == "__main__":
    program_app()
