from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Tuple

from .app_spec import AppSpec

logger = logging.getLogger("uvicorn")


def _merge_seq_attr(
    app: type,
    attr: str,
    *,
    include_inherited: bool = False,
    reverse: bool = False,
) -> Tuple[Any, ...]:
    values: list[Any] = []
    mro = reversed(app.__mro__) if reverse else app.__mro__
    for base in mro:
        if include_inherited:
            if not hasattr(base, attr):
                continue
            seq = getattr(base, attr) or ()
        else:
            seq = base.__dict__.get(attr, ()) or ()
        try:
            values.extend(seq)
        except TypeError:  # non-iterable
            values.append(seq)
    return tuple(values)


@lru_cache(maxsize=None)
def mro_collect_app_spec(app: type) -> AppSpec:
    """Collect AppSpec-like declarations across the app's MRO."""
    logger.info("Collecting app spec for %s", app.__name__)

    sentinel = object()
    title: Any = sentinel
    version: Any = sentinel
    engine: Any | None = sentinel  # type: ignore[assignment]
    response: Any = sentinel
    jsonrpc_prefix: Any = sentinel
    system_prefix: Any = sentinel
    lifespan: Any = sentinel

    for base in app.__mro__:
        if "TITLE" in base.__dict__ and title is sentinel:
            title = base.__dict__["TITLE"]
        if "VERSION" in base.__dict__ and version is sentinel:
            version = base.__dict__["VERSION"]
        if "ENGINE" in base.__dict__ and engine is sentinel:
            engine = base.__dict__["ENGINE"]
        if "RESPONSE" in base.__dict__ and response is sentinel:
            response = base.__dict__["RESPONSE"]
        if "JSONRPC_PREFIX" in base.__dict__ and jsonrpc_prefix is sentinel:
            jsonrpc_prefix = base.__dict__["JSONRPC_PREFIX"]
        if "SYSTEM_PREFIX" in base.__dict__ and system_prefix is sentinel:
            system_prefix = base.__dict__["SYSTEM_PREFIX"]
        if "LIFESPAN" in base.__dict__ and lifespan is sentinel:
            lifespan = base.__dict__["LIFESPAN"]

    if title is sentinel:
        title = "Tigrbl"
    if version is sentinel:
        version = "0.1.0"
    if engine is sentinel:
        engine = None
    if response is sentinel:
        response = None
    if jsonrpc_prefix is sentinel:
        jsonrpc_prefix = "/rpc"
    if system_prefix is sentinel:
        system_prefix = "/system"
    if lifespan is sentinel:
        lifespan = None

    include_inherited_apis = "APIS" not in app.__dict__
    spec = AppSpec(
        title=title,
        version=version,
        engine=engine,
        apis=_merge_seq_attr(
            app,
            "APIS",
            include_inherited=include_inherited_apis,
            reverse=include_inherited_apis,
        ),
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
