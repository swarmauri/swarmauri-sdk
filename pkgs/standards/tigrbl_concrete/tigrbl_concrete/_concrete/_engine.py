# tigrbl/_concrete/_engine.py
from __future__ import annotations

from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
import asyncio
import inspect
from typing import Any, Callable, Optional, Tuple, Union, Protocol, TYPE_CHECKING

from tigrbl_base._base._engine_base import EngineBase
from tigrbl_base._base._engine_provider_base import EngineProviderBase

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
    from tigrbl_core._spec.engine_spec import EngineProviderSpec, EngineSpec


@dataclass(frozen=True)
class EngineProvider(EngineProviderBase):
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

    def to_provider(self) -> "EngineProviderBase":
        return self

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
class Engine(EngineBase):
    # Delegate to provider/spec for capability reporting
    def supports(self) -> dict:
        try:
            return self.provider.supports()
        except Exception:
            return {"engine": self.spec.kind or "unknown"}

    """Thin façade over an :class:`EngineSpec` with convenient (a)context managers."""

    spec: "EngineSpec"
    provider: EngineProvider = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", EngineProvider(self.spec))

    @property
    def is_async(self) -> bool:
        return self.provider.kind == "async"

    def to_provider(self) -> "EngineProviderBase":
        return self.provider

    def raw(self) -> Tuple[Any, SessionFactory]:
        return self.provider.ensure()

    @staticmethod
    def collect(
        *,
        app: Any | None = None,
        router: Any | None = None,
        tables: tuple[Any, ...] = (),
    ) -> dict[str, Any]:
        from tigrbl_core.config.engine_traversal import collect_engine_bindings

        return collect_engine_bindings(app=app, router=router, tables=tables)

    @staticmethod
    def install(collected: dict[str, Any]) -> None:
        from tigrbl_concrete._concrete import engine_resolver as _resolver

        default_db = collected.get("default")
        if default_db is not None:
            _resolver.set_default(default_db)
        for router_obj, db in (collected.get("router") or {}).items():
            _resolver.register_router(router_obj, db)
        for table_obj, db in (collected.get("tables") or {}).items():
            _resolver.register_table(table_obj, db)
        for (model, alias), db in (collected.get("ops") or {}).items():
            _resolver.register_op(model, alias, db)

    @staticmethod
    def install_from_objects(
        *,
        app: Any | None = None,
        router: Any | None = None,
        tables: tuple[Any, ...] = (),
    ) -> dict[str, Any]:
        collected = Engine.collect(app=app, router=router, tables=tables)
        Engine.install(collected)
        return collected

    @staticmethod
    def collect_bindings(
        *,
        app: Any | None = None,
        router: Any | None = None,
        tables: tuple[Any, ...] = (),
    ) -> dict[str, Any]:
        """Backward-compatible alias for :meth:`collect`."""
        return Engine.collect(app=app, router=router, tables=tables)

    @staticmethod
    def install_bindings(collected: dict[str, Any]) -> None:
        """Backward-compatible alias for :meth:`install`."""
        Engine.install(collected)

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


def provider_from_spec(spec: "EngineSpec | EngineProviderSpec") -> "EngineProvider":
    """Materialize a concrete :class:`EngineProvider` from a core provider/spec value."""
    if hasattr(spec, "spec"):
        return EngineProvider(spec.spec)  # type: ignore[arg-type]
    return EngineProvider(spec)


Provider = EngineProvider
