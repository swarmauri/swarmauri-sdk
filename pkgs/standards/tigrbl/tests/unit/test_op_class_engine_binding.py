from tigrbl.engine import install_from_objects, resolver
from tigrbl.engine.shortcuts import mem, pga, pgs, sqlitef
from tigrbl.op import Op


class Model:
    __tablename__ = "t"
    table_config = {"engine": mem(async_=False)}
    __tigrbl_ops__ = (
        Op(alias="create", target="create", engine=pga(host="db", name="op_db")),
    )


class App:
    def __init__(self, engine):
        self.engine = engine


class API:
    def __init__(self, engine):
        self.engine = engine


def test_op_table_api_app_engines(tmp_path):
    app = App(sqlitef(str(tmp_path / "app.sqlite"), async_=False))
    api = API(pgs(host="db", name="api_db"))

    install_from_objects(app=app, api=api, models=[Model])

    p_app = resolver.resolve_provider()
    p_api = resolver.resolve_provider(api=api)
    p_table = resolver.resolve_provider(model=Model)
    p_op = resolver.resolve_provider(model=Model, op_alias="create")

    assert p_app is not None and p_app.kind == "sync"
    assert p_api is not None and p_api is not p_app and p_api.kind == "sync"
    assert p_table is not None and p_table is not p_api and p_table.kind == "sync"
    assert p_op is not None and p_op is not p_table and p_op.kind == "async"
