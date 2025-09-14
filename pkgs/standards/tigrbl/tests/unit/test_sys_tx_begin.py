from types import SimpleNamespace

import pytest

from tigrbl.runtime import system
from tigrbl.runtime.errors import SystemStepError


def test_registry_tx_begin_step() -> None:
    anchor, runner = system.get("txn", "begin")
    assert anchor == system.START_TX
    assert runner is system._sys_tx_begin


def test_tx_begin_calls_installed_runner_and_sets_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = {}

    def fake_begin(ctx: SimpleNamespace) -> None:
        called["ran"] = True

    monkeypatch.setattr(system.INSTALLED, "begin", fake_begin)
    ctx = SimpleNamespace(temp={})
    runner = system.get("txn", "begin")[1]
    runner(None, ctx)
    assert called.get("ran") is True
    assert ctx.temp["__sys_tx_open__"] is True


def test_tx_begin_noop_without_installed_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(system.INSTALLED, "begin", None)
    ctx = SimpleNamespace(temp={})
    runner = system.get("txn", "begin")[1]
    runner(None, ctx)
    assert ctx.temp["__sys_tx_open__"] is False


def test_tx_begin_wraps_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_begin(ctx: SimpleNamespace) -> None:
        raise ValueError("boom")

    monkeypatch.setattr(system.INSTALLED, "begin", bad_begin)
    ctx = SimpleNamespace(temp={})
    runner = system.get("txn", "begin")[1]
    with pytest.raises(SystemStepError):
        runner(None, ctx)
