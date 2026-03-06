# pkgs/standards/tigrbl_core/tigrbl/_spec/app_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from .._spec.engine_spec import EngineCfg
from .._spec.response_spec import ResponseSpec
from .serde import SerdeMixin


@dataclass(eq=False)
class AppSpec(SerdeMixin):
    """
    Used to *produce an App subclass* via App.from_spec().
    """

    title: str = "Tigrbl"
    description: str | None = None
    version: str = "0.1.0"
    engine: Optional[EngineCfg] = None

    # NEW: multi-Router composition (store Router classes or instances)
    routers: Sequence[Any] = field(default_factory=tuple)

    # NEW: orchestration/topology knobs
    ops: Sequence[Any] = field(default_factory=tuple)  # op descriptors or specs
    tables: Sequence[Any] = field(default_factory=tuple)  # table refs owned by app
    schemas: Sequence[Any] = field(default_factory=tuple)  # schema classes/defs
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # security/dep stacks (ASGI dependencies or callables)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # response defaults
    response: Optional[ResponseSpec] = None

    # system routing prefixes (REST/JSON-RPC namespaces)
    jsonrpc_prefix: str = "/rpc"
    system_prefix: str = "/system"

    # optional framework bits
    middlewares: Sequence[Any] = field(default_factory=tuple)
    lifespan: Optional[Callable[..., Any]] = None

    @classmethod
    def collect(cls, app: type) -> "AppSpec":
        from tigrbl.mapping.spec_normalization import (
            merge_seq_attr,
            normalize_app_spec,
        )

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

        description = getattr(app, "DESCRIPTION", None)
        include_inherited_routers = "ROUTERS" not in app.__dict__
        spec = cls(
            title=title,
            description=description,
            version=version,
            engine=engine,
            routers=tuple(
                merge_seq_attr(
                    app,
                    "ROUTERS",
                    include_inherited=include_inherited_routers,
                    reverse=include_inherited_routers,
                    dedupe=False,
                )
                or ()
            ),
            ops=tuple(merge_seq_attr(app, "OPS") or ()),
            tables=tuple(merge_seq_attr(app, "TABLES") or ()),
            schemas=tuple(merge_seq_attr(app, "SCHEMAS") or ()),
            hooks=tuple(merge_seq_attr(app, "HOOKS") or ()),
            security_deps=tuple(merge_seq_attr(app, "SECURITY_DEPS") or ()),
            deps=tuple(merge_seq_attr(app, "DEPS") or ()),
            response=response,
            jsonrpc_prefix=(jsonrpc_prefix or "/rpc"),
            system_prefix=(system_prefix or "/system"),
            middlewares=tuple(merge_seq_attr(app, "MIDDLEWARES") or ()),
            lifespan=lifespan,
        )
        return normalize_app_spec(
            cls(
                title=spec.title,
                description=spec.description,
                version=spec.version,
                engine=spec.engine,
                routers=tuple(spec.routers or ()),
                ops=tuple(spec.ops or ()),
                tables=tuple(spec.tables or ()),
                schemas=tuple(spec.schemas or ()),
                hooks=tuple(spec.hooks or ()),
                security_deps=tuple(spec.security_deps or ()),
                deps=tuple(spec.deps or ()),
                response=spec.response,
                jsonrpc_prefix=(spec.jsonrpc_prefix or "/rpc"),
                system_prefix=(spec.system_prefix or "/system"),
                middlewares=tuple(spec.middlewares or ()),
                lifespan=spec.lifespan,
            )
        )
