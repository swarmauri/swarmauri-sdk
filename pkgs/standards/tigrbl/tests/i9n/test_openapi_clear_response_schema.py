import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl.types import App, Column, String


@pytest.mark.asyncio()
async def test_openapi_clear_response_schema() -> None:
    Base.metadata.clear()

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_openapi_clear"
        name = Column(String, nullable=False)

    app = App()
    api = TigrblApp()
    api.include_model(Widget)
    app.include_router(api.router)

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
