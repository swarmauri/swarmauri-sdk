import pytest
from httpx import AsyncClient, ASGITransport

from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, BulkCapable
from autoapi.v3.types import App, Column, String


@pytest.mark.asyncio()
async def test_openapi_client_create_request_is_array() -> None:
    Base.metadata.clear()

    class Widget(Base, GUIDPk, BulkCapable):
        __tablename__ = "widgets_client_create"
        name = Column(String, nullable=False)

    router = _build_router(Widget, [OpSpec(alias="create", target="create")])
    app = App()
    app.include_router(router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        spec = (await client.get("/openapi.json")).json()

    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        schema = spec["components"]["schemas"][ref]

    options = schema.get("anyOf", [schema])
    assert any(opt.get("type") == "array" for opt in options)


@pytest.mark.asyncio()
async def test_openapi_client_bulk_create_response_schema() -> None:
    Base.metadata.clear()

    class Widget(Base, GUIDPk, BulkCapable):
        __tablename__ = "widgets_client_bulk_create"
        name = Column(String, nullable=False)

    router = _build_router(Widget, [OpSpec(alias="bulk_create", target="bulk_create")])
    app = App()
    app.include_router(router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        spec = (await client.get("/openapi.json")).json()

    path = f"/{Widget.__name__.lower()}"
    ref = spec["paths"][path]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert ref.endswith("WidgetBulkCreateResponse")
    comp = spec["components"]["schemas"]["WidgetBulkCreateResponse"]
    assert comp["type"] == "array"


@pytest.mark.asyncio()
async def test_openapi_client_bulk_delete_response_schema() -> None:
    Base.metadata.clear()

    class Widget(Base, GUIDPk, BulkCapable):
        __tablename__ = "widgets_client_bulk_delete"
        name = Column(String, nullable=False)

    router = _build_router(Widget, [OpSpec(alias="bulk_delete", target="bulk_delete")])
    app = App()
    app.include_router(router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        spec = (await client.get("/openapi.json")).json()

    path = f"/{Widget.__name__.lower()}"
    ref = spec["paths"][path]["delete"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert ref.endswith("WidgetBulkDeleteResponse")
    comp = spec["components"]["schemas"]["WidgetBulkDeleteResponse"]
    assert "deleted" in comp.get("properties", {})
