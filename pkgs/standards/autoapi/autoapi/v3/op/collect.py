# autoapi/v3/ops/collect.py
from __future__ import annotations

from dataclasses import replace
import logging
import re
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from .types import (
    OpSpec,
    TargetOp,
)
from ..config.constants import (
    AUTOAPI_OPS_ATTR,
)
from .decorators import (
    alias_map_for,
    _OpDecl,
    _unwrap,
    _wrap_ctx_core,
    _infer_arity,
    _normalize_persist,
)
from .canonical import should_wire_canonical

try:
    # Per-model registry (observable, triggers rebind elsewhere)
    from .model_registry import get_registered_ops  # type: ignore
except Exception:  # pragma: no cover

    def get_registered_ops(model: type) -> Sequence[OpSpec]:  # shim
        return ()


logger = logging.getLogger(__name__)

_ALIAS_RE = re.compile(r"^[a-z][a-z0-9_]*$")


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────


def _ensure_spec_table(spec: OpSpec, table: type) -> OpSpec:
    if spec.table is table:
        return spec
    return replace(spec, table=table)


def _as_specs(value: Any, table: type) -> List[OpSpec]:
    """
    Accepts a variety of shapes from __autoapi_ops__:
      • OpSpec
      • Iterable[OpSpec]
      • Mapping[str, dict]  (alias -> kwargs for OpSpec without the handler)
      • Iterable[Mapping[str, Any]] (each with 'alias' & 'target')
    Returns a list of OpSpec with .table set.
    """
    specs: List[OpSpec] = []
    if value is None:
        return specs

    def _from_kwargs(kwargs: Mapping[str, Any]) -> Optional[OpSpec]:
        if "alias" not in kwargs or "target" not in kwargs:
            return None
        try:
            return OpSpec(table=table, **kwargs)  # type: ignore[arg-type]
        except TypeError as e:
            logger.error(
                "Invalid OpSpec kwargs in __autoapi_ops__ for %s: %s", table.__name__, e
            )
            return None

    if isinstance(value, OpSpec):
        specs.append(_ensure_spec_table(value, table))
    elif isinstance(value, Mapping):
        # Mapping[str, dict] where key can be alias (if not provided in dict)
        for maybe_alias, cfg in value.items():
            if isinstance(cfg, OpSpec):
                specs.append(_ensure_spec_table(cfg, table))
                continue
            if isinstance(cfg, Mapping):
                kwargs = dict(cfg)
                kwargs.setdefault("alias", maybe_alias)
                sp = _from_kwargs(kwargs)
                if sp:
                    specs.append(sp)
    elif isinstance(value, Iterable):
        for item in value:
            if isinstance(item, OpSpec):
                specs.append(_ensure_spec_table(item, table))
            elif isinstance(item, Mapping):
                sp = _from_kwargs(item)
                if sp:
                    specs.append(sp)
    else:
        logger.warning(
            "__autoapi_ops__ on %s has unsupported type: %r",
            table.__name__,
            type(value),
        )

    return specs


def _collect_class_declared(model: type) -> List[OpSpec]:
    declared = getattr(model, AUTOAPI_OPS_ATTR, None)
    return _as_specs(declared, model)


def _collect_registry(model: type) -> List[OpSpec]:
    try:
        return [
            _ensure_spec_table(sp, model) for sp in (get_registered_ops(model) or ())
        ]
    except Exception as e:  # pragma: no cover
        logger.exception("get_registered_ops failed for %s: %s", model.__name__, e)
        return []


def _generate_canonical(model: type) -> List[OpSpec]:
    """
    Provide a baseline set of canonical specs for CRUD, list, clear, and bulk ops.

    NOTE: We do not wire any `returns` preference here. Serialization mode is
    inferred later from the presence/absence of a response schema during binding.
    """
    canon_targets: Tuple[TargetOp, ...] = (
        "create",
        "read",
        "update",
        "replace",
        "merge",
        "delete",
        "list",
        "clear",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_merge",
        "bulk_delete",
    )
    out: List[OpSpec] = []
    for target in canon_targets:
        if not should_wire_canonical(model, target):
            continue
        alias = (
            target  # canonical alias matches the target (may be remapped by alias_ctx)
        )
        out.append(
            OpSpec(
                alias=alias,
                target=target,  # ← canonical verb goes here
                table=model,
                arity="member"
                if target in {"read", "update", "replace", "merge", "delete"}
                else "collection",
                # persistent by default; binder will auto START_TX/END_TX where appropriate
                persist="default",
                # Do not set `returns` here.
            )
        )
    return out


def _dedupe(
    existing: Dict[Tuple[str, str], OpSpec], incoming: Iterable[OpSpec]
) -> None:
    """
    Merge specs into `existing` using (alias, target) as the key.
    Later sources overwrite earlier ones.
    """
    for sp in incoming:
        if not isinstance(sp, OpSpec):
            continue
        if not sp.alias or not sp.target:
            continue
        existing[(sp.alias, sp.target)] = sp  # last wins


def _apply_alias_ctx_to_canon(specs: List[OpSpec], model: type) -> List[OpSpec]:
    """
    Apply @alias_ctx to canonical specs:

      • Rename canonical alias (alias==target) → provided alias.
      • Apply per-verb overrides from `__autoapi_alias_overrides__`:
          - request_schema    → OpSpec.request_model
          - response_schema   → OpSpec.response_model
          - persist           → OpSpec.persist
          - arity             → OpSpec.arity
          - rest (bool)       → OpSpec.expose_routes
          - engine            → OpSpec.engine             (NEW)

    We do NOT support any `returns` override. If no response schema is set,
    binders should treat the op as returning raw.
    """
    aliases = alias_map_for(model)  # {verb: alias}
    overrides: Mapping[str, Mapping[str, Any]] = (
        getattr(model, "__autoapi_alias_overrides__", {}) or {}
    )

    if not aliases and not overrides:
        return specs

    out: List[OpSpec] = []
    for sp in specs:
        canon = sp.target  # canonical verb string
        # 1) rename if applicable
        new_alias = aliases.get(canon, sp.alias)  # type: ignore[arg-type]
        mutated = sp
        if new_alias != sp.alias:
            if not isinstance(new_alias, str) or not _ALIAS_RE.match(new_alias):
                logger.warning(
                    "Invalid alias %r for verb %r on %s; keeping %r",
                    new_alias,
                    sp.target,
                    model.__name__,
                    sp.alias,
                )
            else:
                mutated = replace(mutated, alias=new_alias, path_suffix="")

        # 2) apply per-verb overrides (no returns handling)
        ov = overrides.get(canon)  # type: ignore[index]
        if ov:
            repl_kwargs: Dict[str, Any] = {}
            if ov.get("request_schema") is not None:
                repl_kwargs["request_model"] = ov["request_schema"]
            if ov.get("response_schema") is not None:
                repl_kwargs["response_model"] = ov["response_schema"]
            # allow per-verb engine binding via overrides["engine"]
            if ov.get("engine") is not None:
                repl_kwargs["engine"] = ov["engine"]
            if ov.get("persist") is not None:
                val = ov["persist"]
                if val in ("default", "skip", "override"):
                    repl_kwargs["persist"] = val
                else:
                    logger.warning(
                        "Invalid persist=%r for %s.%s",
                        val,
                        model.__name__,
                        mutated.alias,
                    )
            if ov.get("arity") is not None:
                val = ov["arity"]
                if val in ("member", "collection"):
                    repl_kwargs["arity"] = val
                else:
                    logger.warning(
                        "Invalid arity=%r for %s.%s", val, model.__name__, mutated.alias
                    )
            if ov.get("rest") is not None:
                repl_kwargs["expose_routes"] = bool(ov["rest"])

            if repl_kwargs:
                mutated = replace(mutated, **repl_kwargs)

        out.append(mutated)

    return out


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def resolve(model: type) -> List[OpSpec]:
    """
    Build the effective OpSpec list for a model class.

    Precedence (later wins):
      1) Canonical defaults (subject to @alias_ctx renaming/overrides)
      2) Class-declared (__autoapi_ops__)
      3) Imperative registry (register_ops)

    Dedupe key: (alias, target)

    Note:
      • ctx-only ops declared via @op_ctx are collected in bindings.model.bind()
        (not here) and then merged/overridden there.
      • Legacy @custom_op and legacy alias policies are intentionally unsupported.
    """
    # 1) Canonical specs (rename alias & apply overrides via alias_ctx if provided)
    canon = _generate_canonical(model)
    canon = _apply_alias_ctx_to_canon(canon, model)

    # 2) Class-declared specs
    class_specs = _collect_class_declared(model)

    # 3) Registry specs
    reg_specs = _collect_registry(model)

    merged: Dict[Tuple[str, str], OpSpec] = {}
    _dedupe(merged, canon)
    _dedupe(merged, class_specs)
    _dedupe(merged, reg_specs)

    specs = list(merged.values())

    # Ensure all specs have table set to the model (defensive)
    specs = [_ensure_spec_table(sp, model) for sp in specs]

    logger.debug("ops.collect.resolve(%s): %d specs", model.__name__, len(specs))
    return specs


def collect_decorated_ops(table: type) -> list[OpSpec]:
    """Collect ctx-only op declarations (``@op_ctx``) into :class:`OpSpec`."""
    out: list[OpSpec] = []

    for base in reversed(table.__mro__):
        names = list(getattr(base, "__dict__", {}).keys())
        for name in dir(base):
            if name not in names:
                names.append(name)
        for name in names:
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decl: _OpDecl | None = getattr(func, "__autoapi_op_decl__", None)
            if not decl:
                continue

            target = decl.target or "custom"
            arity = decl.arity or _infer_arity(target)
            persist = _normalize_persist(decl.persist)
            alias = decl.alias or name

            expose_kwargs: dict[str, Any] = {}
            extra: dict[str, Any] = {}
            if decl.rest is not None:
                expose_kwargs["expose_routes"] = bool(decl.rest)
            elif alias != target and target in {
                "read",
                "update",
                "delete",
                "list",
                "clear",
            }:
                expose_kwargs["expose_routes"] = False

            spec = OpSpec(
                table=table,
                alias=alias,
                target=target,
                arity=arity,
                persist=persist,
                handler=_wrap_ctx_core(table, func),
                request_model=decl.request_schema,
                response_model=decl.response_schema,
                hooks=(),
                status_code=decl.status_code,
                extra=extra,
                **expose_kwargs,
            )
            out.append(spec)

    return out


__all__ = ["resolve", "collect_decorated_ops"]
