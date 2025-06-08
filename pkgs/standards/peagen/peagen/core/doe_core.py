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
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonpatch
import yaml
from jinja2 import Template
from urllib.parse import urlparse

from peagen._utils.config_loader import load_peagen_toml
from peagen.plugins import registry
from peagen.plugin_manager import resolve_plugin_spec

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


def _load_yaml(uri: str | Path) -> Dict[str, Any]:
    return yaml.safe_load(Path(uri).expanduser().read_text(encoding="utf-8"))


def _apply_json_patch(doc: Dict, patch_ops: List[Dict]) -> Dict:
    return jsonpatch.apply_patch(doc, patch_ops, in_place=False)


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


def _render_patch_ops(
    patch_ops: List[Dict[str, Any]], ctx: Dict[str, Any]
) -> List[Dict[str, Any]]:
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
        (spec.get("code") if isinstance(spec, dict) else n): n for n, spec in llm_map.items()
    }
    other_codes = {
        (spec.get("code") if isinstance(spec, dict) else n): n for n, spec in other_map.items()
    }

    design_points = [
        dict(llm + oth)
        for llm in _matrix(llm_map)
        for oth in _matrix(other_map or {"_dummy": [None]})
    ]

    return list(llm_codes.keys()), list(other_codes.keys()), design_points


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
    for idx, point in enumerate(design_points):
        ctx = {
            **point,
            "EXP_ID": f"{idx:03d}",
            "BASE_NAME": template_obj.get("PROJECTS", [{}])[0].get("NAME"),
        }

        proj = deepcopy(template_obj)

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
        other_factors = {other_codes.get(k, k): point[k] for k in other_codes if k in point}

        meta = {
            "design_id": f"{spec_name}-{idx:03d}",
            "LLM_FACTORS": llm_factors,
            "factors": other_factors,
        }
        proj.setdefault("META", {}).update(meta)
        projects.append(proj)

    return projects


def _publish_event(notify_uri: str, output_path: Path, count: int, cfg_path: Optional[Path]) -> None:
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
) -> Dict[str, Any]:
    """
    Expand *spec_path* × *template_path* into a project-payload bundle.

    Returns a JSON-serialisable summary; writes *output_path* unless dry-run.
    """
    # 1. ------------ load + validate -------------------------------------
    spec_obj = _load_yaml(spec_path)
    template_obj = _load_yaml(template_path)

    if not skip_validate:
        ...
        # placeholder
        # _validate(spec_obj, DOE_SPEC_V1_1_SCHEMA, "DOE spec")

    llm_map = spec_obj.get("LLM_FACTORS", {})
    other_map = spec_obj.get("FACTORS", {})

    # fallback for old specs with only FACTORS
    if not llm_map:
        guessed = {k: v for k, v in other_map.items() if k in _LLM_FALLBACK_KEYS}
        llm_map = guessed
        other_map = {k: v for k, v in other_map.items() if k not in guessed}

    llm_keys, other_keys, design_points = build_design_points(llm_map, other_map)

    llm_codes = {k: llm_map[k].get("code", k) if isinstance(llm_map.get(k), dict) else k for k in llm_map}
    other_codes = {k: other_map[k].get("code", k) if isinstance(other_map.get(k), dict) else k for k in other_map}

    projects = generate_projects(
        template_obj=template_obj,
        spec_obj=spec_obj,
        design_points=design_points,
        llm_codes=llm_codes,
        other_codes=other_codes,
        spec_name=spec_path.stem,
    )

    bundle = {
        "PROJECTS": projects,
        "SOURCE": {
            "spec": str(spec_path),
            "template": str(template_path),
            "spec_checksum": _sha256(spec_path),
        },
    }

    # 2. ------------ write file (unless dry-run) -------------------------
    bytes_written = 0
    if not dry_run:
        if output_path.exists() and not force:
            raise FileExistsError(f"{output_path} exists – use force=True to overwrite")
        output_path.write_text(yaml.safe_dump(bundle, sort_keys=False), encoding="utf-8")
        bytes_written = output_path.stat().st_size

    # 3. ------------ optional event publish ------------------------------
    if notify_uri:
        _publish_event(notify_uri, output_path, len(projects), cfg_path)

    # 4. ------------ summary ---------------------------------------------
    return {
        "output": str(output_path),
        "count": len(projects),
        "bytes": bytes_written,
        "llm_keys": llm_keys,
        "other_keys": other_keys,
        "dry_run": dry_run,
    }
