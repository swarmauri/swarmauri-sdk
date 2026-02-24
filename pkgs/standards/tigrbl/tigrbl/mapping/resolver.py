from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

from ..op import OpSpec
from .context import MappingContext, MappingKey


def key_for(spec: OpSpec) -> MappingKey:
    return (spec.alias, spec.target)


def resolve(context: MappingContext) -> List[OpSpec]:
    """Resolve effective op specs with ctx specs overriding canonical entries."""
    merged_by_key: Dict[MappingKey, OpSpec] = {}
    for sp in context.base_specs:
        merged_by_key[key_for(sp)] = sp

    for sp in context.ctx_specs:
        key = key_for(sp)
        base = merged_by_key.get(key)
        if base is not None:
            sp = replace(
                sp,
                http_methods=sp.http_methods or base.http_methods,
                path_suffix=sp.path_suffix or base.path_suffix,
                tags=sp.tags or base.tags,
            )
        merged_by_key[key] = sp

    return list(merged_by_key.values())


def filter_visible(context: MappingContext, specs: List[OpSpec]) -> List[OpSpec]:
    if not context.only_keys:
        return specs
    wanted = set(context.only_keys)
    return [spec for spec in specs if key_for(spec) in wanted]


__all__ = ["resolve", "filter_visible", "key_for"]
