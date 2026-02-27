from tigrbl.mapping.context import MappingContext
from tigrbl.mapping.plan import Step, compile_plan
from tigrbl.mapping.precedence import merge_op_specs
from tigrbl._spec import OpSpec


def test_mapping_plan_step_order_is_deterministic():
    plan = compile_plan()
    assert [step for step, _ in plan.steps] == [
        Step.COLLECT,
        Step.MERGE,
        Step.BIND_MODELS,
        Step.BIND_OPS,
        Step.BIND_HOOKS,
        Step.BIND_DEPS,
        Step.SEAL,
    ]


def test_precedence_prefers_ctx_spec_values():
    base = OpSpec(
        alias="create", target="create", http_methods=("POST",), tags=("base",)
    )
    override = OpSpec(
        alias="create", target="create", http_methods=("PUT",), tags=("ctx",)
    )

    merged = merge_op_specs((base,), (override,))
    assert len(merged) == 1
    assert merged[0].http_methods == ("PUT",)
    assert merged[0].tags == ("ctx",)


def test_mapping_context_is_immutable_dataclass():
    class Demo:
        pass

    ctx = MappingContext(model=Demo, router=None, only_keys=None)
    try:
        ctx.model = str
    except Exception as exc:  # dataclasses.FrozenInstanceError
        assert exc.__class__.__name__ == "FrozenInstanceError"
    else:  # pragma: no cover
        raise AssertionError("MappingContext should be frozen")
