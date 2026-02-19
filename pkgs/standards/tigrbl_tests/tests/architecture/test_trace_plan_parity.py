from __future__ import annotations

from types import SimpleNamespace

import pytest


def _mk_labeled_step(label: str, *, result: object | None = None):
    async def _step(ctx):
        return result

    setattr(_step, "__tigrbl_label", label)
    return _step


def _build_model():
    from tigrbl.op.types import OpSpec

    class DemoModel:
        pass

    specs = (
        OpSpec(alias="create", target="create"),
        OpSpec(alias="read", target="read"),
        OpSpec(alias="bulk_create", target="bulk_create"),
        OpSpec(alias="sync_profile", target="custom"),
    )
    DemoModel.ops = SimpleNamespace(by_alias={sp.alias: (sp,) for sp in specs})
    DemoModel.opspecs = SimpleNamespace(all=specs)
    DemoModel.schemas = SimpleNamespace()

    def _hooks(alias: str):
        return SimpleNamespace(
            START_TX=[],
            PRE_TX_BEGIN=[],
            PRE_HANDLER=[],
            HANDLER=[
                _mk_labeled_step(
                    f"hook:handler:{alias}@HANDLER",
                    result={"alias": alias},
                )
            ],
            POST_HANDLER=[],
            PRE_COMMIT=[],
            END_TX=[],
            POST_RESPONSE=[],
            ON_ERROR=[],
            ON_SUCCESS=[],
        )

    DemoModel.hooks = SimpleNamespace(
        create=_hooks("create"),
        read=_hooks("read"),
        bulk_create=_hooks("bulk_create"),
        sync_profile=_hooks("sync_profile"),
    )
    return DemoModel


class _DummyDB:
    def commit(self):
        return None

    def flush(self):
        return None

    def rollback(self):
        return None


@pytest.mark.asyncio
@pytest.mark.parametrize("alias", ["create", "read", "bulk_create", "sync_profile"])
async def test_trace_labels_match_kernel_plan_for_rest_and_rpc(alias: str):
    from tigrbl.runtime.kernel import Kernel
    from tigrbl.transport.dispatcher import dispatch_operation

    model = _build_model()
    api = SimpleNamespace(models={"DemoModel": model})

    kernel = Kernel()
    kernel.ensure_primed(api)
    expected = [
        entry.split(":", 1)[1]
        for entry in kernel.kernelz_payload(api)["DemoModel"][alias]
    ]
    assert expected, "expected kernel plan labels to be non-empty"

    async def _invoke(rpc_mode: bool) -> list[str]:
        ctx_seed = {"temp": {}}
        result = await dispatch_operation(
            api=api,
            model_or_name="DemoModel",
            alias=alias,
            payload={"id": 1},
            db=_DummyDB(),
            request=None,
            ctx=ctx_seed,
            rpc_mode=rpc_mode,
        )
        assert result["alias"] == alias

        state = ctx_seed["temp"].get("__trace__")
        assert state is not None, "expected trace state to be present"
        observed = [step.get("label") for step in state.steps if step.get("label")]
        labels = [label for label in observed if isinstance(label, str)]
        return [
            label
            for label in labels
            if "@" in label or label.startswith(("secdep:", "dep:"))
        ]

    rest_labels = await _invoke(rpc_mode=False)
    rpc_labels = await _invoke(rpc_mode=True)

    expected_rest = [label for label in expected if label in rest_labels]
    expected_rpc = [label for label in expected if label in rpc_labels]

    assert rest_labels == expected_rest
    assert rpc_labels == expected_rpc
    assert rpc_labels == [label for label in rest_labels if label in rpc_labels]
