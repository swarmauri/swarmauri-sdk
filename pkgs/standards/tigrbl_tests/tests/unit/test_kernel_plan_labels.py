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
        "atom:resolve:values@resolve:values",
        "atom:pre:flush@pre:flush",
    ]


def test_plan_labels_prune_non_persistent():
    atoms = [
        (_ev.RESOLVE_VALUES, _mk_atom("tigrbl.runtime.atoms.resolve.values")),
    ]
    k = Kernel(atoms=atoms)

    class Model:
        pass

    labels = k.plan_labels(Model, "read")
    assert labels == []
