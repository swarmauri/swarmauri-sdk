from pydantic import BaseModel

from tigrbl import TableBase, TigrblApp, bind, schema_ctx


def test_schema_ctx_attaches_schemas() -> None:
    class Widget(TableBase):
        __tablename__ = "schema_ctx_widgets"

        @schema_ctx(alias="Ping", kind="in")
        class PingIn(BaseModel):
            message: str

        @schema_ctx(alias="Ping", kind="out")
        class PingOut(BaseModel):
            message: str

    app = TigrblApp()
    app.include_table(Widget)
    app.initialize()
    bind(Widget)

    assert hasattr(Widget, "schemas")
    assert hasattr(Widget.schemas, "Ping")
    assert getattr(Widget.schemas.Ping, "in_", None) is Widget.PingIn
    assert getattr(Widget.schemas.Ping, "out", None) is Widget.PingOut
