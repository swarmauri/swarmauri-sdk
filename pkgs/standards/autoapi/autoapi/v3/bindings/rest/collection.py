from __future__ import annotations

import inspect
import logging
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


logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/collection")


def _invoke(
    model: type,
    alias: str,
    target: str,
    sp: OpSpec,
    request: Request,
    db: Any,
    payload: Any,
    parent_kw: Dict[str, Any],
    serializer: Callable[[Any], Any] | None = None,
):
    ctx = {
        "request": request,
        "db": db,
        "payload": payload,
        "path_params": parent_kw,
        "env": SimpleNamespace(
            method=alias, params=payload, target=target, model=model
        ),
    }
    ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
    if ac:
        ctx["auth_context"] = ac
    if serializer:
        ctx["response_serializer"] = serializer
    phases = _get_phase_chains(model, alias)
    return _executor._invoke(request=request, db=db, phases=phases, ctx=ctx)


def _param(name: str, annotation: Any) -> inspect.Parameter:
    return inspect.Parameter(
        name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation
    )


def _make_collection_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    nested_vars: Sequence[str] | None = None,
) -> Callable[..., Awaitable[Any]]:
    alias, target = sp.alias, sp.target
    nested_vars = list(nested_vars or [])

    if target in {"list", "clear"}:
        list_dep = _make_list_query_dep(model, alias) if target == "list" else None

        async def _endpoint(
            request: Request,
            q: Mapping[str, Any] | None = Depends(list_dep) if list_dep else None,
            db: Any = Depends(db_dep),
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            if target == "list":
                query = dict(q or {})
                query.update(parent_kw)
                payload = _validate_query(model, alias, target, query)
            else:
                payload = dict(parent_kw)
            result = await _invoke(
                model, alias, target, sp, request, db, payload, parent_kw
            )
            return _serialize_output(model, alias, target, sp, result)

        params = [_param(nv, Annotated[str, Path(...)]) for nv in nested_vars]
        params.append(_param("request", Request))
        if target == "list":
            params.append(_param("q", Annotated[Mapping[str, Any], Depends(list_dep)]))
        params.append(_param("db", Annotated[Any, Depends(db_dep)]))
        _endpoint.__signature__ = inspect.Signature(params)
    else:
        body_model = _request_model_for(model, alias, resource, target)
        base_annotation = body_model or Mapping[str, Any]
        if target == "upsert":
            alias_ns = getattr(model, alias, None)
            item_model = getattr(alias_ns, "in_item", None) if alias_ns else None
            if (
                item_model
                and inspect.isclass(item_model)
                and issubclass(item_model, BaseModel)
            ):
                try:
                    body_annotation = list[item_model]  # type: ignore[valid-type]
                except Exception:  # pragma: no cover
                    body_annotation = List[item_model]  # type: ignore[name-defined]
            elif body_model is None:
                try:
                    body_annotation = list[Mapping[str, Any]]  # type: ignore[valid-type]
                except Exception:  # pragma: no cover
                    body_annotation = List[Mapping[str, Any]]  # type: ignore[name-defined]
            else:
                body_annotation = base_annotation
        else:
            if target in {"create", "update", "replace", "merge"}:
                try:
                    list_ann = list[Mapping[str, Any]]  # type: ignore[valid-type]
                except Exception:  # pragma: no cover
                    list_ann = List[Mapping[str, Any]]  # type: ignore[name-defined]
                if body_model is not None:
                    try:
                        body_annotation = body_model | list_ann  # type: ignore[operator]
                    except Exception:  # pragma: no cover
                        from typing import Union as _Union

                        body_annotation = _Union[body_model, list_ann]
                else:
                    try:
                        body_annotation = Mapping[str, Any] | list_ann  # type: ignore[operator]
                    except Exception:  # pragma: no cover
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
            exec_alias, exec_target = alias, target
            if (
                target in {"create", "update", "replace", "merge"}
                and isinstance(payload, Sequence)
                and not isinstance(payload, Mapping)
            ):
                exec_alias = exec_target = f"bulk_{target}"
            if parent_kw:
                if isinstance(payload, Mapping):
                    payload = {**payload, **parent_kw}
                else:
                    payload = parent_kw

            def serializer(r: Any) -> Any:
                return _serialize_output(model, exec_alias, exec_target, sp, r)

            return await _invoke(
                model,
                exec_alias,
                exec_target,
                sp,
                request,
                db,
                payload,
                parent_kw,
                serializer,
            )

        params = [_param(nv, Annotated[str, Path(...)]) for nv in nested_vars]
        params.extend(
            [
                _param("request", Request),
                _param("db", Annotated[Any, Depends(db_dep)]),
                _param("body", Annotated[body_annotation, Body(...)]),
            ]
        )
        _endpoint.__signature__ = inspect.Signature(params)
        _endpoint.__annotations__["body"] = body_annotation

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = (
        f"REST collection endpoint for {model.__name__}.{alias} ({target})"
    )
    return _endpoint
