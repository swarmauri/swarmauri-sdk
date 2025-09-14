from types import SimpleNamespace

import pytest

from tigrbl.runtime import system
from tigrbl.runtime.errors import SystemStepError


def test_registry_handler_crud_step() -> None:
    anchor, runner = system.get("handler", "crud")
    assert anchor == system.HANDLER
    assert runner is system._sys_handler_crud


def test_handler_calls_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def installed(obj: object | None, ctx: SimpleNamespace) -> None:
        called["obj"] = obj

    monkeypatch.setattr(system.INSTALLED, "handler", installed)
    ctx = SimpleNamespace(temp={})
    runner = system.get("handler", "crud")[1]
    runner("payload", ctx)
    assert called["obj"] == "payload"


def test_handler_uses_temp_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(system.INSTALLED, "handler", None)

    def temp_handler(obj: object | None, ctx: SimpleNamespace) -> None:
        ctx.temp["hit"] = True

    ctx = SimpleNamespace(temp={"handler": temp_handler})
    runner = system.get("handler", "crud")[1]
    runner(None, ctx)
    assert ctx.temp["hit"] is True


def test_handler_uses_ctx_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(system.INSTALLED, "handler", None)

    def ctx_handler(obj: object | None, ctx: SimpleNamespace) -> None:
        ctx.called = True

    ctx = SimpleNamespace(temp={}, handler=ctx_handler)
    runner = system.get("handler", "crud")[1]
    runner(None, ctx)
    assert ctx.called is True


def test_handler_uses_model_runtime_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(system.INSTALLED, "handler", None)

    class ModelRuntime:
        def handler(self, obj: object | None, ctx: SimpleNamespace) -> None:
            ctx.called = "runtime"

    class Model:
        runtime = ModelRuntime()

    ctx = SimpleNamespace(temp={}, model=Model())
    runner = system.get("handler", "crud")[1]
    runner(None, ctx)
    assert ctx.called == "runtime"


def test_handler_uses_model_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(system.INSTALLED, "handler", None)

    class Model:
        def handler(self, obj: object | None, ctx: SimpleNamespace) -> None:
            ctx.called = "model"

    ctx = SimpleNamespace(temp={}, model=Model())
    runner = system.get("handler", "crud")[1]
    runner(None, ctx)
    assert ctx.called == "model"


def test_handler_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(system.INSTALLED, "handler", None)
    ctx = SimpleNamespace(temp={})
    runner = system.get("handler", "crud")[1]
    with pytest.raises(SystemStepError):
        runner(None, ctx)
