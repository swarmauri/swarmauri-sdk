# tigrbl/v3/config/defaults.py
from __future__ import annotations

from typing import Any, Mapping

# Canonical defaults used by config.resolver and runtime atoms.
# Keep these conservative; adapters/apps can override at any scope.
DEFAULTS: Mapping[str, Any] = {
    # ── wire/out (response shaping) ────────────────────────────────────────────
    "exclude_none": False,  # drop null-valued keys in wire:dump
    "omit_nulls": False,  # alias; resolver normalizes both ways
    "response_extras_overwrite": False,  # allow extras to replace existing keys
    "extras_overwrite": False,  # alias; resolver normalizes both ways
    # ── wire/in (request validation) ───────────────────────────────────────────
    "reject_unknown_fields": False,  # if True, unknown input keys cause 422
    # ── refresh / hydration policy ────────────────────────────────────────────
    "refresh_policy": "auto",  # 'auto' | 'always' | 'never'
    "refresh_after_write": None,  # Optional[bool]; resolver maps → policy
    # ── validation/docs policy buckets (deep-merged) ──────────────────────────
    # Shape: dict[op][field] = bool (true means "required for inbound")
    "required_policy": {},
    # ── docs/openapi knobs (deep-merged) ──────────────────────────────────────
    "openapi": {},
    "docs": {},
    # ── tracing (deep-merged) ─────────────────────────────────────────────────
    "trace": {
        "enabled": True,
    },
}
