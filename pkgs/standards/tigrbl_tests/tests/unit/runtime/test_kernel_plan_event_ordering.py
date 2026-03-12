from tigrbl.runtime import events as _ev
from tigrbl_kernel import Kernel


def _mk_atom(module: str, label: str):
    def run(obj, ctx):
        return None

    run.__module__ = module
    run.__tigrbl_label = label
    return run


def test_kernel_plan_labels_follow_canonical_event_order() -> None:
    atoms = [
        (
            _ev.OUT_DUMP,
            _mk_atom(
                "tigrbl.runtime.atoms.out.dump",
                "atom:out:dump@out:dump",
            ),
        ),
        (
            _ev.SCHEMA_COLLECT_IN,
            _mk_atom(
                "tigrbl.runtime.atoms.schema.collect_in",
                "atom:schema:collect_in@schema:collect_in",
            ),
        ),
        (
            _ev.OUT_BUILD,
            _mk_atom(
                "tigrbl.runtime.atoms.wire.build_out",
                "atom:wire:build_out@out:build",
            ),
        ),
    ]
    kernel = Kernel(atoms=atoms)

    class Model:
        pass

    labels = kernel.plan_labels(Model, "create")

    assert labels == [
        "START_TX:hook:sys:txn:begin@START_TX",
        "PRE_HANDLER:atom:schema:collect_in@schema:collect_in",
        "POST_HANDLER:atom:wire:build_out@out:build",
        "POST_RESPONSE:atom:out:dump@out:dump",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]


def test_kernel_plan_labels_prune_persist_tied_events_for_read() -> None:
    atoms = [
        (
            _ev.RESOLVE_VALUES,
            _mk_atom(
                "tigrbl.runtime.atoms.resolve.values",
                "atom:resolve:values@resolve:values",
            ),
        ),
        (
            _ev.OUT_BUILD,
            _mk_atom(
                "tigrbl.runtime.atoms.wire.build_out",
                "atom:wire:build_out@out:build",
            ),
        ),
    ]
    kernel = Kernel(atoms=atoms)

    class Model:
        pass

    labels = kernel.plan_labels(Model, "read")

    assert labels == [
        "START_TX:hook:sys:txn:begin@START_TX",
        "POST_HANDLER:atom:wire:build_out@out:build",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]
