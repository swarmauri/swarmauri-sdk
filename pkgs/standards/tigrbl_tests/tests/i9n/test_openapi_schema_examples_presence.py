import pytest
from httpx import ASGITransport, AsyncClient
from tigrbl import Base, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, S, acol
from tigrbl.types import Mapped, String


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
    app = TigrblApp()
    engine = mem() if db_mode == "async" else mem(async_=False)
    router = TigrblRouter(engine=engine)
    app.include_table(Widget)
    if db_mode == "async":
        await app.initialize()
    else:
        app.initialize()
    app.mount_jsonrpc()
    app.include_router(router)

    transport = ASGITransport(app=app)
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

    assert hasattr(app.schemas, "Widget")
    widget_ns = getattr(app.schemas, "Widget")
    for alias in ["create", "read", "update", "replace", "delete", "list", "clear"]:
        assert hasattr(widget_ns, alias)
        op_ns = getattr(widget_ns, alias)
        assert hasattr(op_ns, "in_")
        assert hasattr(op_ns, "out")
