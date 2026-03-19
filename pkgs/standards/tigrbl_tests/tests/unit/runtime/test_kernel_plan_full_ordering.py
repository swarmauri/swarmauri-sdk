from types import SimpleNamespace

import pytest

from tigrbl import TigrblApp
from tigrbl.runtime import events as _ev
from tigrbl_kernel import Kernel
from tigrbl_kernel.payload import build_kernelz_payload
from tigrbl.runtime.system import END_TX, START_TX


def _mk_step(label: str):
    async def _step(ctx):
        return None

    _step.__tigrbl_label = label
    return _step


def _dep(name: str):
    def dep_fn():
        return None

    dep_fn.__name__ = name
    return SimpleNamespace(dependency=dep_fn)


def test_kernel_plan_labels_cover_dep_hook_and_atom_ordering() -> None:
    router_hook = _mk_step("hook:router:pre@schema:collect_in")
    table_hook = _mk_step("hook:table:post@out:build")
    atoms = [
        (_ev.OUT_BUILD, _mk_step("atom:wire:build_out@out:build")),
        (
            _ev.SCHEMA_COLLECT_IN,
            _mk_step("atom:schema:collect_in@schema:collect_in"),
        ),
    ]

    kernel = Kernel(atoms=atoms)

    class Model:
        hooks = SimpleNamespace(
            create=SimpleNamespace(
                PRE_HANDLER=[router_hook],
                POST_HANDLER=[table_hook],
            )
        )
        ops = SimpleNamespace(
            by_alias={
                "create": [
                    SimpleNamespace(
                        alias="create",
                        target="create",
                        persist="default",
                        secdeps=[
                            _dep("app_sec"),
                            _dep("router_sec"),
                            _dep("table_sec"),
                        ],
                        deps=[_dep("router_dep"), _dep("table_dep")],
                    )
                ]
            }
        )

    labels = kernel.plan_labels(Model, "create")

    assert labels == [
        "START_TX:hook:sys:txn:begin@START_TX",
        "PRE_TX_BEGIN:hook:dep:security:0@dep:security",
        "PRE_TX_BEGIN:hook:dep:security:1@dep:security",
        "PRE_TX_BEGIN:hook:dep:security:2@dep:security",
        "PRE_TX_BEGIN:hook:dep:extra:0@dep:extra",
        "PRE_TX_BEGIN:hook:dep:extra:1@dep:extra",
        "PRE_HANDLER:hook:router:pre@schema:collect_in",
        "PRE_HANDLER:atom:schema:collect_in@schema:collect_in",
        "POST_HANDLER:hook:table:post@out:build",
        "POST_HANDLER:atom:wire:build_out@out:build",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]


def test_kernel_build_injects_sys_steps_only_for_persistent_ops() -> None:
    kernel = Kernel(atoms=[])

    class Model:
        ops = SimpleNamespace(
            by_alias={
                "create": [
                    SimpleNamespace(alias="create", target="create", persist="default")
                ],
                "read": [
                    SimpleNamespace(alias="read", target="read", persist="default")
                ],
            }
        )

    create_chains = kernel._build_op(Model, "create")
    read_chains = kernel._build_op(Model, "read")

    assert create_chains[START_TX] != []
    assert create_chains[END_TX] != []
    assert len(read_chains[START_TX]) == 1
    assert len(read_chains[END_TX]) == 1
    assert getattr(read_chains[START_TX][0], "__tigrbl_label", "").startswith(
        "atom:sys:phase_db"
    )
    assert getattr(read_chains[END_TX][0], "__tigrbl_label", "").startswith(
        "atom:sys:phase_db"
    )


@pytest.mark.asyncio
async def test_kernelz_payload_full_plan_ordering_for_app_router_and_table(monkeypatch):
    app = TigrblApp()

    class Widget:
        __name__ = "Widget"

    app.tables = {"Widget": Widget}

    create_spec = SimpleNamespace(
        alias="create",
        persist="default",
        secdeps=[_dep("app_sec"), _dep("router_sec"), _dep("table_sec")],
        deps=[_dep("router_dep"), _dep("table_dep")],
    )
    read_spec = SimpleNamespace(
        alias="read",
        persist="skip",
        secdeps=[_dep("app_sec")],
        deps=[_dep("router_dep")],
    )
    Widget.opspecs = SimpleNamespace(all=(create_spec, read_spec))

    def fake_build(model, alias):
        assert model is Widget
        if alias == "create":
            return {
                "PRE_HANDLER": [
                    _mk_step("hook:app:pre@schema:collect_in"),
                    _mk_step("hook:router:pre@schema:collect_in"),
                    _mk_step("atom:schema:collect_in@schema:collect_in"),
                ],
                "HANDLER": [
                    _mk_step("hook:app:handler@resolve:values"),
                    _mk_step("hook:router:handler@resolve:values"),
                    _mk_step("hook:table:handler@resolve:values"),
                ],
                "POST_HANDLER": [
                    _mk_step("hook:table:post@out:build"),
                    _mk_step("atom:wire:build_out@out:build"),
                ],
                "POST_RESPONSE": [_mk_step("atom:out:dump@out:dump")],
            }
        return {
            "PRE_HANDLER": [_mk_step("hook:router:pre@schema:collect_in")],
            "POST_HANDLER": [_mk_step("atom:wire:build_out@out:build")],
        }

    kernel = Kernel(atoms=[])
    monkeypatch.setattr(kernel, "_build_op", fake_build)
    monkeypatch.setattr(kernel, "get_specs", lambda model: {})

    payload = build_kernelz_payload(kernel, app)

    assert payload["Widget"]["create"] == [
        "PRE_TX_BEGIN:hook:dep:security:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "PRE_TX_BEGIN:hook:dep:security:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "PRE_TX_BEGIN:hook:dep:security:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "PRE_TX_BEGIN:hook:dep:extra:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "PRE_TX_BEGIN:hook:dep:extra:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "START_TX:hook:sys:txn:begin@START_TX",
        "PRE_HANDLER:hook:app:pre@schema:collect_in",
        "PRE_HANDLER:hook:router:pre@schema:collect_in",
        "PRE_HANDLER:atom:schema:collect_in@schema:collect_in",
        "HANDLER:hook:app:handler@resolve:values",
        "HANDLER:hook:router:handler@resolve:values",
        "HANDLER:hook:table:handler@resolve:values",
        "POST_HANDLER:hook:table:post@out:build",
        "POST_HANDLER:atom:wire:build_out@out:build",
        "END_TX:hook:sys:txn:commit@END_TX",
        "POST_RESPONSE:atom:out:dump@out:dump",
    ]
    assert payload["Widget"]["read"] == [
        "PRE_TX_BEGIN:hook:dep:security:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "PRE_TX_BEGIN:hook:dep:extra:test_kernel_plan_full_ordering._dep.<locals>.dep_fn",
        "PRE_HANDLER:hook:router:pre@schema:collect_in",
        "POST_HANDLER:atom:wire:build_out@out:build",
    ]
