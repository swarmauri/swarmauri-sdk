# tests/test_decorator_and_collect.py
from types import SimpleNamespace

from tigrbl.engine.decorators import (
    engine_ctx,
)  # :contentReference[oaicite:17]{index=17}
from tigrbl.engine import install_from_objects
from tigrbl.engine import (
    resolver,
)  # precedence registry  :contentReference[oaicite:18]{index=18}


# Minimal Table mixin expectation: the collector relies on presence of __tablename__
class TableMixin:
    __tablename__ = "t"


@engine_ctx(kind="sqlite", mode="memory", async_=False)  # table-level ctx
class Model(TableMixin):
    # shape expected by collector for op-level: handlers.<alias>.core is callable
    class handlers:
        pass


# Define an op-level function and decorate with engine_ctx
@engine_ctx(kind="postgres", async_=True, host="db", name="op_db")
async def core_create(payload, *, db=None, request=None, ctx=None):
    return {"ok": True}


# Attach into handlers namespace in the shape collector expects
setattr(Model.handlers, "create", SimpleNamespace(core=core_create))


def test_install_and_resolve_op_vs_table():
    # App/API omitted: we only test table + op registration
    install_from_objects(
        models=[Model]
    )  # registers table-level + op-level  :contentReference[oaicite:19]{index=19}

    # Table-level
    p_table = resolver.resolve_provider(model=Model)
    assert p_table is not None and p_table.kind == "sync"

    # Op-level (wins)
    p_op = resolver.resolve_provider(model=Model, op_alias="create")
    assert p_op is not None and p_op.kind == "async"
