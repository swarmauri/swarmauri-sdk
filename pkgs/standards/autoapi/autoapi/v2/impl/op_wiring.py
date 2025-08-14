# autoapi/v2/impl/op_wiring.py
from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Iterable, List, Optional, Type, Annotated

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
from ..types.op_verb_alias_provider import OpVerbAliasProvider  # back-compat
from ..hooks import Phase


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
    return "collection" if target in {
        "create", "list", "bulk_create", "bulk_update", "bulk_replace", "bulk_delete", "clear"
    } else "member"


def collect_all_specs_for_table(table: Type) -> List[OpSpec]:
    out: List[OpSpec] = []

    # 1) class-declared specs
    if issubclass(table, OpConfigProvider):
        out.extend(list(getattr(table, "__autoapi_ops__", ()) or []))

    # 2) method decorators (custom_op)
    for name in dir(table):
        meth = getattr(table, name, None)
        tag: OpSpec | None = getattr(meth, "__autoapi_custom_op__", None)
        if tag:
            out.append(OpSpec(**{**tag.__dict__, "table": table, "handler": meth}))

    # 3) imperative registry (highest precedence)
    out.extend(get_registered_ops(table))

    # 4) back-compat: __autoapi_verb_aliases__ → specs (RPC/method aliases only)
    if issubclass(table, OpVerbAliasProvider):
        raw = getattr(table, "__autoapi_verb_aliases__", {}) or {}
        if callable(raw):
            raw = raw()
        for tgt, alias in dict(raw).items():
            out.append(OpSpec(alias=alias, target=tgt, table=table, expose_routes=False))

    # Fill defaults & light de-dupe by (alias, target)
    seen: set[tuple[str, str]] = set()
    final: List[OpSpec] = []
    for s in out:
        key = (s.alias, s.target)
        if key in seen:
            continue
        seen.add(key)
        final.append(OpSpec(
            alias=s.alias, target=s.target, table=table,
            expose_routes=s.expose_routes, expose_rpc=s.expose_rpc, expose_method=s.expose_method,
            arity=s.arity or _arity_for(s.target), persist=s.persist, returns=s.returns,
            handler=s.handler, request_model=s.request_model, response_model=s.response_model,
            http_methods=s.http_methods, path_suffix=s.path_suffix, tags=s.tags,
            rbac_guard_op=s.rbac_guard_op or s.target, hooks=s.hooks,
        ))
    return final


# ──────────────────────────────────────────────────────────────────────────────
# Schema & HTTP helpers
# ──────────────────────────────────────────────────────────────────────────────
def _http_methods(spec: OpSpec) -> list[str]:
    if spec.http_methods:
        return list(spec.http_methods)
    return {
        "read": ["GET"], "list": ["GET"], "delete": ["DELETE"],
        "update": ["PATCH"], "replace": ["PUT"], "create": ["POST"],
        "bulk_create": ["POST"], "bulk_update": ["PATCH"], "bulk_replace": ["PUT"], "bulk_delete": ["DELETE"],
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
    return spec.request_model or _schema(table, verb=(spec.target if spec.target != "custom" else "create"))


def _out_model(table: Type, spec: OpSpec):
    if spec.returns == "raw":
        return spec.response_model or None
    if spec.target == "create":  # canonical create often uses 201 + body-less response_model
        return spec.response_model or None
    # default to canonical target (delete returns read_out for parity unless overridden)
    return spec.response_model or _schema(table, verb=("read" if spec.target == "delete" else spec.target))


# ──────────────────────────────────────────────────────────────────────────────
# Main attacher
# ──────────────────────────────────────────────────────────────────────────────
def attach_op_specs(api, router, table: Type) -> None:
    """
    Mount OpSpec-defined verbs across:
      - routes
      - rpc
      - methods (api.methods.Resource.<alias>, plus api.core ResourceAlias callable)
    """
    specs = collect_all_specs_for_table(table)

    # PK metadata
    pk_col = next(iter(table.__table__.primary_key.columns))
    pk_name = pk_col.name
    pk_type = getattr(pk_col.type, "python_type", str)

    # detect sync/async DB mode identical to routes_builder
    is_async = (bool(api.get_async_db) if api.get_db is None else issubclass(table, AsyncCapable))
    provider = api.get_async_db if is_async else api.get_db
    DBDep = Annotated[AsyncSession, Depends(provider)] if is_async else Annotated[Session, Depends(provider)]

    # authz guard (re-use same pattern as routes_builder)
    def _guard(scope: str):
        async def inner(request: Request):
            if api._authorize and not api._authorize(scope, request):
                http_exc, _, _ = create_standardized_error(403, rpc_code=-32095)
                raise http_exc
        return Depends(inner)

    resource_name = table.__name__

    for spec in specs:
        # Ensure RPC method exists for this alias/custom BEFORE wiring the route & runners
        verb_camel = "".join(w.title() for w in (spec.alias if spec.target == "custom" else spec.alias).split("_"))
        target_camel = "".join(w.title() for w in spec.target.split("_"))
        alias_mid = f"{resource_name}.{verb_camel}"
        canon_mid = f"{resource_name}.{target_camel}"

        if spec.expose_rpc:
            if spec.target == "custom" and spec.handler:
                IN = _in_model(table, spec) or dict
                OUT = _out_model(table, spec)

                async def _core(payload, db, _h=spec.handler):
                    # normalized handler signature: (table, *, ctx, db, request, payload)
                    return await _h(table, ctx={}, db=db, request=None, payload=payload)

                rpc_fn = _wrap_rpc(_core, IN, OUT, pk_name, table)
                api.rpc.add(alias_mid, rpc_fn)
            else:
                # alias → canonical: just point to the same RPC handler
                # (canonical RPC must already be registered by routes_builder)
                if canon_mid in api.rpc:
                    api.rpc.add(alias_mid, api.rpc[canon_mid])
                else:
                    # If canonical not present yet, skip for now; route handler will still work via _invoke
                    pass

        # REST wiring
        if spec.expose_routes:
            In = _in_model(table, spec)
            Out = _out_model(table, spec)
            path = _rest_path(table, spec)
            methods = _http_methods(spec)

            # Build endpoint signature: (request[, item_id][, p], db)
            params: list[inspect.Parameter] = [
                inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)
            ]

            if "{item_id}" in path:
                params.append(
                    inspect.Parameter("item_id", inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                      annotation=Annotated[pk_type, Path(...)]))

            needs_query = spec.target == "list"
            needs_body = (In is not None) and (spec.target not in {"read", "delete", "clear", "list"})

            if needs_query:
                params.append(
                    inspect.Parameter("p", inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                      annotation=Annotated[In, Depends()]))
            elif needs_body:
                params.append(
                    inspect.Parameter("p", inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                      annotation=Annotated[In, Body(embed=False)]))

            params.append(inspect.Parameter("db", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=DBDep))

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
                    return obj.model_dump(exclude_unset=True, exclude_none=True) if hasattr(obj, "model_dump") else obj

                # Build RPC params mirroring routes_builder
                if spec.target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_delete"}:
                    rpc_params = [_dump(x) for x in (p or [])]
                elif spec.target == "read":
                    rpc_params = {pk_name: item_id}
                elif spec.target == "delete":
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
                    # custom; member gets id alongside payload
                    rpc_params = ({pk_name: item_id, **(_dump(p) if p else {})}
                                  if "{item_id}" in path else (_dump(p) if p else {}))

                env = _RPCReq(id=None, method=(alias_mid if spec.target == "custom" else alias_mid), params=rpc_params)
                ctx = {"request": req, "db": db, "env": env, "params": env.params}
                ctx.update(getattr(req.state, "ctx", {}))

                # Per-verb pre-hooks
                for h in sorted([x for x in spec.hooks if x.phase.name == "PRE_TX_BEGIN"], key=lambda x: x.order):
                    if h.when is None or h.when(ctx):
                        await h.fn(table=table, ctx=ctx, db=db, request=req, payload=p)

                # Execute via same _invoke engine as canonical endpoints
                if isinstance(db, AsyncSession):
                    def exec_fn(_m, _p, _db=db):
                        return _db.run_sync(lambda s: api.rpc[_m](_p, s))
                else:
                    def exec_fn(_m, _p, _db=db):
                        return api.rpc[_m](_p, _db)

                result = await _invoke(api, alias_mid if spec.expose_rpc else (canon_mid if spec.target != "custom" else alias_mid),
                                       params=rpc_params, ctx=ctx, exec_fn=exec_fn)

                # Per-verb post-hooks
                for h in sorted([x for x in spec.hooks if x.phase.name == "POST_TX_END"], key=lambda x: x.order):
                    if h.when is None or h.when(ctx):
                        await h.fn(table=table, ctx=ctx, db=db, request=req, payload=p)

                return result

            _impl.__name__ = f"opspec_{spec.alias}_{resource_name}"
            wrapped = inspect.signature(lambda: None)  # dummy to avoid mypy warnings
            wrapped = _impl  # for FastAPI, the function object is sufficient
            wrapped.__signature__ = inspect.Signature(parameters=params)

            # deps (authn + rbac)
            guard_scope = f"{resource_name}.{''.join(w.title() for w in (spec.rbac_guard_op or spec.target).split('_'))}"
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

        # In-process method runners (api.methods.Resource.<alias>) + convenience core callable
        if spec.expose_method:
            def _make_runner(method_id: str):
                def _runner(payload, *, db=None, _method=method_id, _api=api):
                    """
                    Call like: api.methods.Resource.alias(...).
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

            runner = _make_runner(alias_mid if spec.target == "custom" else alias_mid)
            api._method_ids[alias_mid] = runner
            _attach_ns(api.methods, resource_name, spec.alias, runner)

            # Also attach a flat convenience on api.core: ResourceAlias(payload, db=...)
            async def _core_callable(payload, *, db=None, _mid=alias_mid, _api=api):
                if db is None:
                    if _api.get_db is None:
                        raise TypeError(
                            "core callable requires db=... when get_db is not configured"
                        )
                    gen = _api.get_db()
                    s = next(gen)
                    try:
                        return _api.rpc[_mid](payload, s)
                    finally:
                        try:
                            next(gen)
                        except StopIteration:
                            pass
                return _api.rpc[_mid](payload, db)

            setattr(api.core, f"{resource_name}{''.join(w.title() for w in spec.alias.split('_'))}", _core_callable)
