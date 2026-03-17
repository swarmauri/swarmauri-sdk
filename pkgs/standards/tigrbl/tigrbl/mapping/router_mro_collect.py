from functools import lru_cache
from tigrbl_core._spec import RouterSpec


@lru_cache(maxsize=None)
def mro_collect_router_hooks(router: type):
    return tuple(RouterSpec.collect(router).hooks or ())


__all__ = ["mro_collect_router_hooks"]
