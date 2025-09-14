import pytest
from tigrbl import TigrblApp, Base
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, S, acol
from tigrbl.types import App, Mapped, String
from httpx import ASGITransport, AsyncClient


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_example_presence"
    name: Mapped[str] = acol(
        storage=S(String, nullable=False), field=F(constraints={"examples": ["foo"]})
    )


def _resolve_schema(spec, schema):
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return spec["components"]["schemas"][ref]
    if "anyOf" in schema:
        return _resolve_schema(spec, schema["anyOf"][0])
    if "items" in schema:
        item = _resolve_schema(spec, schema["items"])
        schema["items"] = item
        if "examples" not in schema and "examples" in item:
            schema["examples"] = [item["examples"][0]]
    return schema


@pytest.mark.asyncio
@pytest.mark.i9n
async def test_openapi_examples_and_schemas_present(db_mode):
    fastapi_app = App()
    engine = mem() if db_mode == "async" else mem(async_=False)
    api = TigrblApp(engine=engine)
    api.include_model(Widget)
    if db_mode == "async":
        await api.initialize()
    else:
        api.initialize()
    api.mount_jsonrpc()
    fastapi_app.include_router(api.router)

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        spec = (await client.get("/openapi.json")).json()

    path = f"/{Widget.__name__.lower()}"
    create_req = spec["paths"][path]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    create_resp = spec["paths"][path]["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"]
    create_req = _resolve_schema(spec, create_req)
    create_resp = _resolve_schema(spec, create_resp)
    assert create_req["properties"]["name"]["examples"][0] == "foo"
    assert create_resp["properties"]["name"]["examples"][0] == "foo"

    expected = {
        "WidgetClearResponse",
        "WidgetCreateRequest",
        "WidgetCreateResponse",
        "WidgetDeleteResponse",
        "WidgetListResponse",
        "WidgetReadResponse",
        "WidgetReplaceRequest",
        "WidgetReplaceResponse",
        "WidgetUpdateRequest",
        "WidgetUpdateResponse",
    }
    assert expected <= set(spec["components"]["schemas"])

    assert hasattr(api.schemas, "Widget")
    widget_ns = getattr(api.schemas, "Widget")
    for alias in ["create", "read", "update", "replace", "delete", "list", "clear"]:
        assert hasattr(widget_ns, alias)
        op_ns = getattr(widget_ns, alias)
        assert hasattr(op_ns, "in_")
        assert hasattr(op_ns, "out")
