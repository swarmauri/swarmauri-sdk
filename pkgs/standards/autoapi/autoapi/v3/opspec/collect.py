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
)
from ..config.constants import (
    AUTOAPI_OPS_ATTR,
)
from ..decorators import alias_map_for  # new: canonical→alias mapping source

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
    Provide a baseline set of canonical specs for CRUD, list, clear.
    Bulk verbs can be added later by registry if supported.
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
        alias = target  # canonical alias matches the target (may be remapped by alias_ctx)
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


def _apply_alias_ctx_to_canon(
    specs: List[OpSpec], model: type
) -> List[OpSpec]:
    """
    Apply @alias_ctx (canonical verb → alias) to canonical specs **by renaming** the
    alias of canonical ops (alias==target). We do NOT create duplicate alias+canonical
    entries and we do NOT support legacy alias policies.
    """
    aliases = alias_map_for(model)  # {verb: alias}
    if not aliases:
        return specs

    out: List[OpSpec] = []
    for sp in specs:
        # Only rewrite canonical alias (alias == target) and only for known verbs
        new_alias = aliases.get(sp.target, sp.alias)  # type: ignore[arg-type]
        if new_alias != sp.alias:
            if not isinstance(new_alias, str) or not _ALIAS_RE.match(new_alias):
                logger.warning(
                    "Invalid alias %r for verb %r on %s; keeping %r",
                    new_alias,
                    sp.target,
                    model.__name__,
                    sp.alias,
                )
                out.append(sp)
                continue
            out.append(replace(sp, alias=new_alias))
        else:
            out.append(sp)
    return out


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def resolve(model: type) -> List[OpSpec]:
    """
    Build the effective OpSpec list for a model class.

    Precedence (later wins):
      1) Canonical defaults (subject to @alias_ctx renaming)
      2) Class-declared (__autoapi_ops__)
      3) Imperative registry (register_ops)

    Dedupe key: (alias, target)

    Note:
      • ctx-only ops declared via @op_ctx are collected in bindings.model.bind()
        (not here) and then merged/overridden there.
      • Legacy @custom_op and legacy alias policies are intentionally unsupported.
    """
    # 1) Canonical specs (rename alias via alias_ctx if provided)
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

    logger.debug("opspec.collect.resolve(%s): %d specs", model.__name__, len(specs))
    return specs


__all__ = ["resolve"]
