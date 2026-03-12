"""Harness: bootstrap + compilation semantics.

Contract (TDD):
- The kernel can be *primed* once per app instance.
- Priming compiles and caches the KernelPlan.
- OpViews are compiled on-demand and cached.

These tests intentionally validate caching behavior (no redundant compilation),
which is critical for runtime-owned routing performance.
"""

from __future__ import annotations

import inspect

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl_kernel import _default_kernel
from tigrbl.types import Column, String


def _init_if_needed(app: TigrblApp) -> None:
    result = app.initialize()
    if inspect.isawaitable(result):
        # NOTE: callers in this file are sync tests.
        raise RuntimeError("Harness expects sync engine in these unit tests")


def test_kernel_ensure_primed_compiles_plan_once() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_bootstrap_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    _init_if_needed(app)

    # Reset any prior cache state.
    _default_kernel.invalidate_kernelz_payload(app)

    _default_kernel.ensure_primed(app)
    plan1 = _default_kernel.kernel_plan(app)

    _default_kernel.ensure_primed(app)
    plan2 = _default_kernel.kernel_plan(app)

    assert plan1 is plan2


def test_opview_is_compiled_once_per_model_alias() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_opview_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    _init_if_needed(app)

    _default_kernel.invalidate_kernelz_payload(app)

    view1 = _default_kernel.get_opview(app, Widget, "create")
    view2 = _default_kernel.get_opview(app, Widget, "create")

    assert view1 is view2
