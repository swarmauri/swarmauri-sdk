import pytest

from tigrbl_base._base._response_base import ResponseBase, TemplateBase
from tigrbl_core._spec.response_spec import ResponseSpec, TemplateSpec


def test_response_base_attributes_and_methods() -> None:
    response = ResponseBase(
        status_code=201,
        headers={"Content-Type": "application/json", "Set-Cookie": "sid=abc"},
        body=b'{"ok": true}',
    )

    assert isinstance(response, ResponseSpec)
    assert response.status_code == 201
    assert response.headers_map["content-type"] == "application/json"
    assert response.raw_headers
    assert response.body_text == '{"ok": true}'
    assert response.json_body() == {"ok": True}
    assert response.cookies == {"sid": "abc"}


def test_response_base_rejects_body_and_content() -> None:
    with pytest.raises(TypeError):
        ResponseBase(body=b"a", content=b"b")


def test_template_base_inheritance() -> None:
    template = TemplateBase()
    assert isinstance(template, TemplateSpec)
