from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Annotated, Any, Awaitable, Callable, Dict, List, Mapping, Sequence

from .common import (
    AUTOAPI_AUTH_CONTEXT_ATTR,
    Body,
    Depends,
    Path,
    Request,
    BaseModel,
    OpSpec,
    _coerce_parent_kw,
    _get_phase_chains,
    _make_list_query_dep,
    _request_model_for,
    _serialize_output,
    _validate_body,
    _validate_query,
    _executor,
)
from ...column.collect import collect_columns


def _make_collection_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    nested_vars: Sequence[str] | None = None,
) -> Callable[..., Awaitable[Any]]:
    alias = sp.alias
    target = sp.target
    nested_vars = list(nested_vars or [])

    # --- No body on GET list / DELETE clear ---
    if target in {"list", "clear"}:
        if target == "list":
            list_dep = _make_list_query_dep(model, alias)

            async def _endpoint(
                request: Request,
                q: Mapping[str, Any] = Depends(list_dep),
                db: Any = Depends(db_dep),
                **kw: Any,
            ):
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}
                _coerce_parent_kw(model, parent_kw)
                query = dict(q)
                query.update(parent_kw)
                payload = _validate_query(model, alias, target, query)
                ctx: Dict[str, Any] = {
                    "request": request,
                    "db": db,
                    "payload": payload,
                    "path_params": parent_kw,
                    "env": SimpleNamespace(
                        method=alias, params=payload, target=target, model=model
                    ),
                }
                ctx["specs"] = collect_columns(model)
                ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
                if ac is not None:
                    ctx["auth_context"] = ac
                phases = _get_phase_chains(model, alias)
                result = await _executor._invoke(
                    request=request,
                    db=db,
                    phases=phases,
                    ctx=ctx,
                )
                return _serialize_output(model, alias, target, sp, result)

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
                        "q",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Mapping[str, Any], Depends(list_dep)],
                    ),
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Any, Depends(db_dep)],
                    ),
                ]
            )
            _endpoint.__signature__ = inspect.Signature(params)
        else:

            async def _endpoint(
                request: Request,
                db: Any = Depends(db_dep),
                **kw: Any,
            ):
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}
                _coerce_parent_kw(model, parent_kw)
                payload: Mapping[str, Any] = dict(parent_kw)
                ctx: Dict[str, Any] = {
                    "request": request,
                    "db": db,
                    "payload": payload,
                    "path_params": parent_kw,
                    "env": SimpleNamespace(
                        method=alias, params=payload, target=target, model=model
                    ),
                }
                ctx["specs"] = collect_columns(model)
                ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
                if ac is not None:
                    ctx["auth_context"] = ac
                phases = _get_phase_chains(model, alias)
                result = await _executor._invoke(
                    request=request,
                    db=db,
                    phases=phases,
                    ctx=ctx,
                )
                return _serialize_output(model, alias, target, sp, result)

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
                ]
            )
            _endpoint.__signature__ = inspect.Signature(params)

        _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
        _endpoint.__qualname__ = _endpoint.__name__
        _endpoint.__doc__ = (
            f"REST collection endpoint for {model.__name__}.{alias} ({target})"
        )
        # NOTE: do NOT set body annotation for no-body endpoints
        return _endpoint

    # --- Body-based collection endpoints: create / bulk_* ---

    body_model = _request_model_for(sp, model)
    base_annotation = body_model if body_model is not None else Mapping[str, Any]

    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        alias_ns = getattr(
            getattr(model, "schemas", None) or SimpleNamespace(), alias, None
        )
        item_model = getattr(alias_ns, "in_item", None) if alias_ns else None
        if (
            item_model
            and inspect.isclass(item_model)
            and issubclass(item_model, BaseModel)
        ):
            try:
                body_annotation = list[item_model]  # type: ignore[valid-type]
            except Exception:  # pragma: no cover - best effort
                body_annotation = List[item_model]  # type: ignore[name-defined]
        elif body_model is None:
            try:
                body_annotation = list[Mapping[str, Any]]  # type: ignore[valid-type]
            except Exception:  # pragma: no cover - best effort
                body_annotation = List[Mapping[str, Any]]  # type: ignore[name-defined]
        else:
            body_annotation = base_annotation
    else:
        if target in {"create", "update", "replace", "merge"}:
            try:
                list_ann = list[Mapping[str, Any]]  # type: ignore[valid-type]
            except Exception:  # pragma: no cover - best effort
                list_ann = List[Mapping[str, Any]]  # type: ignore[name-defined]
            if body_model is not None:
                try:
                    body_annotation = body_model | list_ann  # type: ignore[operator]
                except Exception:  # pragma: no cover - best effort
                    from typing import Union as _Union

                    body_annotation = _Union[body_model, list_ann]
            else:
                try:
                    body_annotation = Mapping[str, Any] | list_ann  # type: ignore[operator]
                except Exception:  # pragma: no cover - best effort
                    from typing import Union as _Union

                    body_annotation = _Union[Mapping[str, Any], list_ann]
        else:
            body_annotation = base_annotation

    async def _endpoint(
        request: Request,
        db: Any = Depends(db_dep),
        body=Body(...),
        **kw: Any,
    ):
        parent_kw = {k: kw[k] for k in nested_vars if k in kw}
        _coerce_parent_kw(model, parent_kw)
        payload = _validate_body(model, alias, target, body)
        exec_alias = alias
        exec_target = target
        if (
            target in {"create", "update", "replace", "merge"}
            and isinstance(payload, Sequence)
            and not isinstance(payload, Mapping)
        ):
            exec_alias = f"bulk_{target}"
            exec_target = f"bulk_{target}"
        if parent_kw:
            if isinstance(payload, Mapping):
                payload = dict(payload)
                payload.update(parent_kw)
            else:
                payload = parent_kw
        ctx: Dict[str, Any] = {
            "request": request,
            "db": db,
            "payload": payload,
            "path_params": parent_kw,
            "env": SimpleNamespace(
                method=exec_alias, params=payload, target=exec_target, model=model
            ),
        }
        ctx["specs"] = collect_columns(model)
        temp_ctx = SimpleNamespace(temp={})
        specs = ctx["specs"]
        for field, spec in specs.items():
            paired = getattr(getattr(spec, "io", None), "_paired", None)
            if paired and field not in payload:
                raw = paired.gen(temp_ctx)
                payload[field] = paired.store(raw, temp_ctx)
                ctx.setdefault("response_extras", {})[paired.alias] = raw
        ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
        if ac is not None:
            ctx["auth_context"] = ac
        ctx["response_serializer"] = lambda r: _serialize_output(
            model, exec_alias, exec_target, sp, r
        )
        phases = _get_phase_chains(model, exec_alias)
        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=ctx,
        )
        extras = ctx.get("response_extras") or {}
        if isinstance(result, dict) and extras:
            result = {**result, **extras}
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
                "body",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[body_annotation, Body(...)],
            ),
        ]
    )
    _endpoint.__signature__ = inspect.Signature(params)

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = (
        f"REST collection endpoint for {model.__name__}.{alias} ({target})"
    )
    _endpoint.__annotations__["body"] = body_annotation
    return _endpoint
