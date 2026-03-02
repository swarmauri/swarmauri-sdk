import logging
import time

from tigrbl.mapping.column_mro_collect import mro_collect_columns
from tigrbl.mapping.collect_decorated_schemas import collect_decorated_schemas


logging.getLogger("uvicorn").setLevel(logging.WARNING)


def _measure(func, obj, iterations=100):
    cold = 0.0
    for _ in range(iterations):
        func.cache_clear()
        start = time.perf_counter()
        func(obj)
        cold += time.perf_counter() - start
    func.cache_clear()
    start = time.perf_counter()
    for _ in range(iterations):
        func(obj)
    cached = time.perf_counter() - start
    return cold, cached


def test_mro_collect_columns_cached():
    class TableBase:
        pass

    class Model(TableBase):
        pass

    cold, cached = _measure(mro_collect_columns, Model, iterations=50)
    assert cached <= cold * 0.75


def test_collect_decorated_schemas_cached():
    class Model:
        pass

    cold, cached = _measure(collect_decorated_schemas, Model, iterations=50)
    assert cached <= cold * 0.75
