# autoapi/autoapi/v3/engine/_engine.py
from __future__ import annotations

from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Tuple, Union, Protocol, TYPE_CHECKING

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
    from .engine_spec import EngineSpec


@dataclass(frozen=True)
class Provider:
    """Lazily builds an engine + sessionmaker from an :class:`EngineSpec`."""

    spec: "EngineSpec"
    _engine: Any = None
    _maker: Optional[SessionFactory] = None

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


@dataclass
class Engine:
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
