from tigrbl import TigrblApi, engine_ctx
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_table_binding_reads_table_config():
    Widget = build_widget_model("LessonTableConfig")
    engine_ctx(kind="sqlite", mode="memory", async_=False)(Widget)

    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    config = api.table_config[Widget.__name__]
    assert config["engine"]["kind"] == "sqlite"
