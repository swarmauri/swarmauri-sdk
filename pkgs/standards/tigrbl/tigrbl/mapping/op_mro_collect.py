from functools import lru_cache
from tigrbl_core._spec.op_spec import _mro_alias_map_for, _mro_collect_decorated_ops


@lru_cache(maxsize=None)
def mro_alias_map_for(table: type):
    return _mro_alias_map_for(table)


@lru_cache(maxsize=None)
def mro_collect_decorated_ops(table: type):
    return tuple(_mro_collect_decorated_ops(table))


__all__ = ["mro_alias_map_for", "mro_collect_decorated_ops"]
