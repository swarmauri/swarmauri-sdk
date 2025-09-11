from types import SimpleNamespace

from tigrbl.runtime import system


def test_run_rollback_calls_installed(monkeypatch) -> None:
    called = {}

    def fake_rb(ctx: SimpleNamespace, err: BaseException | None) -> None:
        called["err"] = err

    monkeypatch.setattr(system.INSTALLED, "rollback", fake_rb)
    ctx = SimpleNamespace()
    err = RuntimeError("boom")
    system.run_rollback(ctx, err)
    assert called.get("err") is err


def test_run_rollback_falls_back_to_ctx_session(monkeypatch) -> None:
    monkeypatch.setattr(system.INSTALLED, "rollback", None)

    class Session:
        def __init__(self) -> None:
            self.rolled_back = False

        def rollback(
            self,
        ) -> None:  # pragma: no cover - executed via system.run_rollback
            self.rolled_back = True

    ctx = SimpleNamespace(session=Session())
    system.run_rollback(ctx, None)
    assert ctx.session.rolled_back is True


def test_run_rollback_swallows_exceptions(monkeypatch) -> None:
    def bad_rb(ctx: SimpleNamespace, err: BaseException | None) -> None:
        raise ValueError("fail")

    monkeypatch.setattr(system.INSTALLED, "rollback", bad_rb)
    ctx = SimpleNamespace()
    system.run_rollback(ctx, None)  # should not raise
