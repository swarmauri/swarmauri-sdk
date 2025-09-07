from __future__ import annotations
import logging

import inspect
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Sequence
from typing import get_origin as _get_origin, get_args as _get_args
import typing as _typing

from pydantic import BaseModel, Field, create_model

from .fastapi import HTTPException, Query, Request, _status
from .helpers import _ensure_jsonable
from ...op import OpSpec

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/io")


def _serialize_output(
    model: type, alias: str, target: str, sp: OpSpec, result: Any
) -> Any:
    """
    If a response schema exists (model.schemas.<alias>.out), serialize to it.
    Otherwise, attempt a best-effort conversion to primitive types so FastAPI
    can JSON-encode the response.
    """

    logger.debug(
        "_serialize_output model=%s alias=%s target=%s", model.__name__, alias, target
    )
    from ...types import Response as _Response  # local import to avoid cycles

    if isinstance(result, _Response):
        logger.debug("result is already a Response")
        return result

    def _final(val: Any) -> Any:
        if target == "list" and isinstance(val, (list, tuple)):
            return [_ensure_jsonable(v) for v in val]
        return _ensure_jsonable(val)

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        logger.debug("no schemas root for %s", model.__name__)
        return _final(result)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        logger.debug("no alias namespace %s", alias)
        return _final(result)
    out_model = getattr(alias_ns, "out", None)
    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        logger.debug("no valid out_model for %s.%s", model.__name__, alias)
        return _final(result)
    try:
        if target == "list" and isinstance(result, (list, tuple)):
            logger.debug("serializing list output of length %d", len(result))
            return [
                out_model.model_validate(x).model_dump(exclude_none=True, by_alias=True)
                for x in result
            ]
        logger.debug("serializing single output")
        return out_model.model_validate(result).model_dump(
            exclude_none=True, by_alias=True
        )
    except Exception:
        logger.debug(
            "rest output serialization failed for %s.%s",
            model.__name__,
            alias,
            exc_info=True,
        )
        return _final(result)


def _validate_body(
    model: type, alias: str, target: str, body: Any | None
) -> Mapping[str, Any] | Sequence[Mapping[str, Any]]:
    """Normalize and validate the incoming request body."""
    logger.debug(
        "_validate_body alias=%s target=%s body_type=%s",
        alias,
        target,
        type(body),
    )
    if isinstance(body, BaseModel):
        logger.debug("body is BaseModel")
        return body.model_dump(exclude_none=True)

    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        items: Sequence[Any] = body or []
        if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
            logger.debug("bulk body not sequence; defaulting to empty list")
            items = []

        schemas_root = getattr(model, "schemas", None)
        alias_ns = getattr(schemas_root, alias, None) if schemas_root else None
        in_item = getattr(alias_ns, "in_item", None) if alias_ns else None

        out: list[Mapping[str, Any]] = []
        for item in items:
            if isinstance(item, BaseModel):
                out.append(item.model_dump(exclude_none=True))
                logger.debug("validated bulk item via model")
                continue
            data: Mapping[str, Any] | None = None
            if in_item and inspect.isclass(in_item) and issubclass(in_item, BaseModel):
                try:
                    inst = in_item.model_validate(item)  # type: ignore[arg-type]
                    data = inst.model_dump(exclude_none=True)
                except Exception:
                    logger.debug(
                        "rest input body validation failed for %s.%s",
                        model.__name__,
                        alias,
                        exc_info=True,
                    )
            if data is None:
                data = dict(item) if isinstance(item, Mapping) else {}
                logger.debug("bulk item fell back to mapping: %s", data)
            out.append(data)
        return out

    if (
        target in {"create", "update", "replace", "merge"}
        and isinstance(body, Sequence)
        and not isinstance(body, (str, bytes, Mapping))
    ):
        logger.debug("treating sequence body as %s", f"bulk_{target}")
        bulk_target = f"bulk_{target}"
        items: Sequence[Any] = body
        schemas_root = getattr(model, "schemas", None)
        alias_ns = getattr(schemas_root, bulk_target, None) if schemas_root else None
        in_item = getattr(alias_ns, "in_item", None) if alias_ns else None

        out: list[Mapping[str, Any]] = []
        for item in items:
            if isinstance(item, BaseModel):
                out.append(item.model_dump(exclude_none=True))
                logger.debug("validated %s item via model", bulk_target)
                continue
            data: Mapping[str, Any] | None = None
            if in_item and inspect.isclass(in_item) and issubclass(in_item, BaseModel):
                try:
                    inst = in_item.model_validate(item)  # type: ignore[arg-type]
                    data = inst.model_dump(exclude_none=True)
                except Exception:
                    logger.debug(
                        "rest input body validation failed for %s.%s",
                        model.__name__,
                        bulk_target,
                        exc_info=True,
                    )
            if data is None:
                data = dict(item) if isinstance(item, Mapping) else {}
                logger.debug("%s item fell back to mapping", bulk_target)
            out.append(data)
        return out

    body = body or {}
    if not isinstance(body, Mapping):
        logger.debug("body not mapping; defaulting to empty dict")
        body = {}

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        logger.debug("no schemas root for %s", model.__name__)
        return dict(body)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        logger.debug("no alias namespace %s", alias)
        return dict(body)
    in_model = getattr(alias_ns, "in_", None)

    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            inst = in_model.model_validate(body)  # type: ignore[arg-type]
            logger.debug("validated body with in_model")
            return inst.model_dump(exclude_none=True)
        except Exception as e:
            logger.debug(
                "rest input body validation failed for %s.%s",
                model.__name__,
                alias,
                exc_info=True,
            )
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )
    return dict(body)


def _validate_query(
    model: type, alias: str, target: str, query: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Validate list/clear inputs coming from the query string."""
    logger.debug(
        "_validate_query alias=%s target=%s keys=%s", alias, target, list(query.keys())
    )
    if not query or (isinstance(query, Mapping) and len(query) == 0):
        logger.debug("empty query")
        return {}

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        logger.debug("no schemas root for %s", model.__name__)
        return dict(query)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        logger.debug("no alias namespace %s", alias)
        return dict(query)
    in_model = getattr(alias_ns, "in_", None)

    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            fields = getattr(in_model, "model_fields", {})
            data: Dict[str, Any] = {}
            for name, f in fields.items():
                alias_key = getattr(f, "alias", None) or name
                if alias_key in query:
                    val = query[alias_key]
                elif name in query:
                    val = query[name]
                else:
                    continue
                if val is None:
                    continue
                if isinstance(val, str) and not val.strip():
                    continue
                if isinstance(val, (list, tuple, set)) and len(val) == 0:
                    continue
                data[name] = val

            if not data:
                logger.debug("no matching query params")
                return {}

            inst = in_model.model_validate(data)  # type: ignore[arg-type]
            logger.debug("validated query via in_model")
            return inst.model_dump(exclude_none=True)
        except Exception as e:
            logger.debug("query validation failed", exc_info=True)
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    return dict(query)


def _strip_optional(t: Any) -> Any:
    """If annotation is Optional[T] return T; else return the input."""
    origin = _get_origin(t)
    if origin is _typing.Union:
        args = tuple(a for a in _get_args(t) if a is not type(None))
        logger.debug("_strip_optional %s -> %s", t, args)
        return args[0] if len(args) == 1 else Any
    return t


def _make_list_query_dep(model: type, alias: str):
    """Build a dependency exposing Query(...) params from schemas.<alias>.in_."""
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), alias, None
    )
    in_model = getattr(alias_ns, "in_", None)

    if not (in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel)):
        logger.debug("building simple list query dep for %s.%s", model.__name__, alias)

        def _dep(request: Request) -> Dict[str, Any]:
            return dict(request.query_params)

        _dep.__name__ = f"list_params_{model.__name__}_{alias}"
        return _dep

    fields = getattr(in_model, "model_fields", {})

    def _dep(**raw: Any) -> Dict[str, Any]:
        """Collect only user-supplied values; never apply schema defaults here."""
        logger.debug("list query dep raw keys=%s", list(raw.keys()))
        data: Dict[str, Any] = {}
        for name, f in fields.items():
            key = getattr(f, "alias", None) or name
            if key not in raw:
                continue
            val = raw[key]
            if val is None:
                continue
            if isinstance(val, str) and not val.strip():
                continue
            if isinstance(val, (list, tuple, set)) and len(val) == 0:
                continue
            data[key] = val
        logger.debug("list query dep result=%s", data)
        return data

    params: list[inspect.Parameter] = []
    for name, f in fields.items():
        key = getattr(f, "alias", None) or name
        ann = getattr(f, "annotation", Any)
        base = _strip_optional(ann)
        origin = _get_origin(base)
        if origin in (list, tuple, set):
            inner = (_get_args(base) or (str,))[0]
            annotation = list[inner] | None  # type: ignore[index]
        else:
            annotation = base | None
        default_q = Query(None, description=getattr(f, "description", None))
        params.append(
            inspect.Parameter(
                name=key,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default_q,
                annotation=annotation,
            )
        )

    _dep.__signature__ = inspect.Signature(
        parameters=params, return_annotation=Dict[str, Any]
    )
    _dep.__name__ = f"list_params_{model.__name__}_{alias}"
    return _dep


def _optionalize_list_in_model(in_model: type[BaseModel]) -> type[BaseModel]:
    """Make every field Optional[...] with default=None."""
    try:
        fields = getattr(in_model, "model_fields", {})
    except Exception:
        logger.debug(
            "_optionalize_list_in_model failed to inspect fields", exc_info=True
        )
        return in_model

    defs: Dict[str, tuple[Any, Any]] = {}
    for name, f in fields.items():
        ann = getattr(f, "annotation", Any)
        opt_ann = _typing.Union[ann, type(None)]
        defs[name] = (
            opt_ann,
            Field(
                default=None,
                alias=getattr(f, "alias", None),
                description=getattr(f, "description", None),
            ),
        )

    New = create_model(  # type: ignore[misc]
        f"{in_model.__name__}__Optionalized",
        **defs,
    )
    setattr(New, "__autoapi_optionalized__", True)
    logger.debug("_optionalize_list_in_model created %s", New)
    return New
