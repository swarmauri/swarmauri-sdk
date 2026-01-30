# tigrbl/tigrbl/v3/app/_app.py
from __future__ import annotations
from typing import Any

from ..deps.fastapi import FastAPI
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from ..ddl import initialize as _ddl_initialize
from ._model_registry import initialize_model_registry
from .app_spec import AppSpec


class App(AppSpec, FastAPI):
    TITLE = "Tigrbl"
    VERSION = "0.1.0"
    LIFESPAN = None
    MIDDLEWARES = ()
    APIS = ()
    OPS = ()
    MODELS = ()
    SCHEMAS = ()
    HOOKS = ()
    SECURITY_DEPS = ()
    DEPS = ()
    RESPONSE = None
    JSONRPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

    def __init__(
        self, *, engine: EngineCfg | None = None, **fastapi_kwargs: Any
    ) -> None:
        # Manually mirror ``AppSpec`` fields so the dataclass-generated ``repr``
        # and friends have expected attributes while runtime structures remain
        # mutable dictionaries or lists as needed.
        title = fastapi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        version = fastapi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        lifespan = fastapi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        self.title = self.TITLE
        self.version = self.VERSION
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.apis = tuple(getattr(self, "APIS", ()))
        self.ops = tuple(getattr(self, "OPS", ()))
        # Runtime registries use mutable containers (dict/namespace), but the
        # dataclass fields expect sequences. Storing a dict here satisfies both.
        self.models = initialize_model_registry(getattr(self, "MODELS", ()))
        self.schemas = tuple(getattr(self, "SCHEMAS", ()))
        self.hooks = tuple(getattr(self, "HOOKS", ()))
        self.security_deps = tuple(getattr(self, "SECURITY_DEPS", ()))
        self.deps = tuple(getattr(self, "DEPS", ()))
        self.response = getattr(self, "RESPONSE", None)
        self.jsonrpc_prefix = getattr(self, "JSONRPC_PREFIX", "/rpc")
        self.system_prefix = getattr(self, "SYSTEM_PREFIX", "/system")
        self.middlewares = tuple(getattr(self, "MIDDLEWARES", ()))
        self.lifespan = self.LIFESPAN

        FastAPI.__init__(
            self,
            title=self.title,
            version=self.version,
            lifespan=self.lifespan,
            **fastapi_kwargs,
        )
        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()
        for mw in getattr(self, "MIDDLEWARES", []):
            self.add_middleware(mw.__class__, **getattr(mw, "kwargs", {}))

    def install_engines(
        self, *, api: Any = None, models: tuple[Any, ...] | None = None
    ) -> None:
        # If class declared APIS/MODELS, use them unless explicit args are passed.
        apis = (api,) if api is not None else self.APIS
        models = models if models is not None else self.MODELS
        if apis:
            for a in apis:
                install_from_objects(app=self, api=a, models=models)
        else:
            install_from_objects(app=self, api=None, models=models)

    def _collect_tables(self) -> list[Any]:
        seen = set()
        tables = []
        for model in self.models.values():
            if not hasattr(model, "__table__"):
                try:  # pragma: no cover - defensive remap
                    from ..table import Base
                    from ..table._base import _materialize_colspecs_to_sqla

                    _materialize_colspecs_to_sqla(model)
                    Base.registry.map_declaratively(model)
                except Exception:
                    pass
            table = getattr(model, "__table__", None)
            if table is not None and not table.columns:
                continue
            if table is not None and table not in seen:
                seen.add(table)
                tables.append(table)
        return tables

    initialize = _ddl_initialize
