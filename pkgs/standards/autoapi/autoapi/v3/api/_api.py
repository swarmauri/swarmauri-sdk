# autoapi/autoapi/v3/api/_api.py
from __future__ import annotations
from typing import Any

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
        get_db = router_kwargs.pop("get_db", None)
        ApiRouter.__init__(
            self,
            prefix=self.PREFIX,
            tags=list(getattr(self, "TAGS", [])),
            dependencies=list(getattr(self, "SECURITY_DEPS", []))
            + list(getattr(self, "DEPS", [])),
            **router_kwargs,
        )

        # namespace containers
        self.models: dict[str, type] = {}
        self.tables: dict[str, Any] = {}

        _engine_ctx = engine if engine is not None else getattr(self, "ENGINE", None)
        if _engine_ctx is not None:
            _resolver.register_api(self, _engine_ctx)
            prov = _resolver.resolve_provider(api=self)
            if prov is not None and get_db is None:
                get_db = prov.get_db

        if get_db is not None:
            self.get_db = get_db

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
