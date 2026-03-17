from functools import lru_cache


@lru_cache(maxsize=None)
def _mro_collect_decorated_hooks_cached(table: type, visible_aliases: frozenset[str]):
    del table, visible_aliases
    return {}


__all__ = ["_mro_collect_decorated_hooks_cached"]
