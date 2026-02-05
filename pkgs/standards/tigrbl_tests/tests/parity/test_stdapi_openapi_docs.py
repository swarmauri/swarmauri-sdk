from pydantic import BaseModel

from tigrbl.deps import stdapi


class CreateWidget(BaseModel):
    name: str


class WidgetOut(BaseModel):
    id: int
    name: str


def test_openapi_generation_and_docs_html():
    router = stdapi.APIRouter(title="Widgets", version="1.2.3", include_docs=True)

    @router.post(
        "/widgets/{widget_id}",
        tags=["widgets"],
        summary="Create widget",
        description="Create or update a widget",
        request_model=CreateWidget,
        response_model=WidgetOut,
        path_param_schemas={"widget_id": {"type": "string"}},
        query_param_schemas={"verbose": {"type": "boolean", "required": False}},
    )
    def create(widget_id: str):
        return {"id": 1, "name": widget_id}

    doc = router.openapi()
    assert doc["openapi"] == "3.1.0"
    assert doc["info"]["title"] == "Widgets"
    assert doc["info"]["version"] == "1.2.3"

    path_item = doc["paths"]["/widgets/{widget_id}"]
    op = path_item["post"]
    assert op["summary"] == "Create widget"
    assert op["description"] == "Create or update a widget"
    assert op["tags"] == ["widgets"]
    assert "parameters" in op
    assert any(p["name"] == "widget_id" for p in op["parameters"])
    assert "requestBody" in op
    assert "responses" in op

    html = router._swagger_ui_html(
        stdapi.Request(
            method="GET",
            path="/docs",
            headers={},
            query={},
            path_params={},
            body=b"",
        )
    )
    assert "swagger-ui" in html
    assert "/openapi.json" in html
