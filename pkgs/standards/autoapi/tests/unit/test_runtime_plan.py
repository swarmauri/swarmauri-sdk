from autoapi.v3.runtime import plan as runtime_plan
from autoapi.v3.runtime import labels as _lbl
from autoapi.v3.runtime import events as _ev
from autoapi.v3.runtime import atoms as runtime_atoms


def test_plan_labels_collects_all_atom_labels():
    """Plan.labels returns every atom label across all anchors."""
    node1 = runtime_plan.AtomNode(
        label=_lbl.make_atom("schema", "collect_in", _ev.SCHEMA_COLLECT_IN),
        run=lambda *_: None,
        domain="schema",
        subject="collect_in",
        anchor=_ev.SCHEMA_COLLECT_IN,
    )
    node2 = runtime_plan.AtomNode(
        label=_lbl.make_atom("out", "build", _ev.OUT_BUILD, field="field"),
        run=lambda *_: None,
        domain="out",
        subject="build",
        anchor=_ev.OUT_BUILD,
        field="field",
    )
    plan = runtime_plan.Plan(
        model_name="M",
        atoms_by_anchor={
            _ev.SCHEMA_COLLECT_IN: (node1,),
            _ev.OUT_BUILD: (node2,),
        },
    )
    assert set(plan.labels()) == {node1.label, node2.label}


def test_attach_atoms_for_model_sets_plan_and_runtime(monkeypatch):
    """attach_atoms_for_model sets the plan and runtime namespace on the model."""
    dummy_plan = runtime_plan.Plan(model_name="X", atoms_by_anchor={})

    class Model:
        pass

    monkeypatch.setattr(runtime_plan, "build_plan", lambda *a, **k: dummy_plan)
    runtime_plan.attach_atoms_for_model(Model, {})

    assert getattr(Model, "_autoapi_plan") is dummy_plan
    assert hasattr(Model, "runtime")
    assert Model.runtime.plan is dummy_plan


def test_build_plan_creates_per_model_and_per_field_atoms(monkeypatch):
    """build_plan instantiates per-model and per-field atoms based on registry."""
    fake_registry = {
        ("emit", "paired_pre"): (_ev.EMIT_ALIASES_PRE, lambda *_: None),
        ("wire", "build_in"): (_ev.IN_VALIDATE, lambda *_: None),
    }
    monkeypatch.setattr(runtime_atoms, "REGISTRY", fake_registry, raising=False)
    monkeypatch.setattr(
        runtime_plan, "_should_instantiate", lambda *a, **k: True, raising=False
    )

    specs = {"f1": object(), "f2": object()}

    class Model:
        pass

    plan = runtime_plan.build_plan(Model, specs)

    assert plan.model_name == "Model"
    assert set(plan.atoms_by_anchor) == {
        _ev.EMIT_ALIASES_PRE,
        _ev.IN_VALIDATE,
    }
    assert len(plan.atoms_by_anchor[_ev.EMIT_ALIASES_PRE]) == 1
    assert len(plan.atoms_by_anchor[_ev.IN_VALIDATE]) == 2
    assert {n.field for n in plan.atoms_by_anchor[_ev.IN_VALIDATE]} == {"f1", "f2"}


def test_flattened_order_includes_deps_and_system_steps():
    """flattened_order adds dep/secdep and system labels in order."""
    node = runtime_plan.AtomNode(
        label=_lbl.make_atom("schema", "collect_in", _ev.SCHEMA_COLLECT_IN),
        run=lambda *_: None,
        domain="schema",
        subject="collect_in",
        anchor=_ev.SCHEMA_COLLECT_IN,
    )
    plan = runtime_plan.Plan(
        model_name="M",
        atoms_by_anchor={_ev.SCHEMA_COLLECT_IN: (node,)},
    )
    labels = runtime_plan.flattened_order(
        plan,
        persist=True,
        include_system_steps=True,
        secdeps=("a",),
        deps=("b",),
    )
    rendered = [lbl.render() for lbl in labels]
    assert rendered[:2] == ["secdep:a", "dep:b"]
    assert rendered[2] == node.label.render()
    assert rendered[3:] == [
        "sys:txn:begin@START_TX",
        "sys:handler:crud@HANDLER",
        "sys:txn:commit@END_TX",
    ]


def test_flattened_order_omits_system_steps_when_not_persist():
    """System step labels are skipped when persist is False."""
    node = runtime_plan.AtomNode(
        label=_lbl.make_atom("schema", "collect_in", _ev.SCHEMA_COLLECT_IN),
        run=lambda *_: None,
        domain="schema",
        subject="collect_in",
        anchor=_ev.SCHEMA_COLLECT_IN,
    )
    plan = runtime_plan.Plan(
        model_name="M",
        atoms_by_anchor={_ev.SCHEMA_COLLECT_IN: (node,)},
    )
    labels = runtime_plan.flattened_order(
        plan,
        persist=False,
        include_system_steps=True,
    )
    assert all(lbl.kind != "sys" for lbl in labels)
