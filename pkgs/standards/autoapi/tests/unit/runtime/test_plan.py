import pytest

from autoapi.v3.runtime import events as _ev
from autoapi.v3.runtime import labels as _lbl
from autoapi.v3.runtime import ordering as _ord
from autoapi.v3.runtime import plan as plan_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_node(
    domain: str, subject: str, anchor: str, field: str | None = None
) -> plan_mod.AtomNode:
    return plan_mod.AtomNode(
        label=_lbl.make_atom(domain, subject, anchor, field=field),
        run=lambda *a, **k: None,
        domain=domain,
        subject=subject,
        anchor=anchor,
        field=field,
    )


# ---------------------------------------------------------------------------
# Plan.labels
# ---------------------------------------------------------------------------


def test_plan_labels_returns_all_labels() -> None:
    nodes1 = (_make_node("schema", "collect_in", _ev.SCHEMA_COLLECT_IN),)
    nodes2 = (
        _make_node("wire", "build_in", _ev.IN_VALIDATE, field="a"),
        _make_node("wire", "build_in", _ev.IN_VALIDATE, field="b"),
    )
    plan = plan_mod.Plan(
        model_name="M",
        atoms_by_anchor={
            _ev.SCHEMA_COLLECT_IN: nodes1,
            _ev.IN_VALIDATE: nodes2,
        },
    )
    assert plan.labels() == [n.label for n in nodes1] + [n.label for n in nodes2]


# ---------------------------------------------------------------------------
# attach_atoms_for_model
# ---------------------------------------------------------------------------


class DummyModel:
    pass


def test_attach_atoms_for_model_attaches_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_plan = plan_mod.Plan(model_name="M", atoms_by_anchor={})

    def fake_build(*a, **k):
        return fake_plan

    monkeypatch.setattr(plan_mod, "build_plan", fake_build)
    model = DummyModel()
    result = plan_mod.attach_atoms_for_model(model, {})
    assert result is fake_plan
    assert getattr(model, "_autoapi_plan") is fake_plan
    assert model.runtime.plan is fake_plan


def test_attach_atoms_for_model_forwards_only_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    def fake_build(model, specs, *, only_keys=None):  # type: ignore[no-untyped-def]
        captured["only_keys"] = only_keys
        return plan_mod.Plan(model_name="M", atoms_by_anchor={})

    monkeypatch.setattr(plan_mod, "build_plan", fake_build)
    plan_mod.attach_atoms_for_model(DummyModel(), {}, only_keys=["a"])
    assert captured["only_keys"] == ["a"]


# ---------------------------------------------------------------------------
# build_plan
# ---------------------------------------------------------------------------


def test_build_plan_instantiates_model_and_field_atoms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def runner(*a, **k):
        return None

    registry = {
        ("schema", "collect_in"): (_ev.SCHEMA_COLLECT_IN, runner),
        ("wire", "build_in"): (_ev.IN_VALIDATE, runner),
    }
    import autoapi.v3.runtime.atoms as atoms_mod

    monkeypatch.setattr(atoms_mod, "REGISTRY", registry, raising=False)

    specs = {"a": object(), "b": object()}
    plan = plan_mod.build_plan(DummyModel, specs)

    assert plan.model_name == "DummyModel"
    per_model = plan.atoms_by_anchor[_ev.SCHEMA_COLLECT_IN]
    assert len(per_model) == 1 and per_model[0].field is None
    per_field = plan.atoms_by_anchor[_ev.IN_VALIDATE]
    assert {n.field for n in per_field} == {"a", "b"}


def test_build_plan_respects_only_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    def runner(*a, **k):
        return None

    registry = {("wire", "build_in"): (_ev.IN_VALIDATE, runner)}
    import autoapi.v3.runtime.atoms as atoms_mod

    monkeypatch.setattr(atoms_mod, "REGISTRY", registry, raising=False)
    specs = {"a": object(), "b": object()}
    plan = plan_mod.build_plan(DummyModel, specs, only_keys=["a"])
    per_field = plan.atoms_by_anchor[_ev.IN_VALIDATE]
    assert [n.field for n in per_field] == ["a"]


# ---------------------------------------------------------------------------
# flattened_order
# ---------------------------------------------------------------------------


def test_flattened_order_combines_labels_and_system_steps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    node = _make_node("schema", "collect_in", _ev.SCHEMA_COLLECT_IN)
    plan = plan_mod.Plan("M", {_ev.SCHEMA_COLLECT_IN: (node,)})
    captured: dict[str, list[_lbl.Label]] = {}

    def fake_flatten(labels, *, persist, anchor_policies=None):  # type: ignore[no-untyped-def]
        captured["labels"] = list(labels)
        captured["persist"] = persist
        captured["anchor_policies"] = anchor_policies
        return list(labels)

    monkeypatch.setattr(plan_mod._ord, "flatten", fake_flatten)
    result = plan_mod.flattened_order(
        plan,
        persist=True,
        include_system_steps=True,
        secdeps=["s"],
        deps=["d"],
        anchor_policies={"x": _ord.AnchorPolicy()},
    )
    assert result == captured["labels"]
    kinds = [lbl.kind for lbl in captured["labels"]]
    assert kinds[:2] == ["secdep", "dep"]
    assert any(lbl.kind == "sys" for lbl in captured["labels"])
    assert captured["persist"] is True
    assert "x" in captured["anchor_policies"]


@pytest.mark.parametrize(
    "persist,include_steps", [(False, True), (True, False), (False, False)]
)
def test_flattened_order_skips_system_steps(
    monkeypatch: pytest.MonkeyPatch, persist: bool, include_steps: bool
) -> None:
    node = _make_node("schema", "collect_in", _ev.SCHEMA_COLLECT_IN)
    plan = plan_mod.Plan("M", {_ev.SCHEMA_COLLECT_IN: (node,)})
    captured: dict[str, list[_lbl.Label]] = {}

    def fake_flatten(labels, *, persist, anchor_policies=None):  # type: ignore[no-untyped-def]
        captured["labels"] = list(labels)
        return list(labels)

    monkeypatch.setattr(plan_mod._ord, "flatten", fake_flatten)
    plan_mod.flattened_order(plan, persist=persist, include_system_steps=include_steps)
    assert not any(lbl.kind == "sys" for lbl in captured["labels"])


# ---------------------------------------------------------------------------
# _should_instantiate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "domain,subject,anchor,field,col",
    [
        ("wire", "build_in", _ev.IN_VALIDATE, "f", object()),
        ("out", "masking", _ev.OUT_DUMP, "g", object()),
    ],
)
def test_should_instantiate_always_true(
    domain: str, subject: str, anchor: str, field: str, col: object
) -> None:
    assert plan_mod._should_instantiate(domain, subject, anchor, field, col)


# ---------------------------------------------------------------------------
# _ensure_known_anchor
# ---------------------------------------------------------------------------


def test_ensure_known_anchor_accepts_valid() -> None:
    plan_mod._ensure_known_anchor(_ev.SCHEMA_COLLECT_IN, "schema", "collect_in")


def test_ensure_known_anchor_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        plan_mod._ensure_known_anchor("not_event", "schema", "collect_in")


# ---------------------------------------------------------------------------
# _ensure_label
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value,kind,expected",
    [
        ("s", "secdep", _lbl.make_secdep("s")),
        ("d", "dep", _lbl.make_dep("d")),
    ],
)
def test_ensure_label_wraps_string(value: str, kind: str, expected: _lbl.Label) -> None:
    assert plan_mod._ensure_label(value, kind=kind) == expected


def test_ensure_label_returns_label() -> None:
    lbl = _lbl.make_secdep("x")
    assert plan_mod._ensure_label(lbl, kind="secdep") is lbl


def test_ensure_label_raises_on_unknown_kind() -> None:
    with pytest.raises(ValueError):
        plan_mod._ensure_label("x", kind="unknown")


def test_ensure_label_raises_on_invalid_dep_name() -> None:
    bad = "bad<dep>name"
    with pytest.raises(ValueError, match="Invalid dep name"):
        plan_mod._ensure_label(bad, kind="dep")
