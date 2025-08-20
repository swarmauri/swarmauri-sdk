# autoapi/v3/schema/col_info.py
"""
Utilities for reading & validating `Column.info["autoapi"]` metadata.

This module centralizes:
  • Allowed keys and verb names
  • Validation (with clear, contextual error messages)
  • Small helpers to decide input/output exposure per verb

It does **not** import SQLAlchemy – callers pass plain dicts extracted from
`Column.info` (or hybrid_property `.info`) so this remains framework-agnostic.

Typical usage in the schema builder:
    meta_src = getattr(col, "info", {}) or {}
    meta = (meta_src.get("autoapi") if isinstance(meta_src, dict) else None) or {}
    check(meta, attr_name, model.__name__)
    # then apply `should_include_in_input` / `should_include_in_output` as needed
"""

from __future__ import annotations

from typing import Any, Mapping

from ..opspec.types import CANON


# ───────────────────────────────────────────────────────────────────────────────
# Public constants
# ───────────────────────────────────────────────────────────────────────────────

# Valid verbs are derived from OpSpec canon (kept in sync automatically)
VALID_VERBS: frozenset[str] = frozenset(
    str(k) for k in (CANON.keys() if hasattr(CANON, "keys") else CANON)
)  # type: ignore[arg-type]

# Keys allowed inside Column.info["autoapi"]
VALID_KEYS: frozenset[str] = frozenset(
    {
        # legacy (still recognized)
        "no_create",  # (bool)   legacy toggle for create
        "no_update",  # (bool)   legacy toggle for update/replace
        # modern flags
        "disable_on",  # (Iterable[str]) verbs for which the field is disabled
        "write_only",  # (bool)   omit from OUT/read schemas
        "read_only",  # (bool | Iterable[str] | Mapping[str,bool])
        "default_factory",  # (callable) → Field(default_factory=…)
        "examples",  # (Any)    → Field(..., examples=…)
        "hybrid",  # (bool)   opt-in for @hybrid_property
        "py_type",  # (type)   explicit Python type for hybrids/unknowns
    }
)

# Convenience: write-phase verbs (helps some validations/decisions)
WRITE_VERBS: frozenset[str] = frozenset(
    v
    for v in VALID_VERBS
    if v not in {"read", "list"}  # everything else mutates or may flush
)


# ───────────────────────────────────────────────────────────────────────────────
# Validation & normalization
# ───────────────────────────────────────────────────────────────────────────────


def _err_ctx(model: str, attr: str, msg: str) -> ValueError:
    return ValueError(f"{model}.{attr}: {msg}")


def _as_iter(x: Any) -> list:
    if x is None:
        return []
    if isinstance(x, (set, tuple, list)):
        return list(x)
    return [x]


def _normalize_read_only(ro: Any, *, model: str, attr: str):
    """
    read_only may be:
      • bool
      • Iterable[str] of verbs
      • Mapping[str, bool] per verb
    Returns one of:
      • bool
      • frozenset[str]
      • dict[str, bool]
    """
    if isinstance(ro, bool):
        return ro

    if isinstance(ro, Mapping):
        out: dict[str, bool] = {}
        for k, v in ro.items():
            if not isinstance(k, str):
                raise _err_ctx(
                    model,
                    attr,
                    f"read_only mapping keys must be str verbs, got {type(k)!r}",
                )
            if k not in VALID_VERBS:
                raise _err_ctx(
                    model,
                    attr,
                    f"read_only has unknown verb {k!r} (valid: {sorted(VALID_VERBS)})",
                )
            if not isinstance(v, bool):
                raise _err_ctx(
                    model, attr, f"read_only[{k!r}] must be bool, got {type(v)!r}"
                )
            out[k] = v
        return out

    if isinstance(ro, (set, list, tuple)):
        bad = [v for v in ro if not isinstance(v, str) or v not in VALID_VERBS]
        if bad:
            raise _err_ctx(
                model,
                attr,
                f"read_only verbs invalid: {bad} (valid: {sorted(VALID_VERBS)})",
            )
        return frozenset(ro)

    raise _err_ctx(
        model,
        attr,
        f"read_only must be bool, Iterable[str], or Mapping[str,bool]; got {type(ro)!r}",
    )


def _normalize_disable_on(disable_on: Any, *, model: str, attr: str) -> frozenset[str]:
    if disable_on is None:
        return frozenset()
    if not isinstance(disable_on, (set, list, tuple, frozenset)):
        raise _err_ctx(
            model,
            attr,
            f"disable_on must be an iterable of verbs; got {type(disable_on)!r}",
        )
    verbs = []
    for v in disable_on:
        if not isinstance(v, str):
            raise _err_ctx(
                model, attr, f"disable_on entries must be str verbs; got {type(v)!r}"
            )
        if v not in VALID_VERBS:
            raise _err_ctx(
                model,
                attr,
                f"disable_on has unknown verb {v!r} (valid: {sorted(VALID_VERBS)})",
            )
        verbs.append(v)
    return frozenset(verbs)


def normalize(
    meta: Mapping[str, Any] | None, *, model: str, attr: str
) -> dict[str, Any]:
    """
    Validate and normalize a meta dict. Unknown keys raise; returns a **new** dict
    with normalized shapes:
      - disable_on → frozenset[str]
      - read_only  → bool | frozenset[str] | dict[str,bool]
      - write_only → bool
      - default_factory → callable | None
      - hybrid → bool
      - py_type → type | None
      - examples → as-is
      - no_create/no_update → bool (legacy)
    """
    meta = dict(meta or {})

    extra = set(meta.keys()) - VALID_KEYS
    if extra:
        raise _err_ctx(model, attr, f"unknown keys in info['autoapi']: {sorted(extra)}")

    out: dict[str, Any] = {}

    # legacy toggles
    if "no_create" in meta:
        if not isinstance(meta["no_create"], bool):
            raise _err_ctx(
                model, attr, f"no_create must be bool, got {type(meta['no_create'])!r}"
            )
        out["no_create"] = bool(meta["no_create"])
    if "no_update" in meta:
        if not isinstance(meta["no_update"], bool):
            raise _err_ctx(
                model, attr, f"no_update must be bool, got {type(meta['no_update'])!r}"
            )
        out["no_update"] = bool(meta["no_update"])

    # modern flags
    out["disable_on"] = _normalize_disable_on(
        meta.get("disable_on"), model=model, attr=attr
    )  # frozenset[str]

    ro = meta.get("read_only", False)
    out["read_only"] = _normalize_read_only(ro, model=model, attr=attr)

    wo = meta.get("write_only", False)
    if not isinstance(wo, bool):
        raise _err_ctx(model, attr, f"write_only must be bool, got {type(wo)!r}")
    out["write_only"] = wo

    df = meta.get("default_factory", None)
    if df is not None and not callable(df):
        raise _err_ctx(
            model, attr, f"default_factory must be callable or None, got {type(df)!r}"
        )
    out["default_factory"] = df

    out["examples"] = meta.get("examples", None)

    hy = meta.get("hybrid", False)
    if not isinstance(hy, bool):
        raise _err_ctx(model, attr, f"hybrid must be bool, got {type(hy)!r}")
    out["hybrid"] = hy

    py_t = meta.get("py_type", None)
    if py_t is not None and not isinstance(py_t, type):
        raise _err_ctx(model, attr, f"py_type must be a type or None, got {py_t!r}")
    out["py_type"] = py_t

    return out


def check(meta: Mapping[str, Any] | None, attr: str, model: str) -> None:
    """
    Validate only (drop-in replacement for v2 `info_schema.check`).
    Raises ValueError on problems; returns None on success.
    """
    # We reuse normalize to perform the validation; ignore the normalized result
    _ = normalize(meta, model=model, attr=attr)


# ───────────────────────────────────────────────────────────────────────────────
# Inclusion helpers (for schema builders / adapters)
# ───────────────────────────────────────────────────────────────────────────────


def _ro_applies(ro: Any, verb: str) -> bool:
    """
    Internal helper to evaluate the read_only directive for a given verb.
    """
    if isinstance(ro, bool):
        return bool(ro)
    if isinstance(ro, frozenset):
        return verb in ro
    if isinstance(ro, dict):
        val = ro.get(verb)
        if val is None:
            return False
        return bool(val)
    # Fallback (shouldn't happen after normalize)
    return False


def should_include_in_input(meta: Mapping[str, Any] | None, *, verb: str) -> bool:
    """
    Decide whether a field should appear in an **input** schema for `verb`.
    Rules:
      - if `verb` is in `disable_on`, exclude
      - if read_only applies for this verb, exclude
      - otherwise include
    """
    if not meta:
        return True
    try:
        m = normalize(meta, model="<model>", attr="<attr>")
    except Exception:
        # If meta is invalid, safest behavior is to include (builder may raise elsewhere)
        m = dict(meta)

    if verb in _as_iter(m.get("disable_on")):
        return False
    if _ro_applies(m.get("read_only", False), verb):
        # read_only excludes from input (except 'read' where it's an OUT schema)
        return False
    return True


def should_include_in_output(meta: Mapping[str, Any] | None, *, verb: str) -> bool:
    """
    Decide whether a field should appear in an **output** (read) schema for `verb`.
    Rules:
      - if `verb` is in `disable_on`, exclude
      - if write_only is True, exclude
      - otherwise include
    """
    if not meta:
        return True
    try:
        m = normalize(meta, model="<model>", attr="<attr>")
    except Exception:
        m = dict(meta)

    if verb in _as_iter(m.get("disable_on")):
        return False
    if bool(m.get("write_only", False)):
        return False
    return True


__all__ = [
    "VALID_VERBS",
    "VALID_KEYS",
    "WRITE_VERBS",
    "normalize",
    "check",
    "should_include_in_input",
    "should_include_in_output",
]
