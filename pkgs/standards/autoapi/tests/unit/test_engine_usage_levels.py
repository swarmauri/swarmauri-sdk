from autoapi.v3 import AutoApp, AutoAPI
from autoapi.v3.ops.types import OpSpec
from autoapi.v3.engine import resolver
from autoapi.v3.engine.engine_spec import EngineSpec
from autoapi.v3.engine.shortcuts import mem, sqlitef


def test_engine_usage_levels_and_precedence(tmp_path):
    app_engine = sqlitef(str(tmp_path / "app.db"))
    api_engine = mem(async_=False)
    table_engine = mem(async_=False)
    op_engine = mem(async_=True)

    app = AutoApp(engine=app_engine)
    api = AutoAPI(engine=api_engine)

    class Model:
        table_config = {"engine": table_engine}
        __name__ = "Model"

    op_spec = OpSpec(alias="do", target="custom", table=Model, engine=op_engine)
    Model.__autoapi_ops__ = [op_spec]

    app.install_engines(api=api, models=(Model,))

    assert resolver.resolve_provider().spec == EngineSpec.from_any(app_engine)
    assert resolver.resolve_provider(api=api).spec == EngineSpec.from_any(api_engine)
    assert resolver.resolve_provider(model=Model).spec == EngineSpec.from_any(
        table_engine
    )
    assert resolver.resolve_provider(
        model=Model, op_alias="do"
    ).spec == EngineSpec.from_any(op_engine)
