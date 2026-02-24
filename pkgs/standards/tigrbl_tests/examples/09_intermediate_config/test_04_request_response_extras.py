"""Lesson 09.4: Registering request/response extras providers."""

from tigrbl.types import (
    RequestExtrasProvider,
    ResponseExtrasProvider,
    list_request_extras_providers,
    list_response_extras_providers,
)


def test_request_and_response_extras_providers_register():
    """Explain how extras providers register on subclassing.

    Purpose: ensure request/response extras can be discovered for pipeline
    augmentation (headers, metadata, etc.).
    Design practice: keep extras providers focused on one responsibility.
    """

    # Setup: create request/response extras providers.
    class LessonRequest(RequestExtrasProvider):
        pass

    class LessonResponse(ResponseExtrasProvider):
        pass

    # Test: read the provider registries.
    request_names = [p.__name__ for p in list_request_extras_providers()]
    response_names = [p.__name__ for p in list_response_extras_providers()]

    # Assertion: both providers are registered and discoverable.
    assert "LessonRequest" in request_names
    assert "LessonResponse" in response_names


def test_request_response_extras_lists_are_sorted():
    """Show that extras providers are listed deterministically.

    Purpose: verify the provider list order remains stable for debugging and
    documentation.
    Design practice: deterministic ordering makes tests and docs predictable.
    """

    # Setup: define providers with alphabetic names to test ordering.
    class AlphaRequest(RequestExtrasProvider):
        pass

    class ZetaResponse(ResponseExtrasProvider):
        pass

    # Test: list providers in their default registry order.
    request_names = [p.__name__ for p in list_request_extras_providers()]
    response_names = [p.__name__ for p in list_response_extras_providers()]

    # Assertion: names are sorted for deterministic output.
    assert request_names == sorted(request_names)
    assert response_names == sorted(response_names)
