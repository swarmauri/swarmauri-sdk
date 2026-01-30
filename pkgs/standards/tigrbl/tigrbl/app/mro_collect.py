from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Tuple

from .app_spec import AppSpec

logger = logging.getLogger("uvicorn")


def _merge_seq_attr(app: type, attr: str) -> Tuple[Any, ...]:
    values: list[Any] = []
    for base in reversed(app.__mro__):
        seq = getattr(base, attr, ()) or ()
        try:
            values.extend(seq)
        except TypeError:  # non-iterable
            values.append(seq)
    return tuple(values)


@lru_cache(maxsize=None)
def mro_collect_app_spec(app: type) -> AppSpec:
    """Collect AppSpec-like declarations across the app's MRO."""
    logger.info("Collecting app spec for %s", app.__name__)

    title = "Tigrbl"
    version = "0.1.0"
    engine: Any | None = None
    response = None
    jsonrpc_prefix = "/rpc"
    system_prefix = "/system"
    lifespan = None

    for base in reversed(app.__mro__):
        title = getattr(base, "TITLE", title)
        version = getattr(base, "VERSION", version)
        eng = getattr(base, "ENGINE", None)
        if eng is not None:
            engine = eng
        response = getattr(base, "RESPONSE", response)
        jsonrpc_prefix = getattr(base, "JSONRPC_PREFIX", jsonrpc_prefix)
        system_prefix = getattr(base, "SYSTEM_PREFIX", system_prefix)
        lifespan = getattr(base, "LIFESPAN", lifespan)

    spec = AppSpec(
        title=title,
        version=version,
        engine=engine,
        apis=_merge_seq_attr(app, "APIS"),
        ops=_merge_seq_attr(app, "OPS"),
        models=_merge_seq_attr(app, "MODELS"),
        schemas=_merge_seq_attr(app, "SCHEMAS"),
        hooks=_merge_seq_attr(app, "HOOKS"),
        security_deps=_merge_seq_attr(app, "SECURITY_DEPS"),
        deps=_merge_seq_attr(app, "DEPS"),
        response=response,
        jsonrpc_prefix=jsonrpc_prefix,
        system_prefix=system_prefix,
        middlewares=_merge_seq_attr(app, "MIDDLEWARES"),
        lifespan=lifespan,
    )
    return spec


__all__ = ["mro_collect_app_spec"]
