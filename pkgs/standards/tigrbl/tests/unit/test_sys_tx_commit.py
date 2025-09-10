from types import SimpleNamespace

import pytest

from tigrbl.runtime import system
from tigrbl.runtime.errors import SystemStepError


def test_registry_tx_commit_step() -> None:
    anchor, runner = system.get("txn", "commit")
    assert anchor == system.END_TX
    assert runner is system._sys_tx_commit


@pytest.mark.asyncio
async def test_tx_commit_calls_installed_when_flag_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = {}

    def fake_commit(ctx: SimpleNamespace) -> None:
        called["ran"] = True

    monkeypatch.setattr(system.INSTALLED, "commit", fake_commit)
    ctx = SimpleNamespace(temp={"__sys_tx_open__": True})
    runner = system.get("txn", "commit")[1]
    await runner(None, ctx)
    assert called.get("ran") is True
    assert ctx.temp["__sys_tx_open__"] is False


@pytest.mark.asyncio
async def test_tx_commit_noop_when_flag_not_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = {}

    def fake_commit(ctx: SimpleNamespace) -> None:  # pragma: no cover - should not run
        called["ran"] = True

    monkeypatch.setattr(system.INSTALLED, "commit", fake_commit)
    ctx = SimpleNamespace(temp={"__sys_tx_open__": False})
    runner = system.get("txn", "commit")[1]
    await runner(None, ctx)
    assert called == {}
    assert ctx.temp["__sys_tx_open__"] is False


@pytest.mark.asyncio
async def test_tx_commit_wraps_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_commit(ctx: SimpleNamespace) -> None:
        raise ValueError("boom")

    monkeypatch.setattr(system.INSTALLED, "commit", bad_commit)
    ctx = SimpleNamespace(temp={"__sys_tx_open__": True})
    runner = system.get("txn", "commit")[1]
    with pytest.raises(SystemStepError):
        await runner(None, ctx)
    assert ctx.temp["__sys_tx_open__"] is False
