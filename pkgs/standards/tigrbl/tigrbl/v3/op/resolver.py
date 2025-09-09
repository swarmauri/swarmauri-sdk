from __future__ import annotations

from dataclasses import replace
import logging
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .types import OpSpec, TargetOp
from ..config.constants import TIGRBL_OPS_ATTR
from .canonical import should_wire_canonical
from .mro_collect import mro_alias_map_for

try:
    # Per-model registry (observable, triggers rebind elsewhere)
    from .model_registry import get_registered_ops  # type: ignore
except Exception:  # pragma: no cover

    def get_registered_ops(model: type) -> Sequence[OpSpec]:  # shim
        return ()


logger = logging.getLogger("uvicorn")

_ALIAS_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _ensure_spec_table(spec: OpSpec, table: type) -> OpSpec:
    if spec.table is table:
        return spec
    return replace(spec, table=table)


def _as_specs(value: Any, table: type) -> List[OpSpec]:
    """Normalize various `__tigrbl_ops__` shapes to a list of OpSpec."""
    specs: List[OpSpec] = []
    if value is None:
        return specs

    def _from_kwargs(kwargs: Mapping[str, Any]) -> Optional[OpSpec]:
        if "alias" not in kwargs or "target" not in kwargs:
            return None
        try:
            spec = OpSpec(table=table, hooks=(), extra={}, **kwargs)
            return spec
        except Exception:  # pragma: no cover - defensive
            return None

    if isinstance(value, OpSpec):
        specs.append(_ensure_spec_table(value, table))
    elif isinstance(value, Mapping):
        for alias, cfg in value.items():
            if isinstance(cfg, Mapping):
                spec = _from_kwargs({"alias": alias, **cfg})
                if spec:
                    specs.append(spec)
    elif isinstance(value, Iterable):
        for item in value:
            if isinstance(item, OpSpec):
                specs.append(_ensure_spec_table(item, table))
            elif isinstance(item, Mapping):
                spec = _from_kwargs(item)
                if spec:
                    specs.append(spec)
    else:
        spec = _from_kwargs(
            {
                "alias": getattr(value, "alias", None),
                "target": getattr(value, "target", None),
            }
        )
        if spec:
            specs.append(spec)
    return specs


def _generate_canonical(table: type) -> List[OpSpec]:
    """Generate canonical CRUD specs based on model attributes."""
    specs: List[OpSpec] = []
    targets: List[Tuple[str, TargetOp]] = [
        ("create", "create"),
        ("read", "read"),
        ("update", "update"),
        # Include canonical "replace" so RPC callers get full CRUD semantics
        # without opting into the Replaceable mixin.
        ("replace", "replace"),
        ("merge", "merge"),
        ("delete", "delete"),
        ("list", "list"),
        ("clear", "clear"),
        ("bulk_create", "bulk_create"),
        ("bulk_update", "bulk_update"),
        ("bulk_replace", "bulk_replace"),
        ("bulk_merge", "bulk_merge"),
        ("bulk_delete", "bulk_delete"),
    ]
    collection_targets = {
        "create",
        "list",
        "clear",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_merge",
        "bulk_delete",
    }
    for alias, target in targets:
        if not should_wire_canonical(table, target):
            continue
        specs.append(
            OpSpec(
                table=table,
                alias=alias,
                target=target,
                arity="collection" if target in collection_targets else "member",
                persist="default",
                handler=None,
                request_model=None,
                response_model=None,
                hooks=(),
                status_code=None,
                extra={},
            )
        )
    return specs


def _collect_class_declared(model: type) -> List[OpSpec]:
    out: List[OpSpec] = []
    raw = getattr(model, TIGRBL_OPS_ATTR, None)
    if isinstance(raw, Mapping) or isinstance(raw, Iterable):
        out.extend(_as_specs(raw, model))
    return out


def _collect_registry(model: type) -> List[OpSpec]:
    return list(get_registered_ops(model))


def _dedupe(
    existing: Dict[Tuple[str, str], OpSpec], incoming: Iterable[OpSpec]
) -> None:
    for sp in incoming:
        if not isinstance(sp, OpSpec):
            continue
        if not sp.alias or not sp.target:
            continue
        existing[(sp.alias, sp.target)] = sp


def _apply_alias_ctx_to_canon(specs: List[OpSpec], model: type) -> List[OpSpec]:
    aliases = mro_alias_map_for(model)
    overrides: Mapping[str, Mapping[str, Any]] = (
        getattr(model, "__tigrbl_alias_overrides__", {}) or {}
    )

    if not aliases and not overrides:
        return specs

    out: List[OpSpec] = []
    for sp in specs:
        canon = sp.target
        new_alias = aliases.get(canon, sp.alias)
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

        ov = overrides.get(canon)
        if ov:
            kwargs = {}
            if "request_schema" in ov:
                kwargs["request_model"] = ov["request_schema"]
            if "response_schema" in ov:
                kwargs["response_model"] = ov["response_schema"]
            if "persist" in ov:
                kwargs["persist"] = ov["persist"]
            if "arity" in ov:
                kwargs["arity"] = ov["arity"]
            if "rest" in ov:
                kwargs["expose_routes"] = bool(ov["rest"])
            if "engine" in ov:
                kwargs["engine"] = ov["engine"]
            if kwargs:
                mutated = replace(mutated, **kwargs)
        out.append(mutated)
    return out


def resolve(model: type) -> List[OpSpec]:
    canon = _generate_canonical(model)
    canon = _apply_alias_ctx_to_canon(canon, model)

    class_specs = _collect_class_declared(model)
    reg_specs = _collect_registry(model)

    merged: Dict[Tuple[str, str], OpSpec] = {}
    _dedupe(merged, canon)
    _dedupe(merged, class_specs)
    _dedupe(merged, reg_specs)

    specs = list(merged.values())
    specs = [_ensure_spec_table(sp, model) for sp in specs]

    logger.debug("ops.resolver.resolve(%s): %d specs", model.__name__, len(specs))
    return specs


__all__ = ["resolve"]
