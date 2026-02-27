from __future__ import annotations

from dataclasses import replace
from typing import Dict

from .._spec.op_spec import OpSpec
from .context import MappingKey


SPEC_PRECEDENCE = ("app", "router", "op", "default")


def key_for(spec: OpSpec) -> MappingKey:
    return (spec.alias, spec.target)


def merge_op_specs(
    base_specs: tuple[OpSpec, ...], ctx_specs: tuple[OpSpec, ...]
) -> tuple[OpSpec, ...]:
    """Apply OpSpec-over-base precedence for operation mapping resolution."""
    merged_by_key: Dict[MappingKey, OpSpec] = {key_for(sp): sp for sp in base_specs}

    for sp in ctx_specs:
        key = key_for(sp)
        base = merged_by_key.get(key)
        if base is None:
            merged_by_key[key] = sp
            continue

        merged_by_key[key] = replace(
            sp,
            http_methods=sp.http_methods or base.http_methods,
            path_suffix=sp.path_suffix or base.path_suffix,
            tags=sp.tags or base.tags,
            deps=sp.deps or base.deps,
            secdeps=sp.secdeps or base.secdeps,
            request_model=sp.request_model
            if sp.request_model is not None
            else base.request_model,
            response_model=sp.response_model
            if sp.response_model is not None
            else base.response_model,
        )

    return tuple(merged_by_key.values())
