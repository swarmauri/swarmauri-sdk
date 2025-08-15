# autoapi/v3/opspec/collect.py
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
    CANON,
    OpSpec,
    TargetOp,
    VerbAliasPolicy,
)
from ..config.constants import (
    OPS_ATTR,
    CUSTOM_OP_ATTR,
    VERB_ALIASES_ATTR,
    VERB_ALIAS_POLICY_ATTR,
)

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
                "Invalid OpSpec kwargs in %s for %s: %s", OPS_ATTR, table.__name__, e
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
            "%s on %s has unsupported type: %r", OPS_ATTR, table.__name__, type(value)
        )

    return specs


def _collect_class_declared(model: type) -> List[OpSpec]:
    declared = getattr(model, OPS_ATTR, None)
    return _as_specs(declared, model)


def _collect_decorators(model: type) -> List[OpSpec]:
    """
    Scan the MRO for callables decorated with @custom_op (they carry
    `.__autoapi_custom_op__` which is either an OpSpec or a kwargs dict).
    """
    out: List[OpSpec] = []
    for cls in reversed(model.__mro__):  # base classes first; child overrides later
        for name, attr in cls.__dict__.items():
            spec_meta = getattr(attr, CUSTOM_OP_ATTR, None)
            if not spec_meta:
                continue
            if isinstance(spec_meta, OpSpec):
                sp = _ensure_spec_table(spec_meta, model)
                # If the spec didn't set a handler, use the function itself
                if sp.handler is None and callable(attr):
                    sp = replace(sp, handler=attr)
                out.append(sp)
            elif isinstance(spec_meta, Mapping):
                kwargs = dict(spec_meta)
                kwargs.setdefault("alias", name)
                sp = OpSpec(table=model, handler=attr, **kwargs)  # type: ignore[arg-type]
                out.append(sp)
            else:
                logger.warning(
                    "Unknown custom_op payload on %s.%s: %r",
                    cls.__name__,
                    name,
                    type(spec_meta),
                )
    return out


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
    Provide a baseline set of canonical specs for CRUD, list, clear.
    Bulk verbs can be added later by registry/decorators if supported.
    """
    canon_targets: Tuple[TargetOp, ...] = (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    )
    out: List[OpSpec] = []
    for target in canon_targets:
        alias = target  # canonical alias matches the target
        out.append(
            OpSpec(
                alias=alias,
                target=target,
                table=model,
                arity="member"
                if target in {"read", "update", "replace", "delete"}
                else "collection",
                # persistent by default; binder will auto START_TX/END_TX where appropriate
                persist="default",
                returns="model" if target != "clear" else "raw",
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


def _normalize_alias_map(
    model: type,
) -> Tuple[List[Tuple[str, TargetOp]], VerbAliasPolicy]:
    """
    Support both styles:
      {"soft_delete": "delete"}  → alias -> target
      {"delete": "soft_delete"}  → target -> alias
    Returns list of (alias, target). Only allows targets in CANON (including bulk, clear).
    """
    raw = getattr(model, VERB_ALIASES_ATTR, {}) or {}
    policy: VerbAliasPolicy = getattr(model, VERB_ALIAS_POLICY_ATTR, "both")  # type: ignore[assignment]

    pairs: List[Tuple[str, TargetOp]] = []
    for k, v in raw.items():
        alias: Optional[str] = None
        target: Optional[TargetOp] = None

        if isinstance(v, str) and v in CANON:
            alias, target = k, v  # alias -> target
        elif isinstance(k, str) and k in CANON and isinstance(v, str):
            alias, target = v, k  # target -> alias

        if alias and target:
            if not _ALIAS_RE.match(alias):
                logger.warning(
                    "Invalid verb alias %r on %s; must match %s",
                    alias,
                    model.__name__,
                    _ALIAS_RE.pattern,
                )
                continue
            pairs.append((alias, target))  # type: ignore[arg-type]
        else:
            logger.warning(
                "Unrecognized alias mapping on %s: %r -> %r", model.__name__, k, v
            )

    return pairs, policy


def _apply_aliases(
    specs: List[OpSpec],
    model: type,
) -> List[OpSpec]:
    """
    Clone canonical specs per alias map. REST stays canonical by default.
    Policy:
      - both:         keep canonical; add alias (expose_rpc/method True, expose_routes False)
      - alias_only:   hide canonical RPC/method; add alias; REST stays canonical
      - canonical_only: ignore alias map
    """
    pairs, policy = _normalize_alias_map(model)
    if not pairs or policy == "canonical_only":
        return specs

    # Map from target -> canonical spec (prefer one with expose_routes True)
    canon_by_target: Dict[str, OpSpec] = {}
    for sp in specs:
        if sp.alias == sp.target:  # heuristic for canonical
            canon_by_target.setdefault(sp.target, sp)

    new_specs: List[OpSpec] = list(specs)

    for alias, target in pairs:
        base = canon_by_target.get(target)
        if not base:
            logger.warning(
                "Alias %r → %r has no base canonical spec on %s",
                alias,
                target,
                model.__name__,
            )
            continue

        # Clone with new alias; keep everything else; hide REST by default
        alias_spec = replace(
            base,
            alias=alias,
            expose_routes=False,
            expose_rpc=True,
            expose_method=True,
        )
        new_specs.append(alias_spec)

        if policy == "alias_only":
            # Hide canonical RPC/method; keep REST canonical endpoints
            hidden = replace(
                base,
                expose_rpc=False,
                expose_method=False,
            )
            # Replace in-place (maintain list order roughly)
            for i, s in enumerate(new_specs):
                if s is base:
                    new_specs[i] = hidden
                    break

    return new_specs


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def resolve(model: type) -> List[OpSpec]:
    """
    Build the effective OpSpec list for a model class.

    Precedence (later wins):
      1) Canonical defaults
      2) Class-declared (__autoapi_ops__)
      3) Decorator-defined (@custom_op)
      4) Imperative registry (register_ops)
      5) Aliasing (__autoapi_verb_aliases__/__autoapi_verb_alias_policy__)

    Dedupe key: (alias, target)
    """
    # Start with canonical specs so every model gets a complete surface by default
    canon = _generate_canonical(model)
    class_specs = _collect_class_declared(model)
    deco_specs = _collect_decorators(model)
    reg_specs = _collect_registry(model)

    merged: Dict[Tuple[str, str], OpSpec] = {}
    _dedupe(merged, canon)
    _dedupe(merged, class_specs)
    _dedupe(merged, deco_specs)
    _dedupe(merged, reg_specs)

    specs = list(merged.values())
    specs = _apply_aliases(specs, model)

    # Ensure all specs have table set to the model (defensive)
    specs = [_ensure_spec_table(sp, model) for sp in specs]

    logger.debug("opspec.collect.resolve(%s): %d specs", model.__name__, len(specs))
    return specs


__all__ = ["resolve"]
