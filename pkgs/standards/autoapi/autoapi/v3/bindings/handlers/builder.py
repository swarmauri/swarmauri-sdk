# autoapi/v3/bindings/handlers/builder.py
from __future__ import annotations

import logging
from typing import Optional, Sequence, Tuple

from ...op import OpSpec
from ...op.types import StepFn
from .namespaces import _ensure_alias_handlers_ns, _ensure_alias_hooks_ns
from .steps import _wrap_core, _wrap_custom

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]


def _attach_one(model: type, sp: OpSpec) -> None:
    alias = sp.alias
    handlers_ns = _ensure_alias_handlers_ns(model, alias)
    hooks_ns = _ensure_alias_hooks_ns(model, alias)
    chain: list[StepFn] = getattr(hooks_ns, "HANDLER")

    custom_step = _wrap_custom(model, sp, sp.handler) if sp.handler else None
    core_step: Optional[StepFn] = (
        None if sp.target == "custom" else _wrap_core(model, sp.target)
    )

    placement = sp.persist
    raw_step: Optional[StepFn] = None

    if placement == "skip":
        if custom_step is not None:
            chain.append(custom_step)
            raw_step = custom_step
    elif sp.target == "custom":
        if custom_step is not None:
            chain.append(custom_step)
            raw_step = custom_step
    elif custom_step is not None and core_step is not None:
        if placement == "append":
            chain.extend([core_step, custom_step])
            raw_step = core_step
        elif placement == "override":
            chain.append(custom_step)
            raw_step = custom_step
            core_step = None
        else:
            chain.extend([custom_step, core_step])
            raw_step = core_step
    elif core_step is not None:
        chain.append(core_step)
        raw_step = core_step
    elif custom_step is not None:
        chain.append(custom_step)
        raw_step = custom_step

    if raw_step is None:
        return

    setattr(handlers_ns, "raw", raw_step)
    setattr(handlers_ns, "handler", raw_step)

    try:
        if core_step is not None:
            sp.core = core_step
            sp.core_raw = core_step
        else:
            sp.core = raw_step
            sp.core_raw = raw_step
    except Exception:
        if core_step is not None:
            setattr(handlers_ns, "core", core_step)
            setattr(handlers_ns, "core_raw", core_step)
        else:
            setattr(handlers_ns, "core", raw_step)
            setattr(handlers_ns, "core_raw", raw_step)

    logger.debug(
        "handlers: %s.%s → handler chain updated (persist=%s)",
        model.__name__,
        alias,
        sp.persist,
    )


def build_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    wanted = set(only_keys or ())
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)


__all__ = ["build_and_attach"]
