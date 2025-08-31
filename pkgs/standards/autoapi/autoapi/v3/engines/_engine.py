# autoapi/autoapi/v3/engines/_engine.py
from __future__ import annotations

from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Union, Protocol

try:
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession
except Exception:  # pragma: no cover
    Session = object  # type: ignore
    AsyncSession = object  # type: ignore


class SessionFactory(Protocol):
    def __call__(self) -> Union[Session, AsyncSession]: ...


Builder = Callable[[], Tuple[Any, SessionFactory]]  # returns (engine, sessionmaker)


@dataclass(frozen=True)
class Provider:
    """
    Lazily builds an engine + sessionmaker; returns fresh sessions on demand.
    kind: "sync" | "async" (informational)
    """
    kind: str
    builder: Builder
    _engine: Any = None
    _maker: Optional[SessionFactory] = None

    def ensure(self) -> Tuple[Any, SessionFactory]:
        if self._maker is None:
            eng, mk = self.builder()
            object.__setattr__(self, "_engine", eng)
            object.__setattr__(self, "_maker", mk)
        return self._engine, self._maker  # type: ignore[return-value]

    def session(self) -> Union[Session, AsyncSession]:
        _, mk = self.ensure()
        return mk()  # type: ignore[misc]


@dataclass
class Engine:
    """
    Thin façade over a Provider with convenient (a)context managers.
    """
    provider: Provider

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
