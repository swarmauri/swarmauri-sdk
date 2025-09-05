"""Utilities for removing fields from parent schemas."""

from __future__ import annotations

import inspect
from typing import (
    Any,
    Dict,
    List,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel, create_model

from .compat import PydanticUndefined


def _strip_parent_fields(base: Type[BaseModel], *, drop: Set[str]) -> Type[BaseModel]:
    """Return a shallow clone of *base* with selected fields removed."""
    assert issubclass(base, BaseModel), "base must be a Pydantic BaseModel subclass"

    # RootModel[Union[Model, List[Model]]] – unwrap inner model so we can strip
    # identifiers and return the cleaned schema directly.
    if len(getattr(base, "model_fields", {})) == 1 and "root" in base.model_fields:
        root_ann = base.model_fields["root"].annotation
        if get_origin(root_ann) is Union:
            item_type = None
            for arg in get_args(root_ann):
                origin = get_origin(arg)
                if inspect.isclass(arg) and issubclass(arg, BaseModel):
                    item_type = arg
                    break
                if origin in (list, List):
                    sub = get_args(arg)[0]
                    if inspect.isclass(sub) and issubclass(sub, BaseModel):
                        item_type = sub
                        break
            if item_type is not None:
                return _strip_parent_fields(item_type, drop=drop)

    hints = get_type_hints(base, include_extras=True)
    new_fields: Dict[str, Tuple[type, Any]] = {}

    for name, finfo in base.model_fields.items():  # type: ignore[attr-defined]
        if name in (drop or ()):  # pragma: no branch
            continue
        typ = hints.get(name, Any)
        default = (
            finfo.default
            if getattr(finfo, "default", PydanticUndefined) is not PydanticUndefined
            else ...
        )
        new_fields[name] = (typ, default)

    clone = create_model(
        f"{base.__name__}Pruned",
        __config__=getattr(base, "model_config", None),
        **new_fields,
    )  # type: ignore[arg-type]
    clone.model_rebuild(force=True)
    return clone


__all__ = ["_strip_parent_fields"]
