import pytest
from httpx import ASGITransport, AsyncClient

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.orm.tables import Base
from autoapi.v3.types import App, Column, String


@pytest.mark.asyncio()
async def test_openapi_clear_response_schema() -> None:
    Base.metadata.clear()

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_openapi_clear"
        name = Column(String, nullable=False)

    app = App()
    api = AutoAPI(app=app)
    api.include_model(Widget)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        spec = (await client.get("/openapi.json")).json()

    path = f"/{Widget.__name__.lower()}"
    schema_ref = spec["paths"][path]["delete"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert schema_ref.endswith("WidgetClearResponse")
    comp = spec["components"]["schemas"]["WidgetClearResponse"]
    assert "deleted" in comp.get("properties", {})
    assert comp.get("examples") == [{"deleted": 0}]
