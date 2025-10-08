import sys
import types
from types import SimpleNamespace


def _ensure_stub_modules() -> None:
    if "tigrbl" in sys.modules:
        return

    tigrbl = types.ModuleType("tigrbl")

    def engine_ctx(**_kwargs):
        def decorator(cls):
            handlers = SimpleNamespace()
            for name, attr in cls.__dict__.items():
                alias = getattr(attr, "__tigrbl_op_alias__", None)
                if not alias:
                    continue

                async def raw(ctx, _func=attr, _cls=cls):
                    return await _func(_cls, ctx)

                setattr(handlers, alias, SimpleNamespace(raw=raw))
            cls.handlers = handlers
            return cls

        return decorator

    def op_ctx(*, alias, **_meta):
        def decorator(func):
            func.__tigrbl_op_alias__ = alias
            return func

        return decorator

    def hook_ctx(*_args, **_kwargs):
        def decorator(func):
            return func

        return decorator

    def include_model(model):
        return model

    tigrbl.engine_ctx = engine_ctx
    tigrbl.op_ctx = op_ctx
    tigrbl.hook_ctx = hook_ctx
    tigrbl.include_model = include_model

    sys.modules["tigrbl"] = tigrbl

    orm = types.ModuleType("tigrbl.orm")
    tables = types.ModuleType("tigrbl.orm.tables")

    class Base:
        pass

    tables.Base = Base
    orm.tables = tables

    sys.modules["tigrbl.orm"] = orm
    sys.modules["tigrbl.orm.tables"] = tables

    specs = types.ModuleType("tigrbl.specs")

    class _Spec:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def _factory(*args, **kwargs):
        return _Spec(*args, **kwargs)

    specs.acol = _factory
    specs.vcol = _factory
    specs.S = _factory
    specs.F = _factory
    specs.IO = _factory

    sys.modules["tigrbl.specs"] = specs

    types_mod = types.ModuleType("tigrbl.types")

    class _Type:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    for name in [
        "String",
        "Integer",
        "LargeBinary",
        "JSON",
        "SAEnum",
        "Text",
    ]:
        setattr(types_mod, name, type(name, (_Type,), {}))

    types_mod.HTTPException = HTTPException

    sys.modules["tigrbl.types"] = types_mod

    core = types.ModuleType("tigrbl.core")

    async def read(cls, ident, db=None):
        return None

    async def list(cls, db=None, filters=None, sort=None):
        return []

    async def merge(cls, ident, data, db=None):
        result = {"id": ident}
        result.update(data or {})
        return result

    core.read = read
    core.list = list
    core.merge = merge

    sys.modules["tigrbl.core"] = core


_ensure_stub_modules()
