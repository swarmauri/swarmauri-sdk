# tigrbl/v3/config/resolver.py
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from types import MappingProxyType
from typing import Any, Dict, Iterable, Mapping, Optional

# Optional defaults module (kept tolerant if not present yet)
try:
    from .defaults import DEFAULTS  # expected: Mapping[str, Any]
except Exception:  # pragma: no cover
    DEFAULTS = {
        # wire/out
        "exclude_none": False,
        "omit_nulls": False,  # alias; normalized below
        "response_extras_overwrite": False,
        "extras_overwrite": False,  # alias
        # wire/in
        "reject_unknown_fields": False,
        # refresh
        "refresh_policy": "auto",  # 'auto' | 'always' | 'never'
        "refresh_after_write": None,  # Optional[bool] → normalized into refresh_policy
        # validation/docs
        "required_policy": {},  # dict[op][field] = bool
        # misc buckets developers may use
        "openapi": {},
        "docs": {},
        "trace": {"enabled": True},
    }


# Keys that should be deep-merged (dict ← dict) instead of overridden.
_DEEP_KEYS = {
    "required_policy",
    "openapi",
    "docs",
    "trace",
    "policies",
}


class CfgView:
    """
    Read-only attribute/dict view over a plain dict.
    Unknown attributes return None (to play nicely with getattr(cfg, 'x', None)).
    """

    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, Any]):
        # freeze top-level mapping
        self._data = MappingProxyType(dict(data))

    def __getattr__(self, name: str) -> Any:
        return self._data.get(name, None)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """Copy out a mutable dict (for diagnostics/serialization)."""
        return dict(self._data)

    def __repr__(self) -> str:  # pragma: no cover
        return f"CfgView({dict(self._data)!r})"


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def resolve_cfg(
    *,
    model: Any = None,
    specs: Optional[Mapping[str, Any]] = None,
    op: Optional[str] = None,
    opspec: Any = None,
    tabspec: Any = None,
    apispec: Any = None,
    appspec: Any = None,
    overrides: Optional[Mapping[str, Any]] = None,
) -> CfgView:
    """
    Merge configuration from multiple scopes with precedence:

      opspec > colspecs > tabspec > apispec > appspec > defaults

    The result is normalized and returned as a read-only CfgView suitable for ctx.cfg.

    Notes:
      - 'specs' is the {field -> ColumnSpec} map; any col-level '.cfg' dicts are merged.
      - Non-dict or None layers are ignored.
      - For a few known keys we support aliases and light normalization (see _normalize()).
    """
    layers: list[Mapping[str, Any]] = []

    # 1) Base defaults (lowest precedence)
    layers.append(_coerce_map(DEFAULTS))

    # 2) App / API / Tab scopes
    if appspec is not None:
        layers.append(_extract_cfg(appspec))
    if apispec is not None:
        layers.append(_extract_cfg(apispec))
    if tabspec is not None:
        layers.append(_extract_cfg(tabspec))

    # 3) Column-level aggregation (merged across all columns in stable order)
    if specs:
        col_cfg = _collect_col_cfg(specs)
        if col_cfg:
            layers.append(col_cfg)

    # 4) Op-spec (highest declared spec layer)
    if opspec is not None:
        layers.append(_extract_cfg(opspec))

    # 5) Per-request overrides (absolute highest precedence)
    if overrides:
        layers.append(_coerce_map(overrides))

    # Merge with precedence (later wins), then normalize and freeze
    merged = _merge_layers(layers)
    merged = _normalize(merged, op=op)

    return CfgView(merged)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _coerce_map(obj: Any) -> Mapping[str, Any]:
    """Best-effort conversion of common config carriers to a plain mapping."""
    if obj is None:
        return {}
    if isinstance(obj, Mapping):
        return obj
    # dataclass?
    if is_dataclass(obj):
        try:
            # Drop keys with ``None`` values so they don't override defaults.
            return {k: v for k, v in asdict(obj).items() if v is not None}
        except Exception:
            pass
    # namespace-like with __dict__
    d = getattr(obj, "__dict__", None)
    if isinstance(d, dict):
        return d
    # pydantic v2 config-like
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            return dict(obj.model_dump())
        except Exception:
            pass
    # last resort: single 'cfg' attr if it's a mapping
    cfg = getattr(obj, "cfg", None)
    if isinstance(cfg, Mapping):
        return cfg
    return {}


def _extract_cfg(spec: Any) -> Mapping[str, Any]:
    """
    Pull a config mapping from a spec-like object.
    Accepts: spec.cfg, spec.config, or the object itself if it's a mapping.
    """
    if isinstance(spec, Mapping):
        return spec
    for name in ("cfg", "config"):
        val = getattr(spec, name, None)
        if isinstance(val, Mapping):
            return val
    # dataclass or namespace
    return _coerce_map(spec)


def _collect_col_cfg(specs: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Merge .cfg from ColumnSpec and its sub-specs (io/field/storage) across all columns.
    Deep-merge dict values for keys in _DEEP_KEYS; override for scalars/others.
    Later fields (lexicographic) win on conflicts to keep determinism.
    """
    acc: Dict[str, Any] = {}
    for field in sorted(specs.keys()):
        col = specs[field]
        # Collect potential cfg dictionaries from multiple places on ColumnSpec
        for obj in (
            col,
            getattr(col, "io", None),
            getattr(col, "field", None),
            getattr(col, "storage", None),
        ):
            mapping = _extract_cfg(obj)
            if mapping:
                acc = _merge_layers([acc, mapping])
    return acc


def _merge_layers(layers: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """
    Precedence-aware merge: later layers override earlier ones.
    Dict values are shallow-merged except for keys in _DEEP_KEYS (deep merge).
    """
    result: Dict[str, Any] = {}
    for layer in layers:
        if not isinstance(layer, Mapping):
            continue
        for k, v in layer.items():
            if (
                k in _DEEP_KEYS
                and isinstance(result.get(k), Mapping)
                and isinstance(v, Mapping)
            ):
                result[k] = _deep_merge_dicts(result[k], v)
            else:
                result[k] = v
    return result


def _deep_merge_dicts(a: Mapping[str, Any], b: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dicts; values in 'b' override 'a'. Only recurses on dicts.
    Lists/sets/tuples are overridden (not concatenated) to remain predictable.
    """
    out: Dict[str, Any] = dict(a)
    for k, v in b.items():
        av = out.get(k)
        if isinstance(av, Mapping) and isinstance(v, Mapping):
            out[k] = _deep_merge_dicts(av, v)
        else:
            out[k] = v
    return out


def _normalize(cfg: Mapping[str, Any], *, op: Optional[str]) -> Dict[str, Any]:
    """
    Produce a normalized config dict with aliases resolved and policy rules applied.
    """
    d = dict(cfg)  # copy

    # 1) Refresh policy normalization
    #    - If refresh_after_write is explicitly True/False, that wins.
    #    - Otherwise ensure refresh_policy has a sane default.
    raw_after = d.get("refresh_after_write", None)
    if isinstance(raw_after, bool):
        d["refresh_policy"] = "always" if raw_after else "never"
    else:
        pol = d.get("refresh_policy", None)
        if pol not in {"auto", "always", "never"}:
            d["refresh_policy"] = "auto"

    # 2) Alias handling for omit nulls and extras overwrite
    if "exclude_none" not in d and isinstance(d.get("omit_nulls"), bool):
        d["exclude_none"] = bool(d["omit_nulls"])
    if "omit_nulls" not in d and isinstance(d.get("exclude_none"), bool):
        d["omit_nulls"] = bool(d["exclude_none"])

    if "response_extras_overwrite" not in d and isinstance(
        d.get("extras_overwrite"), bool
    ):
        d["response_extras_overwrite"] = bool(d["extras_overwrite"])
    if "extras_overwrite" not in d and isinstance(
        d.get("response_extras_overwrite"), bool
    ):
        d["extras_overwrite"] = bool(d["response_extras_overwrite"])

    # 3) required_policy structure sanity: dict[op][field] = bool
    rp = d.get("required_policy")
    if not isinstance(rp, Mapping):
        d["required_policy"] = {}
    else:
        # ensure nested dicts & booleans; ignore malformed entries
        fixed: Dict[str, Dict[str, bool]] = {}
        for op_name, per_field in rp.items():
            if not isinstance(per_field, Mapping):
                continue
            fixed[str(op_name)] = {
                str(f): bool(v)
                for f, v in per_field.items()
                if isinstance(v, (bool, int))
            }
        d["required_policy"] = fixed

    # 4) Optional op-specific view (pre-resolved convenience)
    if op:
        per_op = d["required_policy"].get(op, {})
        d.setdefault("_required_for_op", per_op)

    return d
