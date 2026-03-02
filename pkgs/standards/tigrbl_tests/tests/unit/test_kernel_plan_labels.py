from tigrbl.runtime import events as _ev
from tigrbl.runtime.kernel import Kernel


def _mk_atom(module: str):
    def run(obj, ctx):
        return None

    run.__module__ = module
    return run


def test_plan_labels_reflect_kernel_injection():
    atoms = [
        (_ev.RESOLVE_VALUES, _mk_atom("tigrbl.runtime.atoms.resolve.values")),
        (_ev.PRE_FLUSH, _mk_atom("tigrbl.runtime.atoms.pre.flush")),
    ]
    k = Kernel(atoms=atoms)

    class Model:
        pass

    labels = k.plan_labels(Model, "create")
    assert labels == [
        "START_TX:hook:sys:txn:begin@START_TX",
        "PRE_HANDLER:atom:resolve:values@resolve:values",
        "PRE_HANDLER:atom:pre:flush@pre:flush",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]


def test_plan_labels_prune_non_persistent():
    atoms = [
        (_ev.RESOLVE_VALUES, _mk_atom("tigrbl.runtime.atoms.resolve.values")),
    ]
    k = Kernel(atoms=atoms)

    class Model:
        pass

    labels = k.plan_labels(Model, "read")
    assert labels == [
        "START_TX:hook:sys:txn:begin@START_TX",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]
