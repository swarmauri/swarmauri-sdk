# tigrbl/tigrbl/v3/api/_api.py
from __future__ import annotations
from typing import Any
from types import SimpleNamespace

from ..deps.asgi import APIRouter as ApiRouter
from ..engine.engine_spec import EngineCfg
from ..engine import install_from_objects
from ..ddl import initialize as _ddl_initialize
from ..engine import resolver as _resolver
from ..app._model_registry import initialize_model_registry
from .api_spec import APISpec


class Api(APISpec, ApiRouter):
    """API router with model and table registries."""

    MODELS: tuple[Any, ...] = ()
    TABLES: tuple[Any, ...] = ()

    # dataclass inheritance makes instances unhashable; use identity semantics
    # for both hashing and equality so objects can participate in sets/dicts
    def __hash__(self) -> int:  # pragma: no cover - simple identity hash
        return id(self)

    def __eq__(self, other: object) -> bool:  # pragma: no cover - identity compare
        return self is other

    @property
    def router(self) -> "Api":  # pragma: no cover - simple alias
        """Mirror ASGI app-style router access for API instances."""
        return self

    def __init__(
        self, *, engine: EngineCfg | None = None, **router_kwargs: Any
    ) -> None:
        # Manually initialize fields from ``APISpec`` so ``repr`` and other
        # dataclass-generated helpers have the expected attributes, while also
        # preparing mutable containers used at runtime.
        self.name = getattr(self, "NAME", "api")
        self.prefix = self.PREFIX
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.tags = list(getattr(self, "TAGS", []))
        self.ops = tuple(getattr(self, "OPS", ()))
        self.schemas = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.security_deps = tuple(getattr(self, "SECURITY_DEPS", ()))
        self.deps = tuple(getattr(self, "DEPS", ()))
        self.response = getattr(self, "RESPONSE", None)
        # ``models`` is expected to be a dict at runtime for registry lookups.
        self.models = initialize_model_registry(getattr(self, "MODELS", ()))

        ApiRouter.__init__(
            self,
            prefix=self.PREFIX,
            tags=self.tags,
            dependencies=list(self.security_deps) + list(self.deps),
            **router_kwargs,
        )

        # namespace containers
        self.tables: dict[str, Any] = {}

        _engine_ctx = engine if engine is not None else getattr(self, "ENGINE", None)
        if _engine_ctx is not None:
            _resolver.register_api(self, _engine_ctx)
            _resolver.resolve_provider(api=self)

    def add_route(
        self,
        path: str,
        endpoint: Any,
        *,
        methods: list[str] | tuple[str, ...],
        **kwargs: Any,
    ) -> None:
        """Compatibility alias for frameworks/tests expecting ``add_route``."""
        self.add_api_route(path, endpoint, methods=methods, **kwargs)

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

    def _normalize_prefix(self, prefix: str) -> str:
        return super()._normalize_prefix(prefix)

    def add_api_route(self, path: str, endpoint: Any, **kwargs: Any) -> None:
        return super().add_api_route(path, endpoint, **kwargs)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return super()._merge_tags(tags)

    def route(self, path: str, *, methods: Any, **kwargs: Any):
        return super().route(path, methods=methods, **kwargs)

    def include_router(self, other: Any, **kwargs: Any) -> None:
        return super().include_router(other, **kwargs)

    async def _resolve_route_dependencies(self, route: Any, req: Any) -> None:
        return await super()._resolve_route_dependencies(route, req)

    def _is_metadata_route(self, route: Any) -> bool:
        return super()._is_metadata_route(route)

    async def _resolve_handler_kwargs(self, route: Any, req: Any) -> dict[str, Any]:
        return await super()._resolve_handler_kwargs(route, req)

    async def _invoke_dependency(self, dep: Any, req: Any) -> Any:
        return await super()._invoke_dependency(dep, req)

    initialize = _ddl_initialize
