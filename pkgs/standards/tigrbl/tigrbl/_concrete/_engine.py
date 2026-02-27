# tigrbl/tigrbl/v3/engine/_engine.py
from __future__ import annotations

from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
import asyncio
import inspect
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Union,
    Protocol,
    TYPE_CHECKING,
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


def _read_engine_attr(obj: Any):
    for key in ("engine", "db", "database", "engine_provider", "db_provider"):
        if hasattr(obj, key):
            return getattr(obj, key)
    for key in ("tigrbl_engine", "tigrbl_db", "get_engine"):
        fn = getattr(obj, key, None)
        if callable(fn):
            return fn()
    return None


def _iter_op_decorators(model: Any) -> dict[tuple[Any, str], Mapping[str, Any]]:
    from types import SimpleNamespace

    out: dict[tuple[Any, str], Mapping[str, Any]] = {}
    handlers = getattr(model, "handlers", None)
    if handlers:
        for alias in dir(handlers):
            handler = getattr(handlers, alias, None)
            if handler is None:
                continue
            for slot in ("handler", "core"):
                fn = getattr(handler, slot, None)
                if callable(fn) and (
                    hasattr(fn, "__tigrbl_engine_ctx__") or hasattr(fn, "__tigrbl_db__")
                ):
                    spec = getattr(fn, "__tigrbl_engine_ctx__", None)
                    if spec is None:
                        spec = getattr(fn, "__tigrbl_db__")
                    out[(model, alias)] = {"engine": spec}
                    break

    rpc_namespace = getattr(model, "rpc", SimpleNamespace())
    for alias in dir(rpc_namespace):
        if alias.startswith("_"):
            continue
        fn = getattr(rpc_namespace, alias, None)
        if callable(fn) and (
            hasattr(fn, "__tigrbl_engine_ctx__") or hasattr(fn, "__tigrbl_db__")
        ):
            spec = getattr(fn, "__tigrbl_engine_ctx__", None)
            if spec is None:
                spec = getattr(fn, "__tigrbl_db__")
            out[(model, alias)] = {"engine": spec}

    return out


def _iter_declared_ops(model: Any) -> dict[tuple[Any, str], Mapping[str, Any]]:
    out: dict[tuple[Any, str], Mapping[str, Any]] = {}
    for spec in getattr(model, "__tigrbl_ops__", ()) or ():
        engine = getattr(spec, "engine", None)
        alias = getattr(spec, "alias", None)
        if engine is not None and alias:
            out[(model, alias)] = {"engine": engine}
    return out


def collect_engine_bindings(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> dict[str, Any]:
    app_engine = _read_engine_attr(app) if app is not None else None
    router_engine = _read_engine_attr(router) if router is not None else None

    table_bindings: dict[Any, Any] = {}
    ops: dict[tuple[Any, str], Any] = {}
    tables = tuple(tables)

    for model in tables:
        cfg = getattr(model, "table_config", None)
        model_engine = None
        if isinstance(cfg, Mapping):
            for key in ("engine", "db", "database", "engine_provider", "db_provider"):
                if key in cfg:
                    model_engine = cfg[key]
                    break
        if model_engine is None:
            model_engine = _read_engine_attr(model)
        if model_engine is not None:
            table_bindings[model] = model_engine

        for (decl_model, alias), op_cfg in _iter_op_decorators(model).items():
            ops[(decl_model, alias)] = op_cfg.get("engine")
        for (decl_model, alias), op_cfg in _iter_declared_ops(model).items():
            ops[(decl_model, alias)] = op_cfg.get("engine")

    router_map = (
        {router: router_engine}
        if router_engine is not None and router is not None
        else {}
    )
    return {
        "default": app_engine,
        "router": router_map,
        "tables": table_bindings,
        "ops": ops,
    }


def install_engine_bindings(collected: Mapping[str, Any]) -> None:
    from ..mapping.engine_resolver import (
        register_op,
        register_router,
        register_table,
        set_default,
    )

    default_db = collected.get("default")
    if default_db is not None:
        set_default(default_db)

    for router_obj, db in (collected.get("router") or {}).items():
        register_router(router_obj, db)

    for table_obj, db in (collected.get("tables") or {}).items():
        register_table(table_obj, db)

    for (model, alias), db in (collected.get("ops") or {}).items():
        register_op(model, alias, db)


def install_from_objects(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> dict[str, Any]:
    collected = collect_engine_bindings(app=app, router=router, tables=tables)
    install_engine_bindings(collected)
    return collected
