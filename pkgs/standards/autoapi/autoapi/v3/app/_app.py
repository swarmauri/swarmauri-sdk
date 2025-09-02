# autoapi/autoapi/v3/app/_app.py
from __future__ import annotations
from typing import Any

from ..deps.fastapi import FastAPI
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from .app_spec import AppSpec


class App(AppSpec, FastAPI):
    def __init__(
        self, *, engine: EngineCfg | None = None, **fastapi_kwargs: Any
    ) -> None:
        FastAPI.__init__(
            self,
            title=self.TITLE,
            version=self.VERSION,
            lifespan=self.LIFESPAN,
            **fastapi_kwargs,
        )
        ctx = engine if engine is not None else getattr(self, "ENGINE", None)
        if ctx is not None:
            _resolver.set_default(ctx)
            prov = _resolver.resolve_provider()
            if prov is not None:
                self.get_db = prov.get_db  # type: ignore[attr-defined]
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
