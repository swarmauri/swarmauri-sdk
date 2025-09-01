# autoapi/autoapi/v3/app/_app.py
from __future__ import annotations
from typing import (
    Any,
    AsyncGenerator,
    Generator,
)

from ..deps.fastapi import FastAPI
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from .app_spec import AppSpec


class App(AppSpec, FastAPI):
    def __init__(self, *, db: EngineCfg | None = None, **fastapi_kwargs: Any) -> None:
        FastAPI.__init__(
            self,
            title=self.TITLE,
            version=self.VERSION,
            lifespan=self.LIFESPAN,
            **fastapi_kwargs,
        )
        ctx = db if db is not None else getattr(self, "DB", None)
        if ctx is not None:
            _resolver.set_default(ctx)
        for mw in getattr(self, "MIDDLEWARES", []):
            self.add_middleware(mw.__class__, **getattr(mw, "kwargs", {}))

    def get_db(self) -> Generator[Any, None, None]:
        db, release = _resolver.acquire()
        try:
            yield db
        finally:
            release()

    async def get_async_db(self) -> AsyncGenerator[Any, None]:
        db, release = _resolver.acquire()
        try:
            yield db
        finally:
            release()

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
