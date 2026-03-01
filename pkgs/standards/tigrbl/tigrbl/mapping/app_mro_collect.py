from __future__ import annotations

from functools import lru_cache

from .._spec.app_spec import AppSpec


@lru_cache(maxsize=None)
def mro_collect_app_spec(app: type) -> AppSpec:
    """Collect AppSpec-like declarations across the app's MRO."""
    return AppSpec.collect(app)


__all__ = ["mro_collect_app_spec"]
