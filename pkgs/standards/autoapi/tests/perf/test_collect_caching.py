from autoapi.v3.column.collect import collect_columns
from autoapi.v3.column.column_spec import ColumnSpec
from autoapi.v3.engine.collect import collect_from_objects
from autoapi.v3.hook.collect import collect_decorated_hooks
from autoapi.v3.op.collect import collect_decorated_ops
from autoapi.v3.schema.collect import collect_decorated_schemas


class Model:
    __autoapi_cols__ = {"a": ColumnSpec(storage=None)}


def _run_collect(func, *args, **kwargs):
    func.cache_clear()
    for _ in range(5):
        func(*args, **kwargs)
    info = func.cache_info()
    return info.misses, info.hits


def test_collect_caching_performance():
    assert _run_collect(collect_columns, Model) == (1, 4)
    assert _run_collect(collect_decorated_ops, Model) == (1, 4)
    assert _run_collect(collect_decorated_hooks, Model, visible_aliases=set()) == (1, 4)
    assert _run_collect(collect_decorated_schemas, Model) == (1, 4)
    assert _run_collect(collect_from_objects, models=(Model,)) == (1, 4)
