# peagen/core/doe_core.py
"""
Business-logic for Design-of-Experiments expansion.

Public entry-point
------------------
generate_payload()  – build a DOE-expanded project-payload bundle
"""

from __future__ import annotations

import hashlib
import itertools
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json

import jsonpatch
from peagen.core.patch_core import apply_patch
from peagen.core.eval_core import evaluate_workspace
import yaml
from jinja2 import Template
from urllib.parse import urlparse

from peagen._utils.config_loader import load_peagen_toml
from peagen.plugin_manager import resolve_plugin_spec
from peagen.errors import (
    PatchTargetMissingError,
    SpecFileNotFoundError,
    TemplateFileNotFoundError,
)
from peagen.jsonschemas import DOE_SPEC_V2_SCHEMA
from peagen.plugins.vcs import pea_ref
from peagen._utils._validation import _validate

# ─────────────────────────────── util ──────────────────────────────────────
_LLM_FALLBACK_KEYS = {
    "provider",
    "model",
    "temperature",
    "max_tokens",
    "max_context_tokens",
    "top_p",
    "frequency_penalty",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_yaml(uri: str | Path, *, kind: str | None = None) -> Dict[str, Any]:
    path = Path(uri).expanduser()
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        if kind == "spec":
            raise SpecFileNotFoundError(str(path)) from exc
        if kind == "template":
            raise TemplateFileNotFoundError(str(path)) from exc
        raise


def _apply_json_patch(doc: Dict, patch_ops: List[Dict]) -> Dict:
    """Apply JSON patch operations and raise a custom error on failure."""
    try:
        return jsonpatch.apply_patch(doc, patch_ops, in_place=False)
    except (jsonpatch.JsonPatchConflict, jsonpatch.JsonPointerException) as exc:
        raise PatchTargetMissingError(str(exc)) from exc


def _ctx_lookup(expr: str, ctx: Dict[str, Any]) -> Any:
    val = ctx
    for part in expr.split("."):
        val = val[part]
    return val


# ─────────────────────── factor / matrix helpers ───────────────────────────
def _matrix(factor_map: Dict[str, Any]) -> List[Tuple[Tuple[str, Any], ...]]:
    """
    Convert a rich or legacy *factor_map* into a cartesian matrix.

    Rich format:
        {"temperature": {"levels":[0.2,0.7], "code":"T"}, ...}
    Legacy format:
        {"temperature": [0.2,0.7], ...}
    """
    if not factor_map:
        return [()]

    lists: List[List[Tuple[str, Any]]] = []
    for name, spec in factor_map.items():
        if isinstance(spec, dict) and "levels" in spec:
            levels = spec["levels"]
            key = spec.get("code", name)
        else:
            levels = spec
            key = name
        lists.append([(key, lv) for lv in levels])

    return list(itertools.product(*lists))


# New DOE v2 helpers
def _matrix_v2(factors: List[dict[str, Any]]) -> List[dict[str, str]]:
    if not factors:
        return [{}]
    lists = []
    for fac in factors:
        pairs = [(fac["name"], lv["id"]) for lv in fac.get("levels", [])]
        lists.append(pairs)
    return [dict(p) for p in itertools.product(*lists)]


def _factor_index(factors: List[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    idx = {}
    for fac in factors:
        idx[fac["name"]] = {lv["id"]: lv for lv in fac.get("levels", [])}
    return idx


def _apply_factor_patches(
    base: bytes, idx: dict[str, dict[str, Any]], point: dict[str, str], root: Path
) -> bytes:
    result = base
    for name, lvl_id in point.items():
        level = idx.get(name, {}).get(lvl_id)
        if not level:
            continue
        patch_path = (root / level["patchRef"]).expanduser()
        kind = level.get("patchKind", "json-patch")
        result = apply_patch(result, patch_path, kind)
    return result


def create_factor_branches(vcs, spec: dict[str, Any], spec_dir: Path) -> list[str]:
    """Create a branch for each factor level with its patched artifact."""

    base_path = (spec_dir / spec["baseArtifact"]).expanduser()
    base_bytes = base_path.read_bytes()
    branches: list[str] = []
    start_branch = (
        vcs.repo.active_branch.name if not vcs.repo.head.is_detached else None
    )
    for fac in spec.get("factors", []):
        for lvl in fac.get("levels", []):
            branch = pea_ref("factor", fac["name"], lvl["id"])
            vcs.create_branch(branch, start_branch or "HEAD")
            vcs.switch(branch)
            art_bytes = base_bytes
            if lvl.get("artifactRef"):
                art_bytes = (spec_dir / lvl["artifactRef"]).read_bytes()
            else:
                current_art = Path(vcs.repo.working_tree_dir) / lvl["output_path"]
                if current_art.exists():
                    art_bytes = current_art.read_bytes()
            patch_path = (spec_dir / lvl["patchRef"]).expanduser()
            kind = lvl.get("patchKind", "json-patch")
            patched = apply_patch(art_bytes, patch_path, kind)
            target = Path(vcs.repo.working_tree_dir) / lvl["output_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(patched)
            rel_art = str(target.relative_to(vcs.repo.working_tree_dir))
            rel_patch = (
                str(patch_path.relative_to(vcs.repo.working_tree_dir))
                if patch_path.is_file()
                and patch_path.is_relative_to(vcs.repo.working_tree_dir)
                else None
            )
            paths = [p for p in [rel_art, rel_patch] if p]
            vcs.commit(paths, f"factor {fac['name']}={lvl['id']}")
            branches.append(branch)
    if start_branch:
        vcs.switch(start_branch)
    else:
        vcs.repo.git.switch("--detach", vcs.repo.head.commit.hexsha)
    return branches


def create_run_branches(vcs, spec: dict[str, Any], spec_dir: Path) -> list[str]:
    """Create run branches by applying factor patches for each design point."""

    factors = spec.get("factors", [])
    factor_idx = _factor_index(factors)
    base_path = (spec_dir / spec["baseArtifact"]).expanduser()
    base_bytes = base_path.read_bytes()
    design_points = _matrix_v2(factors)

    # assume a consistent output path across factor levels
    output_path = factors[0]["levels"][0]["output_path"] if factors else "artifact.yaml"

    start_branch = (
        vcs.repo.active_branch.name if not vcs.repo.head.is_detached else None
    )
    base_bytes = None
    factor_idx = None
    if spec and spec_dir and spec.get("baseArtifact"):
        base_path = (spec_dir / spec["baseArtifact"]).expanduser()
        base_bytes = base_path.read_bytes()
        factor_idx = _factor_index(spec.get("factors", []))
    branches: list[str] = []
    for point in design_points:
        label = "_".join(f"{k}-{v}" for k, v in point.items())
        branch = pea_ref("run", label)
        vcs.create_branch(branch, "HEAD")
        vcs.switch(branch)
        patched = _apply_factor_patches(base_bytes, factor_idx, point, spec_dir)
        tgt = Path(vcs.repo.working_tree_dir) / output_path
        tgt.parent.mkdir(parents=True, exist_ok=True)
        tgt.write_bytes(patched)
        vcs.commit([str(tgt.relative_to(vcs.repo.working_tree_dir))], f"run {label}")
        branches.append(branch)
    if start_branch:
        vcs.switch(start_branch)
    else:
        vcs.repo.git.switch("--detach", vcs.repo.head.commit.hexsha)
    return branches


def _render_patch_ops(
    patch_ops: List[Dict[str, Any]], ctx: Dict[str, Any]
) -> List[Dict[str, Any]]:
    warnings.warn(
        "_render_patch_ops is deprecated and will be removed in a future release",
        DeprecationWarning,
        stacklevel=2,
    )
    rendered: List[Dict[str, Any]] = []
    for pt in patch_ops:
        op = pt.copy()
        if "value" in op:
            raw_val = op["value"]

            # SPECIAL-CASE dotted-path mapping
            if isinstance(raw_val, dict) and len(raw_val) == 1:
                key = next(iter(raw_val))
                if "." in key:
                    op["value"] = _ctx_lookup(key, ctx)
                    rendered.append(op)
                    continue

            rendered_val = Template(str(raw_val)).render(**ctx)
            op["value"] = yaml.safe_load(rendered_val)

        rendered.append(op)
    return rendered


# ─────────────────────────── public API ────────────────────────────────────
def build_design_points(
    llm_map: Dict[str, Any], other_map: Dict[str, Any]
) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """Return (llm_keys, other_keys, design_points list)."""
    llm_codes = {
        (spec.get("code") if isinstance(spec, dict) else n): n
        for n, spec in llm_map.items()
    }
    other_codes = {
        (spec.get("code") if isinstance(spec, dict) else n): n
        for n, spec in other_map.items()
    }

    design_points = [
        dict(llm + oth)
        for llm in _matrix(llm_map)
        for oth in _matrix(other_map or {"_dummy": [None]})
    ]

    return list(llm_codes.keys()), list(other_codes.keys()), design_points  # pyright: ignore[reportReturnType]


def generate_projects(
    *,
    template_obj: Dict[str, Any],
    spec_obj: Dict[str, Any],
    design_points: List[Dict[str, Any]],
    llm_codes: Dict[str, str],
    other_codes: Dict[str, str],
    spec_name: str,
) -> List[Dict[str, Any]]:
    projects: List[Dict[str, Any]] = []
    base_list = template_obj.get("PROJECTS", [])
    base_proj = deepcopy(base_list[0]) if base_list else {}
    other_keys = {
        k: deepcopy(v)
        for k, v in template_obj.items()
        if k not in {"PROJECTS", "schemaVersion", "SOURCE"}
    }
    for idx, point in enumerate(design_points):
        ctx = {
            **point,
            "EXP_ID": f"{idx:03d}",
            "BASE_NAME": base_proj.get("NAME"),
        }

        proj = {**other_keys, "PROJECTS": [deepcopy(base_proj)]}

        # per-factor patches
        for factor_def in spec_obj.get("FACTORS", {}).values():
            rendered = _render_patch_ops(factor_def.get("patches", []), ctx)
            proj = _apply_json_patch(proj, rendered)

        # conditional global patches
        for rule in spec_obj.get("PATCHES", []):
            when: Dict[str, Any] = rule.get("when", {})
            if all(point.get(k) == v for k, v in when.items()):
                rendered = _render_patch_ops(rule["apply"], ctx)
                proj = _apply_json_patch(proj, rendered)

        # META section
        llm_factors = {llm_codes.get(k, k): point[k] for k in llm_codes}
        other_factors = {
            other_codes.get(k, k): point[k] for k in other_codes if k in point
        }

        meta = {
            "design_id": f"{spec_name}-{idx:03d}",
            "LLM_FACTORS": llm_factors,
            "factors": other_factors,
        }
        proj.setdefault("META", {}).update(meta)
        projects.append(proj)

    return projects


def _publish_event(
    notify_uri: str, output_path: Path, count: int, cfg_path: Optional[Path]
) -> None:
    nt = urlparse(notify_uri)
    pub_name = nt.scheme or notify_uri

    toml_cfg = load_peagen_toml(cfg_path or Path.cwd())
    bus_cfg = toml_cfg.get("publishers", {}).get("adapters", {}).get(pub_name, {})

    channel = nt.path.lstrip("/") or bus_cfg.get("channel", "peagen.events")
    PubCls = resolve_plugin_spec("publishers", pub_name)  # may raise KeyError
    bus = PubCls(**bus_cfg)
    bus.publish(
        channel,
        {"type": "peagen.experiment.done", "output": str(output_path), "count": count},
    )


def generate_payload(
    *,
    spec_path: Path,
    template_path: Path,
    output_path: Path,
    cfg_path: Optional[Path] = None,
    notify_uri: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
    skip_validate: bool = False,
    evaluate_runs: bool = False,
    eval_program_glob: str = "**/*.*",
    eval_pool: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Expand *spec_path* × *template_path* into a project-payload bundle.

    Returns a JSON-serialisable summary; writes *output_path* unless dry-run.
    """
    # 1. ------------ load + validate -------------------------------------
    spec_obj = _load_yaml(spec_path, kind="spec")
    template_obj = _load_yaml(template_path, kind="template")
    schema_version = template_obj.get("schemaVersion", "1.0.0")

    if "version" not in spec_obj:
        raise ValueError("legacy DOE specs are no longer supported")
    if spec_obj.get("version") != "v2":
        raise ValueError(f"unsupported DOE spec version: {spec_obj.get('version')!r}")

    if not skip_validate:
        _validate(spec_obj, DOE_SPEC_V2_SCHEMA, "DOE spec")

    factors = spec_obj.get("factors", [])
    factor_idx = _factor_index(factors)
    design_points = _matrix_v2(factors)
    llm_keys: List[str] = []
    other_keys = [f["name"] for f in factors]

    llm_codes: Dict[str, str] = {}
    other_codes = {name: name for name in other_keys}

    projects = generate_projects(
        template_obj=template_obj,
        spec_obj=spec_obj,
        design_points=design_points,
        llm_codes=llm_codes,
        other_codes=other_codes,
        spec_name=spec_path.stem,
    )

    # ensure the output directory exists before generating files
    output_path.parent.mkdir(parents=True, exist_ok=True)

    bundles: List[Tuple[Path, Dict[str, Any]]] = []
    for idx, proj_payload in enumerate(projects):
        out_path = output_path.parent / (
            f"{output_path.stem}_{idx:03d}{output_path.suffix}"
        )

        proj_payload.pop("schemaVersion", None)

        bundle = {
            "schemaVersion": schema_version,
            "PROJECTS": [proj_payload],
            "SOURCE": {
                "spec": str(spec_path),
                "template": str(template_path),
                "spec_checksum": _sha256(spec_path),
            },
        }

        bundles.append((out_path, bundle))
    artifact_outputs = []
    if spec_obj.get("baseArtifact"):
        base_path = (spec_path.parent / spec_obj["baseArtifact"]).expanduser()
        base_bytes = base_path.read_bytes()
        for idx2, point in enumerate(design_points):
            patched = _apply_factor_patches(
                base_bytes, factor_idx, point, spec_path.parent
            )
            tgt = output_path.parent / f"{base_path.stem}_{idx2:03d}{base_path.suffix}"
            if not dry_run:
                tgt.write_bytes(patched)
            artifact_outputs.append(str(tgt))

    # 2. ------------ write file (unless dry-run) -------------------------
    bytes_written = 0
    outputs: List[str] = []
    if not dry_run:
        for out_path, bundle in bundles:
            if out_path.exists() and not force:
                raise FileExistsError(
                    f"{out_path} exists – use force=True to overwrite"
                )
            out_path.write_text(
                yaml.safe_dump(bundle, sort_keys=False), encoding="utf-8"
            )
            outputs.append(str(out_path))
            bytes_written += out_path.stat().st_size
    else:
        outputs = [str(p) for p, _ in bundles]

    # 3. ------------ optional event publish ------------------------------
    if notify_uri:
        _publish_event(notify_uri, output_path, len(bundles), cfg_path)

    evaluations: List[Dict[str, Any]] = []
    if evaluate_runs:
        for art in artifact_outputs:
            ws = Path(art).parent
            try:
                report = evaluate_workspace(
                    repo=str(ws),
                    ref="HEAD",
                    program_glob=eval_program_glob,
                    pool_ref=eval_pool,
                    cfg_path=cfg_path,
                )
                evaluations.append(report)
                out_dir = ws / ".peagen"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "eval_results.json").write_text(
                    json.dumps(report, indent=2),
                    encoding="utf-8",
                )
            except Exception as exc:  # pragma: no cover - optional
                evaluations.append({"workspace": str(ws), "error": str(exc)})

    # 4. ------------ summary ---------------------------------------------
    return {
        "outputs": outputs,
        "artifact_outputs": artifact_outputs,
        "evaluations": evaluations,
        "count": len(bundles),
        "bytes": bytes_written,
        "llm_keys": llm_keys,
        "other_keys": other_keys,
        "dry_run": dry_run,
    }
