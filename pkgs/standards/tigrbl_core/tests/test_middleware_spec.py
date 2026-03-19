from __future__ import annotations

from tigrbl_core._spec.middleware_spec import ASGIApp, Message, Scope


async def _sample_app(scope: Scope, receive, send) -> None:
    _ = scope
    message: Message = await receive()
    await send(message)


def test_middleware_type_aliases_are_usable() -> None:
    app: ASGIApp = _sample_app

    assert callable(app)
