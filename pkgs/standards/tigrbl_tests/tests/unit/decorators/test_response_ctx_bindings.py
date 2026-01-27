from tigrbl import response_ctx
from tigrbl.response.types import ResponseSpec


def test_response_ctx_internal_binding_on_function():
    @response_ctx(media_type="application/json", status_code=201)
    def handler(ctx):
        return {"ok": True}

    spec = handler.__tigrbl_response_spec__
    assert spec.media_type == "application/json"
    assert spec.status_code == 201


def test_response_ctx_external_binding_on_class():
    class Wrapper:
        pass

    response_ctx(headers={"X-Test": "yes"})(Wrapper)

    spec = Wrapper.__tigrbl_response_spec__
    assert spec.headers == {"X-Test": "yes"}


def test_response_ctx_binding_with_spec_object():
    spec = ResponseSpec(media_type="text/plain", status_code=204)

    @response_ctx(spec)
    class PlainResponse:
        pass

    assert PlainResponse.__tigrbl_response_spec__ is spec
