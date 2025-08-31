# autoapi/autoapi/v3/api/_api.py
from __future__ import annotations
from typing import (
    Any,
    AsyncGenerator,
    Generator,
)

from ..deps.fastapi import APIRouter as ApiRouter
from ..engine.engine_spec import EngineCtx
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from .api_spec import APISpec


class Api(APISpec, ApiRouter):
    def __init__(self, *, db: EngineCtx | None = None, **router_kwargs: Any) -> None:
        ApiRouter.__init__(
            self,
            prefix=self.PREFIX,
            tags=list(getattr(self, "TAGS", [])),
            dependencies=list(getattr(self, "SECURITY_DEPS", []))
            + list(getattr(self, "DEPS", [])),
            **router_kwargs,
        )
        ctx = db if db is not None else getattr(self, "DB", None)
        if ctx is not None:
            _resolver.register_api(self, ctx)

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
