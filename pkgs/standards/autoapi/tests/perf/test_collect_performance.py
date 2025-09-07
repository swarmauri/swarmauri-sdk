from time import perf_counter, sleep



from autoapi.v3.column.mro_collect import mro_collect_columns
from autoapi.v3.column.column_spec import ColumnSpec
from autoapi.v3.column.io_spec import IOSpec as IO
from autoapi.v3.column.storage_spec import StorageSpec as S
from autoapi.v3.op.mro_collect import mro_collect_decorated_ops
from autoapi.v3.op import op_ctx
from autoapi.v3.hook.mro_collect import mro_collect_decorated_hooks
from autoapi.v3 import hook_ctx


class _SlowCols:
    def __init__(self, calls: dict):
        self.calls = calls

    def __get__(self, obj, cls):
        self.calls["cols"] += 1
        sleep(0.01)
        return {"id": ColumnSpec(storage=S(), io=IO())}


def test_mro_collect_columns_cached_call_faster():
    calls = {"cols": 0}

    class Model:
        __autoapi_cols__ = _SlowCols(calls)

    start = perf_counter()
    mro_collect_columns(Model)
    first = perf_counter() - start

    start = perf_counter()
    mro_collect_columns(Model)
    second = perf_counter() - start

    assert calls["cols"] == 1
    assert second < first * 0.1
    print(f"columns first={first:.6f}s second={second:.6f}s")


def test_mro_collect_ops_cached_call_faster(monkeypatch):
    calls = {"unwrap": 0}
    from autoapi.v3.op import mro_collect as _mro

    orig_unwrap = _mro._unwrap

    def slow_unwrap(attr):
        calls["unwrap"] += 1
        sleep(0.01)
        return orig_unwrap(attr)

    monkeypatch.setattr(_mro, "_unwrap", slow_unwrap)

    class Model:
        @op_ctx()
        def create(cls, ctx):
            return None

    start = perf_counter()
    mro_collect_decorated_ops(Model)
    first = perf_counter() - start
    first_calls = calls["unwrap"]

    start = perf_counter()
    mro_collect_decorated_ops(Model)
    second = perf_counter() - start

    assert calls["unwrap"] == first_calls
    assert second < first * 0.1
    print(f"ops first={first:.6f}s second={second:.6f}s")


def test_mro_collect_hooks_cached_call_faster(monkeypatch):
    calls = {"unwrap": 0}
    from autoapi.v3.hook import mro_collect as _mro

    orig_unwrap = _mro._unwrap

    def slow_unwrap(attr):
        calls["unwrap"] += 1
        sleep(0.01)
        return orig_unwrap(attr)

    monkeypatch.setattr(_mro, "_unwrap", slow_unwrap)

    class Model:
        @hook_ctx(ops="*", phase="POST_RESPONSE")
        def _hook(cls, ctx):
            return None

    visible = {"create"}

    start = perf_counter()
    mro_collect_decorated_hooks(Model, visible_aliases=visible)
    first = perf_counter() - start
    first_calls = calls["unwrap"]

    start = perf_counter()
    mro_collect_decorated_hooks(Model, visible_aliases=visible)
    second = perf_counter() - start

    assert calls["unwrap"] == first_calls
    assert second < first * 0.1
    print(f"hooks first={first:.6f}s second={second:.6f}s")
