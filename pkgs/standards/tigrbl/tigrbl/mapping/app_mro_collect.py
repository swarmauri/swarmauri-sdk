from functools import lru_cache
from tigrbl_core._spec import AppSpec


@lru_cache(maxsize=None)
def mro_collect_app_spec(app: type):
    return AppSpec.collect(app)


__all__ = ["mro_collect_app_spec"]
