from __future__ import annotations

from typing import Any, Callable, Iterable, List

from .hook_mro_collect import mro_collect_decorated_hooks
from ..op import resolve as resolve_ops
from tigrbl_atoms import PHASES
from .context import MappingContext
from .precedence import key_for, merge_op_specs


def _dedupe_by_name(funcs: Iterable[Callable[..., Any]]) -> List[Callable[..., Any]]:
    return list({getattr(fn, "__qualname__", str(fn)): fn for fn in funcs}.values())


def collect(ctx: MappingContext) -> MappingContext:
    """Collect canonical specs from the model graph."""
    base_specs = tuple(resolve_ops(ctx.model))
    return ctx.evolve(base_specs=base_specs)


def merge(ctx: MappingContext) -> MappingContext:
    """Merge context ops into canonical specs using explicit precedence rules."""
    all_specs = merge_op_specs(ctx.base_specs, ctx.ctx_specs)
    if ctx.only_keys:
        wanted = set(ctx.only_keys)
        visible_specs = tuple(spec for spec in all_specs if key_for(spec) in wanted)
    else:
        visible_specs = all_specs
    return ctx.evolve(all_specs=all_specs, visible_specs=visible_specs)


def bind_models(ctx: MappingContext) -> MappingContext:
    """Model-bind stage placeholder for deterministic plan execution."""
    return ctx


def bind_ops(ctx: MappingContext) -> MappingContext:
    """Operation-bind stage placeholder for deterministic plan execution."""
    return ctx


def bind_hooks(ctx: MappingContext) -> MappingContext:
    aliases = {sp.alias for sp in ctx.all_specs}
    base_hooks = getattr(ctx.model, "__tigrbl_hooks__", {}) or {}
    for phases in base_hooks.values():
        for phase, fns in list(phases.items()):
            phases[phase] = _dedupe_by_name(fns if isinstance(fns, list) else list(fns))

    ctx_hooks = mro_collect_decorated_hooks(ctx.model, visible_aliases=aliases)
    for alias, phases in ctx_hooks.items():
        if alias not in aliases:
            continue
        per = base_hooks.setdefault(alias, {})
        for phase, fns in phases.items():
            if phase in PHASES:
                existing = per.setdefault(phase, [])
                per[phase] = _dedupe_by_name([*existing, *fns])
    return ctx.evolve(merged_hooks=base_hooks)


def bind_deps(ctx: MappingContext) -> MappingContext:
    deps = {key_for(sp): tuple(sp.deps) for sp in ctx.visible_specs}
    secdeps = {key_for(sp): tuple(sp.secdeps) for sp in ctx.visible_specs}
    return ctx.evolve(deps=deps, secdeps=secdeps)


def seal(ctx: MappingContext) -> MappingContext:
    bound_graph = {
        "model": ctx.model,
        "router": ctx.router,
        "spec_count": len(ctx.visible_specs),
    }
    return ctx.evolve(bound_graph=bound_graph)
