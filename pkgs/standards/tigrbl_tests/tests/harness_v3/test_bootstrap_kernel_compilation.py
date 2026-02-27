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

import pytest

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.kernel import _default_kernel
from tigrbl.runtime.kernel import opview_compiler
from tigrbl.types import Column, String


def _init_if_needed(app: TigrblApp) -> None:
    result = app.initialize()
    if inspect.isawaitable(result):
        # NOTE: callers in this file are sync tests.
        raise RuntimeError("Harness expects sync engine in these unit tests")


def test_kernel_ensure_primed_compiles_plan_once(monkeypatch: pytest.MonkeyPatch) -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_bootstrap_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    _init_if_needed(app)

    # Reset any prior cache state.
    _default_kernel.invalidate_kernelz_payload(app)

    calls = {"n": 0}
    original = _default_kernel.compile_plan

    def wrapped(app_obj):
        calls["n"] += 1
        return original(app_obj)

    monkeypatch.setattr(_default_kernel, "compile_plan", wrapped)

    _default_kernel.ensure_primed(app)
    _default_kernel.ensure_primed(app)

    assert calls["n"] == 1

    plan1 = _default_kernel.kernel_plan(app)
    plan2 = _default_kernel.kernel_plan(app)
    assert plan1 is plan2


def test_opview_is_compiled_once_per_model_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_opview_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    _init_if_needed(app)

    _default_kernel.invalidate_kernelz_payload(app)

    calls = {"n": 0}
    original = opview_compiler.compile_opview_from_specs

    def wrapped(*args, **kwargs):
        calls["n"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(opview_compiler, "compile_opview_from_specs", wrapped)

    view1 = _default_kernel.get_opview(app, Widget, "create")
    view2 = _default_kernel.get_opview(app, Widget, "create")

    assert view1 is view2
    assert calls["n"] == 1
