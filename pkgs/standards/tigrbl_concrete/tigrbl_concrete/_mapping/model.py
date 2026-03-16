from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional, Set, Tuple

from tigrbl_concrete._mapping.op_resolver import resolve as resolve_ops
from tigrbl_core._spec import OpSpec

from .model_helpers import _ensure_model_namespaces, _filter_specs, _index_specs

MappingKey = tuple[str, str]


def bind(
    model: type,
    *,
    router: Any | None = None,
    only_keys: Optional[Set[MappingKey]] = None,
) -> Tuple[OpSpec, ...]:
    del router
    specs = tuple(_filter_specs(tuple(resolve_ops(model)), only_keys))
    _ensure_model_namespaces(model)
    all_specs, by_key, by_alias = _index_specs(specs)
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    model.opspecs = model.ops
    return all_specs


def rebind(
    model: type,
    *,
    router: Any | None = None,
    changed_keys: Optional[Set[MappingKey]] = None,
) -> Tuple[OpSpec, ...]:
    return bind(model, router=router, only_keys=changed_keys)


__all__ = ["bind", "rebind"]
