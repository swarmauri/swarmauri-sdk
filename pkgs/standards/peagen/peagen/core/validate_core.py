from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jsonschema import Draft7Validator

from peagen._utils._validation import _path

from peagen._utils.config_loader import load_peagen_toml
from peagen.jsonschemas import (
    PEAGEN_TOML_V1_SCHEMA,
    DOE_SPEC_V2_SCHEMA,
    PTREE_V1_SCHEMA,
    PROJECTS_PAYLOAD_V1_SCHEMA,
)


def _collect_errors(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Return a list of formatted validation errors."""
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    messages: List[str] = []
    for err in errors:
        messages.append(f"{_path(err)} – {err.message}")
        for sub in err.context:
            messages.append(f"{_path(sub)} – {sub.message}")
    return messages


def validate_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Validate a ``.peagen.toml`` configuration file."""
    try:
        cfg = load_peagen_toml(path or ".peagen.toml")
    except FileNotFoundError:
        return {"ok": False, "errors": ["No .peagen.toml found"]}

    errs = _collect_errors(cfg, PEAGEN_TOML_V1_SCHEMA)
    return {"ok": not errs, "errors": errs}


def _load_yaml(path: Path) -> Dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {"_yaml_error": str(exc)}


def _load_json(path: Path) -> Dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"_json_error": str(exc)}


def validate_doe_spec(path: Path) -> Dict[str, Any]:
    data = _load_yaml(path)
    if data is None or isinstance(data, dict) and "_yaml_error" in data:
        return {"ok": False, "errors": [data.get("_yaml_error", "YAML error")]}  # type: ignore[union-attr]

    if "version" not in data:
        return {"ok": False, "errors": ["legacy DOE specs are no longer supported"]}
    if data.get("version") != "v2":
        return {
            "ok": False,
            "errors": [f"unsupported DOE spec version: {data.get('version')!r}"],
        }

    errs = _collect_errors(data, DOE_SPEC_V2_SCHEMA)
    return {"ok": not errs, "errors": errs}


def validate_evolve_spec(path: Path) -> Dict[str, Any]:
    data = _load_yaml(path)
    if data is None or isinstance(data, dict) and "_yaml_error" in data:
        return {"ok": False, "errors": [data.get("_yaml_error", "YAML error")]}

    if data.get("version") != "2.0.0":
        return {
            "ok": False,
            "errors": [f"unsupported evolve spec version: {data.get('version')!r}"],
        }

    # The evolve spec schema is still under development. Skip strict
    # validation for now and ensure at least a ``JOBS`` section exists.
    if "JOBS" not in data:
        return {"ok": False, "errors": ["JOBS section is required"]}
    return {"ok": True, "errors": []}


def validate_ptree(path: Path) -> Dict[str, Any]:
    data = _load_yaml(path)
    if data is None or isinstance(data, dict) and "_yaml_error" in data:
        return {"ok": False, "errors": [data.get("_yaml_error", "YAML error")]}  # type: ignore[union-attr]
    errs = _collect_errors(data, PTREE_V1_SCHEMA)
    return {"ok": not errs, "errors": errs}


def validate_projects_payload(path: Path) -> Dict[str, Any]:
    data = _load_yaml(path)
    if data is None or isinstance(data, dict) and "_yaml_error" in data:
        return {"ok": False, "errors": [data.get("_yaml_error", "YAML error")]}  # type: ignore[union-attr]
    errs = _collect_errors(data, PROJECTS_PAYLOAD_V1_SCHEMA)
    return {"ok": not errs, "errors": errs}


def validate_artifact(kind: str, path: Optional[Path]) -> Dict[str, Any]:
    """Dispatch validation based on *kind*."""
    if kind == "config":
        return validate_config(path)
    if path is None:
        return {"ok": False, "errors": ["path is required"]}
    if kind == "doe":
        return validate_doe_spec(path)
    if kind == "evolve":
        return validate_evolve_spec(path)
    if kind == "ptree":
        return validate_ptree(path)
    if kind == "projects_payload":
        return validate_projects_payload(path)
    return {"ok": False, "errors": [f"unknown kind: {kind}"]}
