import pytest

from autoapi.v3.runtime import atoms as runtime_atoms
from autoapi.v3.runtime import events as _ev
from autoapi.v3.runtime import labels as _lbl
from autoapi.v3.runtime import plan as runtime_plan
from autoapi.v3 import decorators as _deco


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
        secdeps=("a",),
        deps=("b",),
    )
    labels = runtime_plan.flattened_order(
        plan,
        persist=True,
        include_system_steps=True,
    )
    rendered = [lbl.render() for lbl in labels]
    assert rendered[:2] == ["secdep:a", "dep:b"]
    assert rendered[2] == node.label.render()
    assert rendered[3:] == [
        "sys:txn:begin@START_TX",
        "sys:handler:crud@HANDLER",
        "sys:txn:commit@END_TX",
    ]


def test_runtime_exposes_step_kinds_and_domains():
    from autoapi.v3 import runtime

    assert runtime.STEP_KINDS == ("secdep", "dep", "sys", "atom", "hook")
    assert runtime.DOMAINS == (
        "emit",
        "out",
        "refresh",
        "resolve",
        "schema",
        "storage",
        "wire",
    )


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


def test_flattened_order_skips_system_steps_when_disabled():
    """System step labels are omitted when include_system_steps=False."""
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
        include_system_steps=False,
    )
    assert all(lbl.kind != "sys" for lbl in labels)


def test_build_plan_respects_only_keys(monkeypatch):
    """build_plan filters per-field atoms using only_keys."""
    fake_registry = {("wire", "build_in"): (_ev.IN_VALIDATE, lambda *_: None)}
    monkeypatch.setattr(runtime_atoms, "REGISTRY", fake_registry, raising=False)
    monkeypatch.setattr(
        runtime_plan, "_should_instantiate", lambda *a, **k: True, raising=False
    )

    specs = {"f1": object(), "f2": object()}

    class Model:
        pass

    plan = runtime_plan.build_plan(Model, specs, only_keys=["f1"])
    fields = [n.field for n in plan.atoms_by_anchor[_ev.IN_VALIDATE]]
    assert fields == ["f1"]


@pytest.mark.parametrize(
    "domain,subject,anchor,field,col",
    [
        ("wire", "build_in", "anchor1", "f1", object()),
        ("out", "masking", "anchor2", "f2", object()),
    ],
)
def test_should_instantiate_always_true(domain, subject, anchor, field, col):
    """_should_instantiate returns True for any inputs."""
    assert runtime_plan._should_instantiate(domain, subject, anchor, field, col)


def test_ensure_known_anchor_accepts_valid_event():
    """_ensure_known_anchor passes for known event names."""
    runtime_plan._ensure_known_anchor(_ev.SCHEMA_COLLECT_IN, "schema", "collect_in")


def test_ensure_known_anchor_rejects_unknown_event():
    """_ensure_known_anchor raises for unknown event names."""
    with pytest.raises(ValueError):
        runtime_plan._ensure_known_anchor("bogus", "schema", "collect_in")


@pytest.mark.parametrize(
    "raw,kind,maker",
    [
        ("a", "secdep", _lbl.make_secdep),
        ("b", "dep", _lbl.make_dep),
    ],
)
def test_ensure_label_wraps_strings(raw, kind, maker):
    """_ensure_label wraps strings into the appropriate label types."""
    assert runtime_plan._ensure_label(raw, kind=kind) == maker(raw)


def test_ensure_label_returns_existing_label():
    """_ensure_label returns Label instances unchanged."""
    label = _lbl.make_atom("schema", "collect_in", _ev.SCHEMA_COLLECT_IN)
    assert runtime_plan._ensure_label(label, kind="dep") is label


def test_ensure_label_invalid_kind_raises():
    """_ensure_label errors on unsupported kinds."""
    with pytest.raises(ValueError):
        runtime_plan._ensure_label("x", kind="other")


def test_ensure_label_invalid_dep_name_rejected():
    """_ensure_label rejects dep names with invalid characters."""
    bad = "bad<dep>name"
    with pytest.raises(ValueError, match="Invalid dep name"):
        runtime_plan._ensure_label(bad, kind="dep")


def test_wrap_ctx_core_generates_valid_dep_name():
    """_wrap_ctx_core returns a function with a valid dep name."""

    class T:
        pass

    async def op(cls, ctx):
        return None

    op.__qualname__ = "T.op"

    wrapped = _deco._wrap_ctx_core(T, op)
    dep_name = f"{wrapped.__module__}.{wrapped.__qualname__}"
    assert runtime_plan._ensure_label(dep_name, kind="dep") == _lbl.make_dep(dep_name)
