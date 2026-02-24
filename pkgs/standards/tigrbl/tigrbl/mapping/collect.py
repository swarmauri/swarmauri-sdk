from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, List, Optional, Set

from ..hook.mro_collect import mro_collect_decorated_hooks
from ..op import OpSpec, resolve as resolve_ops
from ..op.mro_collect import mro_alias_map_for, mro_collect_decorated_ops
from .context import MappingContext, MappingKey


def collect(
    model: type,
    *,
    router: Any | None = None,
    only_keys: Optional[Set[MappingKey]] = None,
) -> MappingContext:
    """Collect all spec sources for a single mapping pass."""
    base_specs: List[OpSpec] = list(resolve_ops(model))
    ctx_specs: List[OpSpec] = list(mro_collect_decorated_ops(model))

    # Inherit canonical schemas for aliased ctx ops lacking explicit schemas.
    base_by_target: Dict[str, OpSpec] = {sp.target: sp for sp in base_specs}
    fixed_ctx_specs: List[OpSpec] = []
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

    changed_keys = set(only_keys or ())
    return MappingContext(
        model=model,
        router=router,
        only_keys=only_keys,
        alias_map=mro_alias_map_for(model),
        base_specs=tuple(base_specs),
        ctx_specs=tuple(fixed_ctx_specs),
        changed_keys=changed_keys,
    )


def collect_hooks(context: MappingContext):
    aliases = {sp.alias for sp in context.base_specs} | {
        sp.alias for sp in context.ctx_specs
    }
    return mro_collect_decorated_hooks(context.model, visible_aliases=aliases)


__all__ = ["collect", "collect_hooks"]
