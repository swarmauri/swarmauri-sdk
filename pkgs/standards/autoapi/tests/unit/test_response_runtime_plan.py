from __future__ import annotations

from autoapi.v3.runtime import plan as runtime_plan

from .response_utils import build_alias_model


def test_response_atoms_in_runtime_plan(tmp_path) -> None:
    Widget = build_alias_model(tmp_path)
    plan = runtime_plan.attach_atoms_for_model(Widget, {})
    labels = [lbl.render() for lbl in plan.labels()]
    assert "atom:response:template@out:dump" in labels
    assert "atom:response:negotiate@out:dump" in labels
    assert "atom:response:render@out:dump" in labels
