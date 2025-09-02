from __future__ import annotations

from autoapi.v3.runtime import plan as runtime_plan


def test_response_atom_in_runtime_plan() -> None:
    class Model:  # pragma: no cover - simple model
        pass

    plan = runtime_plan.attach_atoms_for_model(Model, {})
    labels = [lbl.render() for lbl in plan.labels()]
    assert "atom:response:template@out:dump" in labels
    assert "atom:response:negotiate@out:dump" in labels
    assert "atom:response:render@out:dump" in labels
