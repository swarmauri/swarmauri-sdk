# autoapi/autoapi/v3/api/_api.py
from __future__ import annotations
from typing import Any
from types import SimpleNamespace

from ..deps.fastapi import APIRouter as ApiRouter
from ..engine.engine_spec import EngineCfg
from ..engine import install_from_objects
from ..engine import resolver as _resolver
from .api_spec import APISpec


class Api(APISpec, ApiRouter):
    """API router with model and table registries."""

    MODELS: tuple[Any, ...] = ()
    TABLES: tuple[Any, ...] = ()

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
        self.models: dict[str, type] = {}

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
