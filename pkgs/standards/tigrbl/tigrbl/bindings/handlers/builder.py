# tigrbl/v3/bindings/handlers/builder.py
from __future__ import annotations

import logging
from typing import Optional, Sequence, Tuple

from ...op import OpSpec
from ...op.types import StepFn
from .namespaces import _ensure_alias_handlers_ns, _ensure_alias_hooks_ns
from .steps import _wrap_core, _wrap_custom

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/handlers/builder")

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

    logger.debug(
        "Attaching handler for %s.%s target=%s placement=%s",
        model.__name__,
        alias,
        sp.target,
        placement,
    )

    if placement == "skip":
        logger.debug("Placement 'skip' selected")
        if custom_step is not None:
            logger.debug("Appending custom step for alias %s", alias)
            chain.append(custom_step)
            raw_step = custom_step
    elif sp.target == "custom":
        logger.debug("Target 'custom' with alias %s", alias)
        if custom_step is not None:
            logger.debug("Appending custom step for alias %s", alias)
            chain.append(custom_step)
            raw_step = custom_step
    elif custom_step is not None and core_step is not None:
        logger.debug("Both custom and core steps present")
        if placement == "append":
            logger.debug("Appending core then custom step")
            chain.extend([core_step, custom_step])
            raw_step = core_step
        elif placement == "override":
            logger.debug("Overriding core step with custom step")
            chain.append(custom_step)
            raw_step = custom_step
            core_step = None
        else:
            logger.debug("Prepending custom then core step")
            chain.extend([custom_step, core_step])
            raw_step = core_step
    elif core_step is not None:
        logger.debug("Only core step present; appending")
        chain.append(core_step)
        raw_step = core_step
    elif custom_step is not None:
        logger.debug("Only custom step present; appending")
        chain.append(custom_step)
        raw_step = custom_step

    if raw_step is None:
        logger.debug("No raw step produced; exiting")
        return

    setattr(handlers_ns, "raw", raw_step)
    setattr(handlers_ns, "handler", raw_step)

    if core_step is not None:
        object.__setattr__(sp, "core", core_step)
        object.__setattr__(sp, "core_raw", core_step)
        setattr(handlers_ns, "core", core_step)
        setattr(handlers_ns, "core_raw", core_step)
        logger.debug("Core step registered for %s.%s", model.__name__, alias)
    else:
        object.__setattr__(sp, "core", raw_step)
        object.__setattr__(sp, "core_raw", raw_step)
        setattr(handlers_ns, "core", raw_step)
        setattr(handlers_ns, "core_raw", raw_step)
        logger.debug("Raw step registered as core for %s.%s", model.__name__, alias)

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
    logger.debug("Building handlers for %s (only_keys=%s)", model.__name__, wanted)
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            logger.debug("Skipping spec %s due to only_keys filter", key)
            continue
        logger.debug("Processing spec %s", key)
        _attach_one(model, sp)


__all__ = ["build_and_attach"]
