from __future__ import annotations

from tigrbl import Base, schema_ctx
from tigrbl.types import BaseModel


def test_schema_ctx_attaches_schemas() -> None:
    class Widget(Base):
        __tablename__ = "schema_ctx_widgets"

        @schema_ctx(alias="Ping", kind="in")
        class PingIn(BaseModel):
            message: str

        @schema_ctx(alias="Ping", kind="out")
        class PingOut(BaseModel):
            message: str

    assert hasattr(Widget, "schemas")
