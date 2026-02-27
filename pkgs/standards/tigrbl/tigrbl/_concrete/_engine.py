# tigrbl/tigrbl/v3/engine/_engine.py
from __future__ import annotations

from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
import asyncio
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Union,
)

try:
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession
except Exception:  # pragma: no cover
    Session = object  # type: ignore
    AsyncSession = object  # type: ignore


class SessionFactory(Protocol):
    def __call__(self) -> Union[Session, AsyncSession]: ...


Builder = Callable[[], Tuple[Any, SessionFactory]]  # returns (engine, sessionmaker)

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .._spec.engine_spec import EngineSpec


@dataclass(frozen=True)
class Provider:
    # supports() exposes engine capabilities for compatibility checks
    def supports(self) -> dict:
        try:
            return self.spec.supports()
        except Exception:
            return {"engine": self.spec.kind or "unknown"}

    """Lazily builds an engine + sessionmaker from an :class:`EngineSpec`."""

    spec: "EngineSpec"
    _engine: Any = None
    _maker: Optional[SessionFactory] = None
    get_db: Callable[..., Any] = field(init=False)

    @property
    def kind(self) -> str:
        return "async" if self.spec.async_ else "sync"

    def ensure(self) -> Tuple[Any, SessionFactory]:
        if self._maker is None:
            eng, mk = self.spec.build()
            object.__setattr__(self, "_engine", eng)
            object.__setattr__(self, "_maker", mk)
        return self._engine, self._maker  # type: ignore[return-value]

    def session(self) -> Union[Session, AsyncSession]:
        _, mk = self.ensure()
        return mk()  # type: ignore[misc]

    def __post_init__(self) -> None:
        if self.spec.async_:

            async def _get_db() -> Any:
                db = self.session()
                try:
                    yield db  # type: ignore[misc]
                finally:
                    close = getattr(db, "close", None)
                    if callable(close):
                        rv = close()
                        if inspect.isawaitable(rv):
                            await rv

            object.__setattr__(self, "get_db", _get_db)
        else:

            def _get_db() -> Any:
                db = self.session()
                try:
                    yield db  # type: ignore[misc]
                finally:
                    close = getattr(db, "close", None)
                    if callable(close):
                        rv = close()
                        if inspect.isawaitable(rv):
                            try:
                                loop = asyncio.get_running_loop()
                            except RuntimeError:
                                asyncio.run(rv)
                            else:
                                loop.create_task(rv)

            object.__setattr__(self, "get_db", _get_db)


@dataclass
class Engine:
    # Delegate to provider/spec for capability reporting
    def supports(self) -> dict:
        try:
            return self.provider.supports()
        except Exception:
            return {"engine": self.spec.kind or "unknown"}

    """Thin façade over an :class:`EngineSpec` with convenient (a)context managers."""

    spec: "EngineSpec"
    provider: Provider = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", Provider(self.spec))

    @property
    def is_async(self) -> bool:
        return self.provider.kind == "async"

    def raw(self) -> Tuple[Any, SessionFactory]:
        return self.provider.ensure()

    @staticmethod
    def collect_engine_bindings(
        *,
        app: Any | None = None,
        router: Any | None = None,
        tables: Iterable[Any] = (),
    ) -> Mapping[str, Any]:
        """Collect engine bindings from app/router/table objects."""
        from ..mapping.traversal import collect_engine_bindings

        return collect_engine_bindings(app=app, router=router, tables=tables)

    @staticmethod
    def install_engine_bindings(collected: Mapping[str, Any]) -> None:
        """Install collected engine bindings into the resolver."""
        from ..mapping.traversal import install_engine_bindings

        install_engine_bindings(collected)

    @classmethod
    def install_from_objects(
        cls,
        *,
        app: Any | None = None,
        router: Any | None = None,
        tables: Iterable[Any] = (),
    ) -> None:
        """Collect and install engine bindings from app/router/table objects."""
        collected = cls.collect_engine_bindings(app=app, router=router, tables=tables)
        cls.install_engine_bindings(collected)

    @property
    def get_db(self) -> Callable[..., Any]:
        return self.provider.get_db

    @contextmanager
    def session(self) -> Session:
        db = self.provider.session()
        try:
            yield db  # type: ignore[return-value]
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                close()

    @asynccontextmanager
    async def asession(self) -> AsyncSession:
        db = self.provider.session()
        try:
            yield db  # type: ignore[return-value]
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                # AsyncSession.close() is sync; close() may exist as async in some impls
                res = close()
                if hasattr(res, "__await__"):
                    await res
