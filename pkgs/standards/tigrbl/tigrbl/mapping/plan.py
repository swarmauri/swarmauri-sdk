from __future__ import annotations

from typing import Any, Callable, Iterable, List

from ..op.types import PHASES
from .collect import collect_hooks
from .context import MappingContext, MappingPlan
from .resolver import filter_visible, resolve


def _dedupe_by_name(funcs: Iterable[Callable[..., Any]]) -> List[Callable[..., Any]]:
    return list({getattr(fn, "__qualname__", str(fn)): fn for fn in funcs}.values())


def _merge_hooks(context: MappingContext, aliases: set[str]):
    base_hooks = getattr(context.model, "__tigrbl_hooks__", {}) or {}
    for phases in base_hooks.values():
        for phase, fns in list(phases.items()):
            phases[phase] = _dedupe_by_name(fns if isinstance(fns, list) else list(fns))

    ctx_hooks = collect_hooks(context)
    for alias, phases in ctx_hooks.items():
        if alias not in aliases:
            continue
        per = base_hooks.setdefault(alias, {})
        for phase, fns in phases.items():
            if phase in PHASES:
                existing = per.setdefault(phase, [])
                per[phase] = _dedupe_by_name([*existing, *fns])
    return base_hooks


def plan(context: MappingContext) -> MappingPlan:
    all_specs = resolve(context)
    visible_specs = filter_visible(context, all_specs)
    visible_aliases = (
        {sp.alias for sp in visible_specs}
        if visible_specs
        else {sp.alias for sp in all_specs}
    )
    merged_hooks = _merge_hooks(context, visible_aliases)

    return MappingPlan(
        model=context.model,
        router=context.router,
        only_keys=context.only_keys,
        alias_map=context.alias_map,
        all_specs=tuple(all_specs),
        visible_specs=tuple(visible_specs),
        merged_hooks=merged_hooks,
    )


__all__ = ["plan"]
