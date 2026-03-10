from __future__ import annotations

from tigrbl_core._spec.response_spec import ResponseSpec, TemplateSpec


def test_template_spec_defaults() -> None:
    template = TemplateSpec(name="index.html")

    assert template.name == "index.html"
    assert template.search_paths == []
    assert template.filters == {}


def test_response_spec_can_embed_template() -> None:
    template = TemplateSpec(name="ok.html", package="demo")
    response = ResponseSpec(kind="html", status_code=200, template=template)

    assert response.kind == "html"
    assert response.status_code == 200
    assert response.template is template
