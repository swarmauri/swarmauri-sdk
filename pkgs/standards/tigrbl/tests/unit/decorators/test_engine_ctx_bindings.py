from tigrbl import Api, App, engine_ctx


def test_engine_ctx_binding_on_function_sets_attributes():
    @engine_ctx("sqlite:///file.db")
    def op(ctx):
        return None

    assert op.__tigrbl_engine_ctx__ == "sqlite:///file.db"
    assert op.__tigrbl_db__ == "sqlite:///file.db"


def test_engine_ctx_internal_binding_on_table_class():
    @engine_ctx("sqlite:///mem.db")
    class Widget:
        __tablename__ = "widgets"

    cfg = Widget.table_config
    assert cfg["engine"] == "sqlite:///mem.db"
    assert cfg["db"] == "sqlite:///mem.db"


def test_engine_ctx_external_binding_on_api_class():
    class ExampleApi(Api):
        PREFIX = ""
        NAME = "example"

    engine_ctx("postgresql+asyncpg://db")(ExampleApi)

    assert ExampleApi.engine == "postgresql+asyncpg://db"
    assert ExampleApi.db == "postgresql+asyncpg://db"


def test_engine_ctx_binding_on_app_instance():
    class ExampleApp(App):
        TITLE = "Example"
        VERSION = "0.1.0"
        LIFESPAN = None

    app = ExampleApp()

    engine_ctx(kind="sqlite", memory=True)(app)

    expected = {"kind": "sqlite", "async": True, "mode": "memory"}
    assert app.engine == expected
    assert app.db == expected


def test_engine_ctx_binding_on_plain_object():
    class Plain:
        pass

    target = Plain()
    engine_ctx("sqlite:///plain.db")(target)

    assert target.engine == "sqlite:///plain.db"
    assert target.db == "sqlite:///plain.db"
