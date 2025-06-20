"""Helpers for applying artifact patches.

This module implements various patch kinds used by the
Design-of-Experiments system. Only lightweight algorithms are
included; advanced patch types may rely on external tools.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import jsonpatch
import yaml

from peagen.errors import PatchTargetMissingError


# ---------------------------------------------------------------------------
# JSON patch helpers
# ---------------------------------------------------------------------------

def _apply_json_patch(doc: Any, ops: list[dict[str, Any]]) -> Any:
    """Return ``doc`` after applying RFC6902 operations."""
    try:
        return jsonpatch.apply_patch(doc, ops, in_place=False)
    except (jsonpatch.JsonPatchConflict, jsonpatch.JsonPointerException) as exc:
        raise PatchTargetMissingError(str(exc)) from exc


# ---------------------------------------------------------------------------
# JSON merge (RFC 7386)
# ---------------------------------------------------------------------------

def _apply_json_merge(doc: Any, patch: Any) -> Any:
    if not isinstance(patch, dict) or not isinstance(doc, dict):
        return patch

    result = dict(doc)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _apply_json_merge(result.get(key, {}), value)
        else:
            result[key] = value
    return result


def _apply_yaml_overlay(doc: Any, patch: Any) -> Any:
    """Apply a simple YAML overlay (identical to JSON merge)."""
    return _apply_json_merge(doc, patch)


# ---------------------------------------------------------------------------
# Git patch application
# ---------------------------------------------------------------------------

def _apply_git_patch(base: bytes, patch_path: Path) -> bytes:
    with TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        tgt = tmp / "artifact"
        tgt.write_bytes(base)

        subprocess.run(["git", "init"], cwd=tmp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "nobody@example.com"], cwd=tmp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.name", "nobody"], cwd=tmp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "artifact"], cwd=tmp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "base"], cwd=tmp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "apply", str(patch_path)], cwd=tmp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return tgt.read_bytes()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_patch(base: bytes, patch_path: Path, kind: str) -> bytes:
    """Apply *patch_path* of type *kind* to ``base`` and return new bytes."""
    kind = kind.lower()
    if kind == "json-patch":
        ops = yaml.safe_load(patch_path.read_text(encoding="utf-8"))
        doc = yaml.safe_load(base.decode("utf-8"))
        patched = _apply_json_patch(doc, ops)
        return yaml.safe_dump(patched, sort_keys=False).encode("utf-8")
    if kind in {"json-merge", "yaml-overlay"}:
        patch = yaml.safe_load(patch_path.read_text(encoding="utf-8"))
        doc = yaml.safe_load(base.decode("utf-8"))
        if kind == "json-merge":
            patched = _apply_json_merge(doc, patch)
        else:
            patched = _apply_yaml_overlay(doc, patch)
        return yaml.safe_dump(patched, sort_keys=False).encode("utf-8")
    if kind == "git":
        return _apply_git_patch(base, patch_path)
    if kind == "cue":
        raise NotImplementedError("cue patching requires the 'cue' tool")
    raise ValueError(f"unknown patch kind: {kind}")


__all__ = ["apply_patch"]
