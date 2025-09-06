from autoapi.v3.column.collect import collect_columns
from autoapi.v3.column.column_spec import ColumnSpec
from autoapi.v3.engine.collect import collect_from_objects
from autoapi.v3.hook.collect import collect_decorated_hooks
from autoapi.v3.op.collect import collect_decorated_ops
from autoapi.v3.schema.collect import collect_decorated_schemas


class Model:
    __autoapi_cols__ = {"a": ColumnSpec(storage=None)}


def test_collect_caching_behaves_consistently():
    collect_columns.cache_clear()
    first = collect_columns(Model)
    second = collect_columns(Model)
    assert first is second
    assert collect_columns.cache_info().hits >= 1

    collect_decorated_ops.cache_clear()
    first_ops = collect_decorated_ops(Model)
    second_ops = collect_decorated_ops(Model)
    assert first_ops is second_ops
    assert collect_decorated_ops.cache_info().hits >= 1

    collect_decorated_hooks.cache_clear()
    first_hooks = collect_decorated_hooks(Model, visible_aliases=set())
    second_hooks = collect_decorated_hooks(Model, visible_aliases=set())
    assert first_hooks is second_hooks
    assert collect_decorated_hooks.cache_info().hits >= 1

    collect_decorated_schemas.cache_clear()
    first_schema = collect_decorated_schemas(Model)
    second_schema = collect_decorated_schemas(Model)
    assert first_schema is second_schema
    assert collect_decorated_schemas.cache_info().hits >= 1

    collect_from_objects.cache_clear()
    first_eng = collect_from_objects(models=(Model,))
    second_eng = collect_from_objects(models=(Model,))
    assert first_eng is second_eng
    assert collect_from_objects.cache_info().hits >= 1
