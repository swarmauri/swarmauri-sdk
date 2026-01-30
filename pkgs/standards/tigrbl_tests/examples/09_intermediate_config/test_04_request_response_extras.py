from tigrbl.types import (
    RequestExtrasProvider,
    ResponseExtrasProvider,
    list_request_extras_providers,
    list_response_extras_providers,
)


def test_request_and_response_extras_providers_register():
    class LessonRequest(RequestExtrasProvider):
        pass

    class LessonResponse(ResponseExtrasProvider):
        pass

    assert any(p.__name__ == "LessonRequest" for p in list_request_extras_providers())
    assert any(p.__name__ == "LessonResponse" for p in list_response_extras_providers())
