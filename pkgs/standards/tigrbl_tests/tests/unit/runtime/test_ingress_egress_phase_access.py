import pytest

from tigrbl.decorators.hook import hook_ctx
from tigrbl.hook.exceptions import InvalidHookPhaseError
from tigrbl_kernel.atoms import _inject_atoms


_PHASE_ONLY_ATOM_ANCHORS = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_DISPATCH",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
)


def _mk_atom(module: str, label: str):
    def run(obj, ctx):
        return None

    run.__module__ = module
    run.__tigrbl_label = label
    return run


@pytest.mark.parametrize("phase", _PHASE_ONLY_ATOM_ANCHORS)
def test_atom_injection_accepts_ingress_and_egress_phase_anchors(phase: str) -> None:
    chains = {}
    atoms = [
        (
            phase,
            _mk_atom(
                "tigrbl.runtime.atoms.response.custom",
                f"atom:response:custom@{phase}",
            ),
        )
    ]

    _inject_atoms(chains, atoms, persistent=True)

    assert phase in chains
    assert len(chains[phase]) == 1


@pytest.mark.parametrize("phase", _PHASE_ONLY_ATOM_ANCHORS)
def test_hook_ctx_rejects_ingress_and_egress_phase_hooks(phase: str) -> None:
    with pytest.raises(InvalidHookPhaseError):

        class Model:
            @hook_ctx(ops="create", phase=phase)
            def bad_phase_hook(cls, ctx):
                return None
