from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Tuple

from .app_spec import AppSpec

logger = logging.getLogger("uvicorn")


def _merge_seq_attr(app: type, attr: str) -> Tuple[Any, ...]:
    values: list[Any] = []
    for base in app.__mro__:
        seq = base.__dict__.get(attr, ()) or ()
        try:
            values.extend(seq)
        except TypeError:  # non-iterable
            values.append(seq)
    return tuple(values)


def _first_attr(app: type, attr: str, default: Any, *, skip_none: bool = False) -> Any:
    for base in app.__mro__:
        if attr in base.__dict__:
            value = base.__dict__[attr]
            if skip_none and value is None:
                continue
            return value
    return default


@lru_cache(maxsize=None)
def mro_collect_app_spec(app: type) -> AppSpec:
    """Collect AppSpec-like declarations across the app's MRO."""
    logger.info("Collecting app spec for %s", app.__name__)

    title = _first_attr(app, "TITLE", "Tigrbl")
    version = _first_attr(app, "VERSION", "0.1.0")
    engine: Any | None = _first_attr(app, "ENGINE", None, skip_none=True)
    response = _first_attr(app, "RESPONSE", None, skip_none=True)
    jsonrpc_prefix = _first_attr(app, "JSONRPC_PREFIX", "/rpc")
    system_prefix = _first_attr(app, "SYSTEM_PREFIX", "/system")
    lifespan = _first_attr(app, "LIFESPAN", None, skip_none=True)

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
