from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence

from .serde import SerdeMixin

if TYPE_CHECKING:  # pragma: no cover
    from .._spec.engine_spec import EngineCfg
    from .._spec.response_spec import ResponseSpec


class AppSpec(SerdeMixin, ABC):
    """Core interface for app-level specification payloads."""

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str | None: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @property
    @abstractmethod
    def engine(self) -> Optional["EngineCfg"]: ...

    @property
    @abstractmethod
    def routers(self) -> Sequence[Any]: ...

    @property
    @abstractmethod
    def ops(self) -> Sequence[Any]: ...

    @property
    @abstractmethod
    def tables(self) -> Sequence[Any]: ...

    @property
    @abstractmethod
    def schemas(self) -> Sequence[Any]: ...

    @property
    @abstractmethod
    def hooks(self) -> Sequence[Callable[..., Any]]: ...

    @property
    @abstractmethod
    def security_deps(self) -> Sequence[Callable[..., Any]]: ...

    @property
    @abstractmethod
    def deps(self) -> Sequence[Callable[..., Any]]: ...

    @property
    @abstractmethod
    def response(self) -> Optional["ResponseSpec"]: ...

    @property
    @abstractmethod
    def jsonrpc_prefix(self) -> str: ...

    @property
    @abstractmethod
    def system_prefix(self) -> str: ...

    @property
    @abstractmethod
    def middlewares(self) -> Sequence[Any]: ...

    @property
    @abstractmethod
    def lifespan(self) -> Optional[Callable[..., Any]]: ...

