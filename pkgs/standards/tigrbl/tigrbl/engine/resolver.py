# tigrbl/tigrbl/v3/engine/resolver.py
from __future__ import annotations

import asyncio
import inspect
import hashlib
import json
import logging
import threading
from typing import Any, Callable, Optional

from ._engine import AsyncSession, Engine, Provider, Session
from .engine_spec import EngineSpec, EngineCfg

logger = logging.getLogger("uvicorn")

# Registry with strict precedence: op > model > router > app
_LOCK = threading.RLock()
_DEFAULT: Optional[Provider] = None
_API: dict[int, Provider] = {}
_TAB: dict[Any, Provider] = {}
_OP: dict[tuple[Any, str], Provider] = {}
_PROV_BY_KEY: dict[tuple, Provider] = {}
_SECRET_KEYS = {
    "pwd",
    "password",
    "pass",
    "secret",
    "token",
    "apikey",
    "api_key",
    "key",
}


def _stable_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))


def _hash_secret(value: object) -> str:
    encoded = str(value).encode("utf-8", "surrogatepass")
    return hashlib.sha256(encoded).hexdigest()


def _spec_key(spec: EngineSpec) -> tuple:
    mapping = dict(spec.mapping or {})
    norm: dict[str, object] = {}
    for key, value in mapping.items():
        if str(key).lower() in _SECRET_KEYS:
            norm[key] = {"__sha256__": _hash_secret(value)}
        else:
            norm[key] = value
    mapping_s = _stable_json(norm)
    pwd_hash = _hash_secret(spec.pwd) if spec.pwd is not None else None
    return (
        spec.kind,
        bool(spec.async_),
        spec.dsn,
        spec.path,
        bool(spec.memory),
        spec.pool,
        spec.user,
        pwd_hash,
        spec.host,
        spec.port,
        spec.name,
        int(spec.pool_size or 0),
        int(spec.max or 0),
        mapping_s,
    )


def _intern_provider(spec: EngineSpec, *, provider: Provider | None = None) -> Provider:
    key = _spec_key(spec)
    with _LOCK:
        existing = _PROV_BY_KEY.get(key)
        if existing is not None:
            return existing
        new_provider = provider or spec.to_provider()
        _PROV_BY_KEY[key] = new_provider
        return new_provider


def _with_class(obj: Any) -> list[Any]:
    """Return ``obj`` and its class when ``obj`` is an instance.

    This allows resolution to honor providers registered on classes even when
    an instance is supplied at lookup time.
    """
    return [obj] if isinstance(obj, type) else [obj, type(obj)]


def _coerce(ctx: Optional[EngineCfg]) -> Optional[Provider]:
    """
    Promote an @engine_ctx value to a lazy Provider.
    """
    logger.debug("_coerce called with ctx=%r", ctx)
    if ctx is None:
        logger.debug("_coerce: ctx is None")
        return None
    if isinstance(ctx, Provider):
        logger.debug("_coerce: ctx is already a Provider")
        return _intern_provider(ctx.spec, provider=ctx)
    if isinstance(ctx, Engine):
        logger.debug("_coerce: ctx is an Engine; returning provider")
        return _intern_provider(ctx.spec, provider=ctx.provider)
    if isinstance(ctx, EngineSpec):
        logger.debug("_coerce: ctx is an EngineSpec; converting to provider")
        return _intern_provider(ctx)
    spec = EngineSpec.from_any(ctx)
    logger.debug("_coerce: EngineSpec.from_any returned %r", spec)
    return _intern_provider(spec) if spec else None


# ---- registration -----------------------------------------------------------


def set_default(ctx: EngineCfg | None) -> None:
    """
    Register the app-level default Provider used when no API/table/op binds.
    """
    global _DEFAULT
    prov = _coerce(ctx)
    logger.debug("set_default: setting default provider to %r", prov)
    with _LOCK:
        _DEFAULT = prov


def register_api(router: Any, ctx: EngineCfg | None) -> None:
    """
    Register an API-level Provider.
    """
    prov = _coerce(ctx)
    logger.debug("register_api: router=%r coerced provider=%r", router, prov)
    if prov is None:
        logger.debug("register_api: no provider; skipping registration")
        return
    with _LOCK:
        _API[id(router)] = prov
        logger.debug("register_api: registered provider for router id %s", id(router))


def register_table(model: Any, ctx: EngineCfg | None) -> None:
    """
    Register a table/model-level Provider.
    """
    prov = _coerce(ctx)
    logger.debug("register_table: model=%r coerced provider=%r", model, prov)
    if prov is None:
        logger.debug("register_table: no provider; skipping registration")
        return
    with _LOCK:
        _TAB[model] = prov
        logger.debug("register_table: registered provider for model %r", model)


def register_op(model: Any, alias: str, ctx: EngineCfg | None) -> None:
    """
    Register an op-level Provider for (model, alias).
    """
    prov = _coerce(ctx)
    logger.debug(
        "register_op: model=%r alias=%r coerced provider=%r", model, alias, prov
    )
    if prov is None:
        logger.debug("register_op: no provider; skipping registration")
        return
    with _LOCK:
        _OP[(model, alias)] = prov
        logger.debug(
            "register_op: registered provider for model %r alias %s", model, alias
        )


# ---- resolution -------------------------------------------------------------


def resolve_provider(
    *,
    router: Any = None,
    model: Any = None,
    op_alias: str | None = None,
) -> Optional[Provider]:
    """
    Resolve the effective Provider using precedence:
        op > model > router > app(default)
    """
    logger.debug(
        "resolve_provider called with router=%r model=%r op_alias=%r",
        router,
        model,
        op_alias,
    )
    with _LOCK:
        if model is not None and op_alias is not None:
            logger.debug("resolve_provider: checking op-level provider")
            for m in _with_class(model):
                logger.debug(
                    "resolve_provider: looking for op provider for %r alias %s",
                    m,
                    op_alias,
                )
                p = _OP.get((m, op_alias))
                if p:
                    logger.debug("resolve_provider: found op-level provider %r", p)
                    return p
        if model is not None:
            logger.debug("resolve_provider: checking model-level provider")
            for m in _with_class(model):
                logger.debug("resolve_provider: looking for model provider %r", m)
                p = _TAB.get(m)
                if p:
                    logger.debug("resolve_provider: found model-level provider %r", p)
                    return p
        if router is not None:
            logger.debug("resolve_provider: checking router-level provider")
            for a in _with_class(router):
                logger.debug("resolve_provider: looking for router provider %r", a)
                # APIs are keyed by ``id`` to avoid relying on ``__hash__``
                p = _API.get(id(a))
                if p:
                    logger.debug("resolve_provider: found router-level provider %r", p)
                    return p
        logger.debug("resolve_provider: returning default provider %r", _DEFAULT)
        return _DEFAULT


SessionT = Session | AsyncSession


def acquire(
    *,
    router: Any = None,
    model: Any = None,
    op_alias: str | None = None,
) -> tuple[SessionT, Callable[[], None]]:
    """
    Acquire a DB session from the resolved Provider.

    Returns:
        (session, release_fn)

    Raises:
        RuntimeError: if no Provider can be resolved and no default is set.
    """
    logger.debug(
        "acquire called with router=%r model=%r op_alias=%r", router, model, op_alias
    )
    p = resolve_provider(router=router, model=model, op_alias=op_alias)
    if p is None:
        logger.debug("acquire: no provider resolved; raising error")
        raise RuntimeError(
            f"No database provider configured for op={op_alias} "
            f"model={getattr(model, '__name__', model)} "
            f"router={type(router).__name__ if router else None} and no default"
        )
    db: SessionT = p.session()
    logger.debug("acquire: session %r acquired from provider %r", db, p)

    def _release() -> None:
        logger.debug("_release: attempting to release session %r", db)
        close = getattr(db, "close", None)
        if callable(close):
            try:
                rv = close()
                logger.debug("_release: close returned %r", rv)
                if inspect.isawaitable(rv):
                    logger.debug("_release: awaiting asynchronous close")
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        logger.debug("_release: no running loop; using asyncio.run")
                        asyncio.run(rv)
                    else:
                        logger.debug("_release: scheduling close on running loop")
                        loop.create_task(rv)
                # If close is sync, it has already executed
            except Exception:
                logger.debug("_release: error during close", exc_info=True)
                # best-effort close; swallow to avoid masking handler errors
                pass
        logger.debug("_release: release complete for session %r", db)

    return db, _release


def iter_providers() -> list[Provider]:
    with _LOCK:
        out: list[Provider] = []
        if _DEFAULT is not None:
            out.append(_DEFAULT)
        out.extend(_API.values())
        out.extend(_TAB.values())
        out.extend(_OP.values())
    seen: set[int] = set()
    uniq: list[Provider] = []
    for provider in out:
        pid = id(provider)
        if pid not in seen:
            seen.add(pid)
            uniq.append(provider)
    return uniq


def warmup(*, ensure: bool = True) -> None:
    if not ensure:
        return
    for provider in iter_providers():
        provider.ensure()


def reset(*, dispose: bool = True) -> None:
    """Reset resolver state; optionally dispose any built engines."""
    global _DEFAULT
    with _LOCK:
        providers: list[Provider] = []
        if _DEFAULT is not None:
            providers.append(_DEFAULT)
        providers.extend(_API.values())
        providers.extend(_TAB.values())
        providers.extend(_OP.values())
        providers.extend(_PROV_BY_KEY.values())

        seen: set[int] = set()
        uniq: list[Provider] = []
        for provider in providers:
            pid = id(provider)
            if pid not in seen:
                seen.add(pid)
                uniq.append(provider)

        if dispose:
            for provider in uniq:
                try:
                    engine = getattr(provider, "_engine", None)
                    if engine is None:
                        continue
                    dispose_fn = getattr(engine, "dispose", None)
                    if dispose_fn is None:
                        continue
                    result = dispose_fn()
                    if inspect.isawaitable(result):
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            asyncio.run(result)
                        else:
                            loop.create_task(result)
                except Exception:
                    logger.debug("reset: error disposing engine", exc_info=True)

        _DEFAULT = None
        _API.clear()
        _TAB.clear()
        _OP.clear()
        _PROV_BY_KEY.clear()
