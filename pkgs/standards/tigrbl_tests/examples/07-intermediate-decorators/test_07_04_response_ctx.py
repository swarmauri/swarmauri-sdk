from __future__ import annotations

from tigrbl import Base, response_ctx
from tigrbl.types import BaseModel


def test_response_ctx_sets_response_spec() -> None:
    class Widget(Base):
        __tablename__ = "response_ctx_widgets"

        @response_ctx(alias="echo")
        class EchoResponse(BaseModel):
            message: str

    assert hasattr(Widget, "response") or hasattr(Widget, "responses")
