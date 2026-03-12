from __future__ import annotations

import pytest

from tigrbl_kernel.models import PackedKernel
from tigrbl_runtime.executors.kernel_executor import _run_phase_chain
from tigrbl_runtime.executors.packed import PackedPlanExecutor
from tigrbl_runtime.executors.types import _Ctx
from tigrbl_runtime.runtime.gw.invoke import _run_phase_chain as _run_gw_phase_chain


class DummyKernel:
    pass


@pytest.mark.asyncio
async def test_run_phase_chain_sets_ctx_phase() -> None:
    seen = []

    async def step(ctx):
        seen.append(ctx.phase)

    ctx = _Ctx.ensure(request=None, db=None, seed={})
    await _run_phase_chain(
        DummyKernel(), ctx, {"PRE_HANDLER": [step], "END_TX": [step]}
    )

    assert seen == ["PRE_HANDLER", "END_TX"]


@pytest.mark.asyncio
async def test_run_segment_python_sets_ctx_phase_from_packed_segment() -> None:
    seen = []

    async def step(ctx):
        seen.append(ctx.phase)

    packed = PackedKernel(
        segment_offsets=(0,),
        segment_lengths=(1,),
        segment_step_ids=(0,),
        segment_phases=("POST_COMMIT",),
        step_table=(step,),
    )

    ctx = _Ctx.ensure(request=None, db=None, seed={})
    await PackedPlanExecutor()._run_segment_python(ctx, packed, 0)

    assert seen == ["POST_COMMIT"]


@pytest.mark.asyncio
async def test_gateway_run_phase_chain_sets_ctx_phase() -> None:
    seen = []

    async def step(ctx):
        seen.append(ctx.phase)

    ctx = _Ctx.ensure(request=None, db=None, seed={})
    await _run_gw_phase_chain(ctx, {"INGRESS_BEGIN": [step], "INGRESS_ROUTE": [step]})

    assert seen == ["INGRESS_BEGIN", "INGRESS_ROUTE"]
