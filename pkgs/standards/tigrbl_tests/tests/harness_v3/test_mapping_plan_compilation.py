"""Harness: MappingPlan compilation.

The mapping layer is the "bootstrap" pipeline that turns model declarations
into deterministic operation specs and binding specs.

Contract (TDD):
- mapping.plan.compile_plan() has a stable step order.
- Executing the plan produces visible operation specs for the model.

(Separate tests assert that those specs are ultimately attached to the model
and exposed via REST + JSON-RPC.)
"""

from __future__ import annotations

from tigrbl import Base
from tigrbl.mapping import collect as collect_ctx
from tigrbl.mapping import plan as mapping_plan
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_mapping_compile_plan_step_order_is_canonical() -> None:
    compiled = mapping_plan.compile_plan()
    steps = [step for step, _ in compiled.steps]

    assert steps == [
        mapping_plan.Step.COLLECT,
        mapping_plan.Step.MERGE,
        mapping_plan.Step.BIND_MODELS,
        mapping_plan.Step.BIND_OPS,
        mapping_plan.Step.BIND_HOOKS,
        mapping_plan.Step.BIND_DEPS,
        mapping_plan.Step.SEAL,
    ]


def test_mapping_plan_produces_visible_specs_for_default_ops() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_mapping_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    ctx = collect_ctx.collect(Widget)
    out = mapping_plan.plan(ctx)

    # Contract: default CRUD ops are visible after merge.
    aliases = {sp.alias for sp in out.visible_specs}

    assert "create" in aliases
    assert "read" in aliases
    assert "update" in aliases
    assert "delete" in aliases
    assert "list" in aliases
