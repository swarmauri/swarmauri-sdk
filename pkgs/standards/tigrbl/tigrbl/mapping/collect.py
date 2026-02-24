from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Optional, Set

from ..op import OpSpec, resolve as resolve_ops
from ..op.mro_collect import mro_alias_map_for, mro_collect_decorated_ops
from .context import MappingContext, MappingKey


def collect(
    model: type,
    *,
    router: Any | None = None,
    only_keys: Optional[Set[MappingKey]] = None,
) -> MappingContext:
    """Collect all mutable inputs into a single immutable mapping context."""
    base_specs = tuple(resolve_ops(model))
    ctx_specs = tuple(mro_collect_decorated_ops(model))

    base_by_target: Dict[str, OpSpec] = {sp.target: sp for sp in base_specs}
    fixed_ctx_specs: list[OpSpec] = []
    for sp in ctx_specs:
        if (
            sp.alias != sp.target
            and sp.target != "custom"
            and sp.request_model is None
            and sp.response_model is None
        ):
            base = base_by_target.get(sp.target)
            if base:
                sp = replace(
                    sp,
                    request_model=base.request_model,
                    response_model=base.response_model,
                )
        fixed_ctx_specs.append(sp)

    alias_map = mro_alias_map_for(model)
    aliases = {
        canonical: frozenset(
            {canonical, *[a for a, c in alias_map.items() if c == canonical]}
        )
        for canonical in set(alias_map.values()) | set(alias_map.keys())
    }

    return MappingContext(
        model=model,
        router=router,
        only_keys=only_keys,
        alias_map=alias_map,
        aliases=aliases,
        base_specs=base_specs,
        ctx_specs=tuple(fixed_ctx_specs),
        changed_keys=frozenset(only_keys or ()),
    )


__all__ = ["collect"]
