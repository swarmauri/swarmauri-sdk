# autoapi/v2/impl/op_wiring.py
from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, List, Type, Annotated

from fastapi import Depends, Request, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .schema import _schema
from .rpc_adapter import _wrap_rpc
from ._runner import _invoke
from ..jsonrpc_models import _RPCReq, create_standardized_error
from ..mixins import AsyncCapable
from ..ops.spec import OpSpec
from ..ops.registry import get_registered_ops
from ..types.op_config_provider import OpConfigProvider
from ..naming import snake_to_camel
from inspect import iscoroutinefunction


def _ensure_model_namespaces(table):
    if not hasattr(table, "schemas"):
        setattr(table, "schemas", SimpleNamespace())
    if not hasattr(table, "methods"):
        setattr(table, "methods", SimpleNamespace())
    if not hasattr(table, "rpc"):
        setattr(table, "rpc", SimpleNamespace())
    if not hasattr(table, "core"):
        setattr(table, "core", SimpleNamespace())
    if not hasattr(table, "core_raw"):
        setattr(table, "core_raw", SimpleNamespace())
    if not hasattr(table, "hooks"):
        setattr(table, "hooks", SimpleNamespace())
    return table  # convenience


# ──────────────────────────────────────────────────────────────────────────────
# Small helper (avoid importing from routes_builder to prevent cycles)
# ──────────────────────────────────────────────────────────────────────────────
def _attach_ns(root: Any, resource: str, name: str, fn: Any) -> None:
    ns = getattr(root, resource, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(root, resource, ns)
    setattr(ns, name, fn)


# ──────────────────────────────────────────────────────────────────────────────
# Spec collection (class attr → decorators → registry → legacy alias map)
# ──────────────────────────────────────────────────────────────────────────────
def _arity_for(target: str) -> str:
    return (
        "collection"
        if target
        in {
            "create",
            "list",
            "bulk_create",
            "bulk_update",
            "bulk_replace",
            "bulk_delete",
            "clear",
        }
        else "member"
    )


def collect_all_specs_for_table(table: Type) -> List[OpSpec]:
    out: List[OpSpec] = []

    # 1) class-declared specs
    if issubclass(table, OpConfigProvider):
        out.extend(list(getattr(table, "__autoapi_ops__", ()) or []))

    # 2) method decorators (custom_op)
    for name in dir(table):
        try:
            meth = getattr(table, name, None)
        except Exception:
            continue
        tag: OpSpec | None = getattr(meth, "__autoapi_custom_op__", None)
        if tag:
            out.append(OpSpec(**{**tag.__dict__, "table": table, "handler": meth}))

    # 3) imperative registry (highest precedence)
    out.extend(get_registered_ops(table))

    # 4) back-compat: __autoapi_verb_aliases__ → specs (RPC/method aliases only)
    raw = getattr(table, "__autoapi_verb_aliases__", {}) or {}
    policy = getattr(table, "__autoapi_verb_alias_policy__", "both")
    if callable(raw):
        raw = raw()
    for tgt, alias in dict(raw).items():
        if policy == "canonical_only":
            continue
        out.append(
            OpSpec(
                alias=alias,
                target=tgt,
                table=table,
                expose_routes=False,
                expose_rpc=True,
                expose_method=True,
            )
        )

    # Fill defaults & light de-dupe by (alias, target)
    seen: set[tuple[str, str]] = set()
    final: List[OpSpec] = []
    for s in out:
        key = (s.alias, s.target)
        if key in seen:
            continue
        seen.add(key)
        final.append(
            OpSpec(
                alias=s.alias,
                target=s.target,
                table=table,
                expose_routes=s.expose_routes,
                expose_rpc=s.expose_rpc,
                expose_method=s.expose_method,
                arity=s.arity or _arity_for(s.target),
                persist=s.persist,
                returns=s.returns,
                handler=s.handler,
                request_model=s.request_model,
                response_model=s.response_model,
                http_methods=s.http_methods,
                path_suffix=s.path_suffix,
                tags=s.tags,
                rbac_guard_op=s.rbac_guard_op or s.target,
                hooks=s.hooks,
            )
        )
    return final


# ──────────────────────────────────────────────────────────────────────────────
# Schema & HTTP helpers
# ──────────────────────────────────────────────────────────────────────────────
def _http_methods(spec: OpSpec) -> list[str]:
    if spec.http_methods:
        return list(spec.http_methods)
    return {
        "read": ["GET"],
        "list": ["GET"],
        "delete": ["DELETE"],
        "update": ["PATCH"],
        "replace": ["PUT"],
        "create": ["POST"],
        "bulk_create": ["POST"],
        "bulk_update": ["PATCH"],
        "bulk_replace": ["PUT"],
        "bulk_delete": ["DELETE"],
        "clear": ["DELETE"],
    }.get(spec.target, ["POST"])


def _rest_path(table: Type, spec: OpSpec) -> str:
    # Return path *relative* to the router prefix (e.g., "/{tab}")
    if spec.target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_delete"}:
        return "/bulk"
    if spec.target == "clear":
        return ""
    if spec.target == "custom":
        seg = spec.path_suffix or spec.alias
        return f"/{{item_id}}/{seg}" if spec.arity == "member" else f"/{seg}"
    # canonical mapping
    return "/{item_id}" if spec.arity == "member" else ""


def _in_model(table: Type, spec: OpSpec):
    # For canonical targets, reuse their input schemas; for custom default to create's shape unless overridden
    return spec.request_model or _schema(
        table, verb=(spec.target if spec.target != "custom" else "create")
    )


def _out_model(table: Type, spec: OpSpec):
    if spec.returns == "raw":
        return spec.response_model or None
    if (
        spec.target == "create"
    ):  # canonical create often uses 201 + body-less response_model
        return spec.response_model or None
    # default to canonical target (delete returns read_out for parity unless overridden)
    return spec.response_model or _schema(
        table, verb=("read" if spec.target == "delete" else spec.target)
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main attacher
# ──────────────────────────────────────────────────────────────────────────────
def attach_op_specs(api, router, table: Type) -> None:
    """
    Mount OpSpec-defined verbs across:
      - REST routes (if expose_routes)
      - RPC ids on api.rpc (if expose_rpc)
      - api.methods.Resource.<alias> runners (if expose_method)

    Additionally, ALWAYS project each OpSpec onto the model class:
      - table.schemas.{AliasCamel}In / {AliasCamel}Out
      - table.methods.<alias>         (runner that opens DB if needed)
      - table.rpc.{AliasCamel}        (normalized handler; uses api.rpc when present, otherwise local wrap)
      - table.core.<alias>            (canonical core or custom raw core; falls back to runner)
      - table.core_raw.<alias>        (payload → *args mapper; requires db=...)
      - table.hooks.<alias>           (list of hooks for introspection)
    """
    specs = collect_all_specs_for_table(table)

    # PK metadata
    pk_col = next(iter(table.__table__.primary_key.columns))
    pk_name = pk_col.name
    pk_type = getattr(pk_col.type, "python_type", str)

    # detect sync/async DB mode identical to routes_builder
    is_async = (
        bool(api.get_async_db)
        if api.get_db is None
        else issubclass(table, AsyncCapable)
    )
    provider = api.get_async_db if is_async else api.get_db
    DBDep = (
        Annotated[AsyncSession, Depends(provider)]
        if is_async
        else Annotated[Session, Depends(provider)]
    )

    # authz guard (re-use same pattern as routes_builder)
    def _guard(scope: str):
        async def inner(request: Request):
            if api._authorize and not api._authorize(scope, request):
                http_exc, _, _ = create_standardized_error(403, rpc_code=-32095)
                raise http_exc

        return Depends(inner)

    resource_name = table.__name__

    # ── ensure model namespaces exist
    for _ns in ("schemas", "methods", "rpc", "core", "core_raw", "hooks"):
        if not hasattr(table, _ns):
            setattr(table, _ns, SimpleNamespace())

    # small helpers
    def _alias_camel(s: str) -> str:
        return "".join(w.title() for w in s.split("_"))

    def _mk_local_core_for_custom(handler):
        # normalized custom core that accepts (payload, db)
        async def _custom_core(payload, db, _h=handler, _t=table):
            res = _h(_t, ctx={}, db=db, request=None, payload=payload)
            # Support both sync/async custom handlers
            if inspect.isawaitable(res):
                return await res
            return res

        return _custom_core

    def _mk_core_raw(core_fn, target: str):
        # async wrapper that maps payload → positional args and calls canonical core
        async def _core_raw(
            payload, *, db=None, _core=core_fn, _verb=target, _pk=pk_name
        ):
            if _core is None:
                raise RuntimeError("core callable is not available for this OpSpec")
            if db is None:
                raise TypeError("table.core_raw requires db=...")

            def _dump(o):
                return (
                    o.model_dump(exclude_unset=True, exclude_none=True)
                    if hasattr(o, "model_dump")
                    else o
                )

            def _build_args(_p):
                if _verb in ("create", "list"):
                    return (_p,)
                if _verb in (
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_delete",
                ):
                    if isinstance(_p, list):
                        return ([_dump(x) for x in _p],)
                    return (_dump(_p),)
                if _verb == "clear":
                    return ()
                if _verb in ("read", "delete"):
                    d = _dump(_p)
                    return (d[_pk],)
                if _verb in ("update", "replace"):
                    d = _dump(_p)
                    body = {k: v for k, v in d.items() if k != _pk}
                    return (d[_pk], body)
                # custom/default: pass full payload
                return (_p,)

            if hasattr(db, "run_sync"):  # AsyncSession
                return await db.run_sync(lambda s: _core(*_build_args(payload), s))
            return _core(*_build_args(payload), db)

        return _core_raw

    for spec in specs:
        # Compute models (used for REST + class schemas)
        In = _in_model(table, spec)
        Out = _out_model(table, spec)

        alias_mid = f"{resource_name}.{spec.alias}"
        canon_mid = f"{resource_name}.{spec.target}"
        alias_camel = _alias_camel(spec.alias)
        target_camel = snake_to_camel(spec.target)

        # Determine the canonical core (if any) or a custom core
        canon_core = getattr(api.core, f"{resource_name}{target_camel}", None)
        core_for_model = None
        if spec.target == "custom" and spec.handler:
            core_for_model = _mk_local_core_for_custom(spec.handler)
        else:
            core_for_model = canon_core  # may be None if canonical not bound yet

        # ────────────────────────────────────────────────────────────
        # RPC exposure on API
        # ────────────────────────────────────────────────────────────
        if spec.expose_rpc:
            if spec.target == "custom" and spec.handler:
                # normalized handler signature: (table, *, ctx, db, request, payload)
                async def _core(payload, db, _h=spec.handler, _t=table):
                    res = _h(_t, ctx={}, db=db, request=None, payload=payload)
                    if inspect.isawaitable(res):
                        return await res
                    return res

                rpc_fn = _wrap_rpc(_core, In or dict, Out, pk_name, table)
                api.rpc.add(alias_mid, rpc_fn)
            else:
                # alias → canonical: reuse canonical rpc if present
                if canon_mid in api.rpc:
                    api.rpc.add(alias_mid, api.rpc[canon_mid])
                # else: skip now; local table.rpc below will still work

        # ────────────────────────────────────────────────────────────
        # REST route
        # ────────────────────────────────────────────────────────────
        if spec.expose_routes:
            path = _rest_path(table, spec)
            methods = _http_methods(spec)

            # Build endpoint signature: (request[, item_id][, p], db)
            params: list[inspect.Parameter] = [
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                )
            ]
            if "{item_id}" in path:
                params.append(
                    inspect.Parameter(
                        "item_id",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[pk_type, Path(...)],
                    )
                )

            needs_query = spec.target == "list"
            needs_body = (In is not None) and (
                spec.target not in {"read", "delete", "clear", "list"}
            )

            if needs_query:
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[In, Depends()],
                    )
                )
            elif needs_body:
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[In, Body(embed=False)],
                    )
                )

            params.append(
                inspect.Parameter(
                    "db", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=DBDep
                )
            )

            async def _impl(**kw):
                req: Request = kw.pop("request")
                db = kw.pop("db")
                p = kw.pop("p", None)
                item_id = kw.pop("item_id", None)

                # Ensure ctx
                if getattr(req.state, "ctx", None) is None:
                    req.state.ctx = {}
                req.state.ctx["__op_alias__"] = spec.alias
                req.state.ctx["__op_target__"] = spec.target
                req.state.ctx["__op_persist_policy__"] = spec.persist
                if spec.persist == "skip":
                    req.state.ctx["__autoapi_skip_persist__"] = True

                def _dump(obj):
                    return (
                        obj.model_dump(exclude_unset=True, exclude_none=True)
                        if hasattr(obj, "model_dump")
                        else obj
                    )

                # Build RPC params mirroring routes_builder
                if spec.target in {
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_delete",
                }:
                    rpc_params = [_dump(x) for x in (p or [])]
                elif spec.target in {"read", "delete"}:
                    rpc_params = {pk_name: item_id}
                elif spec.target in {"update", "replace"}:
                    rpc_params = {pk_name: item_id, **_dump(p)}
                elif spec.target == "list":
                    rpc_params = _dump(p)
                elif spec.target == "clear":
                    rpc_params = {}
                elif spec.target == "create":
                    rpc_params = _dump(p)
                else:
                    # custom; member gets id alongside payload if present in path
                    rpc_params = (
                        {pk_name: item_id, **(_dump(p) if p else {})}
                        if "{item_id}" in path
                        else (_dump(p) if p else {})
                    )

                env = _RPCReq(id=None, method=alias_mid, params=rpc_params)
                ctx = {"request": req, "db": db, "env": env, "params": env.params}
                ctx.update(getattr(req.state, "ctx", {}))

                # Per-verb pre-hooks
                for h in sorted(
                    [x for x in spec.hooks if x.phase.name == "PRE_TX_BEGIN"],
                    key=lambda x: x.order,
                ):
                    if h.when is None or h.when(ctx):
                        await h.fn(table=table, ctx=ctx, db=db, request=req, payload=p)

                # Execute via same _invoke engine as canonical endpoints
                if isinstance(db, AsyncSession):

                    def exec_fn(_m, _p, _db=db):
                        return _db.run_sync(lambda s: api.rpc[_m](_p, s))
                else:

                    def exec_fn(_m, _p, _db=db):
                        return api.rpc[_m](_p, _db)

                result = await _invoke(
                    api,
                    alias_mid
                    if spec.expose_rpc
                    else (canon_mid if spec.target != "custom" else alias_mid),
                    params=rpc_params,
                    ctx=ctx,
                    exec_fn=exec_fn,
                )

                # Per-verb post-hooks
                for h in sorted(
                    [x for x in spec.hooks if x.phase.name == "POST_TX_END"],
                    key=lambda x: x.order,
                ):
                    if h.when is None or h.when(ctx):
                        await h.fn(table=table, ctx=ctx, db=db, request=req, payload=p)

                return result

            _impl.__name__ = f"opspec_{spec.alias}_{resource_name}"
            wrapped = _impl
            wrapped.__signature__ = inspect.Signature(parameters=params)

            # deps (authn + rbac)
            guard_scope = (
                f"{resource_name}.{snake_to_camel(spec.rbac_guard_op or spec.target)}"
            )
            deps = [_guard(guard_scope)]
            if guard_scope not in api._allow_anon:
                deps.insert(0, api._authn_dep)

            router.add_api_route(
                _rest_path(table, spec),
                wrapped,
                methods=methods,
                response_model=Out,
                dependencies=deps,
                tags=list(spec.tags or (resource_name,)),
                name=f"{resource_name} - {spec.alias}",
                summary=f"{resource_name} - {spec.alias}",
            )

        # ────────────────────────────────────────────────────────────
        # api.methods runner (public in-process)
        # ────────────────────────────────────────────────────────────
        def _make_runner(method_id: str):
            def _runner(payload, *, db=None, _method=method_id, _api=api):
                """
                Call like: api.methods.Resource.alias(...)
                Opens a sync session if needed (mirrors routes_builder).
                """
                if db is None:
                    if _api.get_db is None:
                        raise TypeError(
                            "Supply a Session via db=... or configure get_db on AutoAPI()"
                        )
                    gen = _api.get_db()
                    db_ = next(gen)
                    try:
                        return _api.rpc[_method](payload, db_)
                    finally:
                        try:
                            next(gen)  # close
                        except StopIteration:
                            pass
                else:
                    return _api.rpc[_method](payload, db)

            return _runner

        if spec.expose_method:
            runner = _make_runner(alias_mid)
            api._method_ids[alias_mid] = runner
            _attach_ns(api.methods, resource_name, spec.alias, runner)

        # Also expose a convenience callable on api.core for the alias.
        if spec.target == "custom":
            core_alias = core_for_model or (
                lambda payload, *, db=None: api.rpc[alias_mid](payload, db)
            )
        else:
            core_alias = getattr(api.core, f"{resource_name}{target_camel}", None) or (
                lambda payload, *, db=None: api.rpc[alias_mid](payload, db)
            )
        setattr(api.core, f"{resource_name}{_alias_camel(spec.alias)}", core_alias)
        _attach_ns(api.core, resource_name, spec.alias, core_alias)

        # ────────────────────────────────────────────────────────────
        # PROJECT spec ONTO THE MODEL CLASS (schemas / methods / rpc / core / core_raw / hooks)
        # ────────────────────────────────────────────────────────────

        # 1) Schemas on model + register into api._schemas for discovery
        if isinstance(In, type) and In is not dict:
            setattr(table.schemas, f"{alias_camel}In", In)
            if f"{resource_name}{alias_camel}In" not in api._schemas:
                api._schemas[f"{resource_name}{alias_camel}In"] = In
                setattr(api.schemas, f"{resource_name}{alias_camel}In", In)
        if Out is not None and isinstance(Out, type) and Out is not dict:
            setattr(table.schemas, f"{alias_camel}Out", Out)
            if f"{resource_name}{alias_camel}Out" not in api._schemas:
                api._schemas[f"{resource_name}{alias_camel}Out"] = Out
                setattr(api.schemas, f"{resource_name}{alias_camel}Out", Out)

        # 2) rpc on model (prefer api.rpc if present; otherwise local wrap around core)
        if alias_mid in api.rpc:
            setattr(
                table.rpc,
                alias_camel,
                lambda payload, db, _mid=alias_mid, _api=api: _api.rpc[_mid](
                    payload, db
                ),
            )
        else:
            # Local normalized callable not registered in api.rpc (respects IN/OUT)
            local_rpc = (
                _wrap_rpc(core_for_model, In or dict, Out, pk_name, table)
                if core_for_model
                else None
            )
            if local_rpc is None:
                # fallback to canonical rpc if available
                def _fallback_rpc(payload, db, _mid=canon_mid, _api=api):
                    return _api.rpc[_mid](payload, db)

                setattr(table.rpc, alias_camel, _fallback_rpc)
            else:
                setattr(table.rpc, alias_camel, local_rpc)

        # 3) methods on model (always; use model.rpc so it works even if expose_rpc=False)
        def _model_runner(
            payload, *, db=None, _tab_rpc=getattr(table.rpc, alias_camel)
        ):
            if db is None:
                if api.get_db is None:
                    raise TypeError(
                        "Supply a Session via db=... or configure get_db on AutoAPI()"
                    )
                gen = api.get_db()
                db_ = next(gen)
                try:
                    return _tab_rpc(payload, db_)
                finally:
                    try:
                        next(gen)  # close
                    except StopIteration:
                        pass
            else:
                return _tab_rpc(payload, db)

        setattr(table.methods, spec.alias, _model_runner)

        # 4) hooks on model (introspection)
        setattr(table.hooks, spec.alias, list(spec.hooks or ()))

        # 5) core + core_raw on model
        setattr(table.core, spec.alias, core_for_model or _model_runner)
        setattr(
            table.core_raw,
            spec.alias,
            _mk_core_raw(
                core_for_model or (lambda payload, db: api.rpc[alias_mid](payload, db)),
                spec.target,
            ),
        )


def _apply_spec_to_model(
    api, table: type, spec: OpSpec, *, IN, OUT, pk_name: str, runner
):
    """
    Mirror one OpSpec into the model's namespaces:
      • table.schemas.{AliasCamel}In / {AliasCamel}Out
      • table.methods.<alias>           (runner that opens DB using api.get_db if needed)
      • table.rpc.{AliasCamel}          (call-through to api.rpc["Model.alias"])
      • table.core.<alias>              (canonical core or custom raw core)
      • table.core_raw.<alias>          (async wrapper accepting payload, *, db)
      • table.hooks.<alias>             (list of hooks)
    Also registers alias/custom schemas onto api._schemas (so class-binding sees them).
    """
    resource = table.__name__
    alias_camel = snake_to_camel(spec.alias)
    alias_mid = f"{resource}.{spec.alias}"

    _ensure_model_namespaces(table)

    # ── schemas on model + api._schemas (so routes_builder can mirror them too)
    if isinstance(IN, type) and IN is not dict:
        setattr(table.schemas, f"{alias_camel}In", IN)
        api._schemas.setdefault(f"{resource}{alias_camel}In", IN)
        setattr(api.schemas, f"{resource}{alias_camel}In", IN)
    if OUT is not None and isinstance(OUT, type) and OUT is not dict:
        setattr(table.schemas, f"{alias_camel}Out", OUT)
        api._schemas.setdefault(f"{resource}{alias_camel}Out", OUT)
        setattr(api.schemas, f"{resource}{alias_camel}Out", OUT)

    # ── methods on model (same runner you attached to api.methods)
    setattr(table.methods, spec.alias, runner)

    # right after methods assignment
    if not hasattr(table, "handlers"):
        setattr(table, "handlers", SimpleNamespace())
    setattr(table.handlers, spec.alias, api.rpc[f"{table.__name__}.{spec.alias}"])

    # ── rpc on model (call-through to api.rpc)
    def _rpc(payload, db, _mid=alias_mid, _api=api):
        return _api.rpc[_mid](payload, db)

    setattr(table.rpc, alias_camel, _rpc)

    # ── core + core_raw on model
    # For canonical alias → reuse canonical core. For custom → derive from handler.
    canon_name = f"{resource}{snake_to_camel(spec.target)}"
    canon_core = getattr(api.core, canon_name, None)

    if spec.target == "custom" and spec.handler:
        # Raw core that invokes the custom handler with a normalized signature
        async def _custom_core(payload, db, _h=spec.handler, _t=table):
            res = _h(_t, ctx={}, db=db, request=None, payload=payload)
            if iscoroutinefunction(_h) or hasattr(res, "__await__"):
                return await res
            return res

        core_fn = _custom_core
    else:
        # alias of canonical
        core_fn = canon_core  # may be None if canonical not bound yet

    # Attach to table.core (if still None, fall back to runner so calls won't explode)
    setattr(table.core, spec.alias, (core_fn or runner))

    # core_raw accepts (payload, *, db) and handles AsyncSession/Session uniformly
    async def _core_raw(
        payload, *, db=None, _core=core_fn, _verb=spec.target, _pk=pk_name
    ):
        # If canonical core is missing (rare race), just use the rpc runner
        if _core is None:
            return (
                await runner(payload, db=db)
                if iscoroutinefunction(runner)
                else runner(payload, db=db)
            )

        # Build args like routes_builder.core_raw for canonical verbs
        def _dump(o):
            return (
                o.model_dump(exclude_unset=True, exclude_none=True)
                if hasattr(o, "model_dump")
                else o
            )

        def _build_args(_p):
            if _verb in ("create", "list"):
                return (_p,)
            if _verb in ("bulk_create", "bulk_update", "bulk_replace", "bulk_delete"):
                if isinstance(_p, list):
                    return ([_dump(x) for x in _p],)
                return (_dump(_p),)
            if _verb == "clear":
                return ()
            if _verb in ("read", "delete"):
                d = _dump(_p)
                return (d[_pk],)
            if _verb in ("update", "replace"):
                d = _dump(_p)
                body = {k: v for k, v in d.items() if k != _pk}
                return (d[_pk], body)
            # custom: pass through whole payload
            return (_p,)

        if db is None:
            # No auto-open here; model core_raw expects a db (mirror api.core_raw behavior)
            raise TypeError("table.core_raw requires db=...")

        if hasattr(db, "run_sync"):  # AsyncSession
            return await db.run_sync(lambda s: _core(*_build_args(payload), s))
        return _core(*_build_args(payload), db)

    setattr(table.core_raw, spec.alias, _core_raw)

    # ── hooks on model: append per-alias list (introspection)
    existing = getattr(table.hooks, spec.alias, None)
    if existing is None:
        setattr(table.hooks, spec.alias, list(spec.hooks or ()))
    else:
        existing.extend(list(spec.hooks or ()))
