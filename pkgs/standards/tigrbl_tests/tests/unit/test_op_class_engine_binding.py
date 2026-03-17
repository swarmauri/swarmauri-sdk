from tigrbl.engine.bind import install_from_objects
from tigrbl.engine import resolver
from tigrbl.shortcuts.engine import pga, pgs, sqlitef
from tigrbl.shortcuts.engine import mem
from tigrbl._concrete._op import Op


class Model:
    __tablename__ = "t"
    table_config = {"engine": mem(async_=False)}
    __tigrbl_ops__ = (
        Op(alias="create", target="create", engine=pga(host="db", name="op_db")),
    )


class App:
    def __init__(self, engine):
        self.engine = engine


class Router:
    def __init__(self, engine):
        self.engine = engine


def test_op_table_router_app_engines(tmp_path):
    app = App(sqlitef(str(tmp_path / "app.sqlite"), async_=False))
    router = Router(pgs(host="db", name="api_db"))

    install_from_objects(app=app, router=router, tables=[Model])

    p_app = resolver.resolve_provider()
    p_router = resolver.resolve_provider(router=router)
    p_table = resolver.resolve_provider(model=Model)
    p_op = resolver.resolve_provider(model=Model, op_alias="create")

    assert p_app is not None and p_app.kind == "sync"
    assert p_router is not None and p_router is not p_app and p_router.kind == "sync"
    assert p_table is not None and p_table is not p_router and p_table.kind == "sync"
    assert p_op is not None and p_op is not p_table and p_op.kind == "async"
