from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Sequence,
    List as _List,
    Union as _Union,
)

from .common import (
    TIGRBL_AUTH_CONTEXT_ATTR,
    BaseModel,
    Body,
    Depends,
    Response,
    OpSpec,
    Path,
    Request,
    _coerce_parent_kw,
    _get_phase_chains,
    _make_list_query_dep,
    _request_model_for,
    _serialize_output,
    _validate_body,
    _validate_query,
    _executor,
    _status_for,
)

from .io_headers import _make_header_dep

from ...runtime.executor.types import _Ctx


logging.getLogger("uvicorn").debug("Loaded module v3/bindings/rest/collection")


def _ctx(model, alias, target, request, db, payload, parent_kw, api):
    ctx: Dict[str, Any] = {
        "request": request,
        "db": db,
        "payload": payload,
        "path_params": parent_kw,
        # expose both API router and FastAPI app; runtime opview resolution
        # relies on the app object, which must be hashable.
        "api": api if api is not None else getattr(request, "app", None),
        "app": getattr(request, "app", None),
        "model": model,
        "op": alias,
        "method": alias,
        "target": target,
        "env": SimpleNamespace(
            method=alias, params=payload, target=target, model=model
        ),
    }
    ac = getattr(request.state, TIGRBL_AUTH_CONTEXT_ATTR, None)
    if ac is not None:
        ctx["auth_context"] = ac
    return _Ctx(ctx)


def _sig(nested_vars, extra):
    params = [
        inspect.Parameter(
            nv,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, Path(...)],
        )
        for nv in nested_vars
    ]
    params.extend(extra)
    return inspect.Signature(params)


def _list_ann(tp):
    try:
        return list[tp]  # type: ignore[valid-type]
    except Exception:  # pragma: no cover - best effort
        return _List[tp]  # type: ignore[name-defined]


def _union(a, b):
    try:
        return a | b  # type: ignore[operator]
    except Exception:  # pragma: no cover - best effort
        return _Union[a, b]


def _make_collection_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    nested_vars: Sequence[str] | None = None,
    api: Any | None = None,
) -> Callable[..., Awaitable[Any]]:
    alias, target, nested_vars = sp.alias, sp.target, list(nested_vars or [])
    status_code = _status_for(sp)
    hdr_dep = _make_header_dep(model, alias)

    if target in {"list", "clear"}:
        list_dep = _make_list_query_dep(model, alias) if target == "list" else None

        async def _endpoint(
            request: Request,
            db: Any = Depends(db_dep),
            h: Mapping[str, Any] = Depends(hdr_dep),
            q: Mapping[str, Any] | None = None,
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            if q is not None:
                query = {**dict(q), **parent_kw}
                payload = _validate_query(model, alias, target, query)
            else:
                payload = dict(parent_kw)
            if isinstance(h, Mapping):
                payload = {**payload, **dict(h)}
            ctx = _ctx(model, alias, target, request, db, payload, parent_kw, api)
            ctx["response_serializer"] = lambda r: _serialize_output(
                model, alias, target, sp, r
            )
            phases = _get_phase_chains(model, alias)
            result = await _executor._invoke(
                request=request, db=db, phases=phases, ctx=ctx
            )
            if isinstance(result, Response):
                if sp.status_code is not None or result.status_code == 200:
                    result.status_code = status_code
                return result
            return result

        params = [
            inspect.Parameter(
                nv,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[str, Path(...)],
            )
            for nv in nested_vars
        ]
        params.extend(
            [
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                ),
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(db_dep)],
                ),
                inspect.Parameter(
                    "h",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Mapping[str, Any], Depends(hdr_dep)],
                ),
            ]
        )
        if target == "list":
            params.append(
                inspect.Parameter(
                    "q",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Mapping[str, Any], Depends(list_dep)],
                )
            )
        _endpoint.__signature__ = inspect.Signature(params)
    else:
        body_model = _request_model_for(sp, model)
        if body_model is None and sp.request_model is None and target == "custom":

            async def _endpoint(
                request: Request,
                db: Any = Depends(db_dep),
                h: Mapping[str, Any] = Depends(hdr_dep),
                **kw: Any,
            ):
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}
                _coerce_parent_kw(model, parent_kw)
                payload: Mapping[str, Any] = dict(parent_kw)
                if isinstance(h, Mapping):
                    payload = {**payload, **dict(h)}
                ctx = _ctx(model, alias, target, request, db, payload, parent_kw, api)

                def _serializer(r, _ctx=ctx):
                    out = _serialize_output(model, alias, target, sp, r)
                    temp = (
                        getattr(_ctx, "temp", {}) if isinstance(_ctx, Mapping) else {}
                    )
                    extras = (
                        temp.get("response_extras", {})
                        if isinstance(temp, Mapping)
                        else {}
                    )
                    if isinstance(out, dict) and isinstance(extras, dict):
                        out.update(extras)
                    return out

                ctx["response_serializer"] = _serializer
                phases = _get_phase_chains(model, alias)
                result = await _executor._invoke(
                    request=request,
                    db=db,
                    phases=phases,
                    ctx=ctx,
                )
                return result

            _endpoint.__signature__ = _sig(
                nested_vars,
                [
                    inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Request,
                    ),
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Any, Depends(db_dep)],
                    ),
                    inspect.Parameter(
                        "h",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Mapping[str, Any], Depends(hdr_dep)],
                    ),
                ],
            )
            _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
            _endpoint.__qualname__ = _endpoint.__name__
            _endpoint.__doc__ = (
                f"REST collection endpoint for {model.__name__}.{alias} ({target})"
            )
            return _endpoint

        base = body_model or Mapping[str, Any]
        body_required = target in {
            "create",
            "update",
            "replace",
            "merge",
        } or target.startswith("bulk_")
        if target.startswith("bulk_"):
            alias_ns = getattr(
                getattr(model, "schemas", None) or SimpleNamespace(), alias, None
            )
            item_model = getattr(alias_ns, "in_item", None) if alias_ns else None
            body_annotation = (
                _list_ann(item_model)
                if isinstance(item_model, type) and issubclass(item_model, BaseModel)
                else _list_ann(Mapping[str, Any])
                if body_model is None
                else base
            )
        elif target in {"create", "update", "replace", "merge"}:
            body_annotation = _union(
                base if body_model else Mapping[str, Any],
                _list_ann(Mapping[str, Any]),
            )
        else:
            body_annotation = _union(base, type(None)) if not body_required else base

        async def _endpoint(
            request: Request,
            db: Any = Depends(db_dep),
            h: Mapping[str, Any] = Depends(hdr_dep),
            body=None,
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload = _validate_body(model, alias, target, body)
            if isinstance(h, Mapping):
                if isinstance(payload, Mapping):
                    payload = {**payload, **dict(h)}
                else:
                    payload = [{**dict(item), **dict(h)} for item in payload]
            is_seq = (
                target in {"create", "update", "replace", "merge"}
                and isinstance(payload, Sequence)
                and not isinstance(payload, Mapping)
            )
            exec_alias = f"bulk_{target}" if is_seq else alias
            exec_target = f"bulk_{target}" if is_seq else target
            if parent_kw:
                if isinstance(payload, Mapping):
                    payload = {**payload, **parent_kw}
                else:
                    payload = [{**dict(item), **parent_kw} for item in payload]
            ctx = _ctx(
                model, exec_alias, exec_target, request, db, payload, parent_kw, api
            )

            def _serializer(r, _ctx=ctx):
                out = _serialize_output(model, exec_alias, exec_target, sp, r)
                temp = getattr(_ctx, "temp", {}) if isinstance(_ctx, Mapping) else {}
                extras = (
                    temp.get("response_extras", {}) if isinstance(temp, Mapping) else {}
                )
                if isinstance(out, dict) and isinstance(extras, dict):
                    out.update(extras)
                return out

            ctx["response_serializer"] = _serializer
            phases = _get_phase_chains(model, exec_alias)
            result = await _executor._invoke(
                request=request, db=db, phases=phases, ctx=ctx
            )
            if isinstance(result, Response):
                if sp.status_code is not None or result.status_code == 200:
                    result.status_code = status_code
                return result
            return result

        body_default = ... if body_required else None
        _endpoint.__signature__ = _sig(
            nested_vars,
            [
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                ),
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(db_dep)],
                ),
                inspect.Parameter(
                    "h",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Mapping[str, Any], Depends(hdr_dep)],
                ),
                inspect.Parameter(
                    "body",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[body_annotation, Body()],
                    default=body_default,
                ),
            ],
        )
        _endpoint.__annotations__["body"] = body_annotation

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = (
        f"REST collection endpoint for {model.__name__}.{alias} ({target})"
    )
    return _endpoint
