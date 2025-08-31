# autoapi/autoapi/v3/api/_api.py
from __future__ import annotations
from typing import (
    Any,
    AsyncGenerator,
    Generator,
)

from ..engines import resolver as _resolver
from ..engine import install_from_objects
from .api_spec import APISpec


class API(APISpec):
    def __init__(self, **fastapi_kwargs: Any) -> None:
        super().__init__(
            title=self.TITLE,
            version=self.VERSION,
            lifespan=self.LIFESPAN,
            **fastapi_kwargs,
        )
        if self.DB is not None:
            _resolver.set_default(self.DB)
        for mw in self.MIDDLEWARES:
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
