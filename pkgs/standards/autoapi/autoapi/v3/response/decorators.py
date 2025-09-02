from __future__ import annotations
from typing import Any, Callable, Optional, TypeVar, overload

from .types import ResponseSpec

T = TypeVar("T")
_ATTR = "__autoapi_response_spec__"


def _to_spec(spec: Optional[ResponseSpec] = None, **kwargs: Any) -> ResponseSpec:
    if spec is not None and kwargs:
        raise TypeError("response_ctx: provide either a ResponseSpec or keyword args")
    if spec is not None:
        return spec
    return ResponseSpec(**kwargs)


@overload
def response_ctx(spec: ResponseSpec) -> Callable[[T], T]: ...


@overload
def response_ctx(**kwargs: Any) -> Callable[[T], T]: ...


def response_ctx(*args: Any, **kwargs: Any) -> Callable[[T], T]:
    spec = _to_spec(*args, **kwargs)

    def decorator(target: T) -> T:
        setattr(target, _ATTR, spec)
        return target

    return decorator


def get_attached_response_spec(obj: Any) -> Optional[ResponseSpec]:
    return getattr(obj, _ATTR, None)
