import pytest
from httpx import AsyncClient, ASGITransport

from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, BulkCapable
from tigrbl.types import App, Column, String


@pytest.mark.asyncio()
async def test_openapi_client_create_request_schema_contains_object() -> None:
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

    if schema.get("type") == "object":
        return

    any_of = schema.get("anyOf") or []
    assert any(
        subschema.get("type") == "object"
        or (
            "$ref" in subschema
            and spec["components"]["schemas"][subschema["$ref"].split("/")[-1]].get(
                "type"
            )
            == "object"
        )
        for subschema in any_of
    )


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
