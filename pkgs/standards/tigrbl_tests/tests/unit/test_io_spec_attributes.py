from types import SimpleNamespace

from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.runtime.atoms.schema import collect_in, collect_out
from tigrbl.runtime.atoms.out import masking
from tigrbl.runtime.kernel import _default_kernel as K
from tigrbl.core.crud import helpers
from tigrbl.orm.tables import Base
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped


class DummyModel:
    pass


def test_in_verbs_filters_input():
    DummyModel.__tigrbl_colspecs__ = {
        "name": ColumnSpec(
            storage=S(type_=Integer),
            field=F(py_type=int),
            io=IO(in_verbs=("create",)),
        )
    }
    data = {"name": "one"}
    allowed = helpers._filter_in_values(DummyModel, data, "create")
    blocked = helpers._filter_in_values(DummyModel, data, "update")
    assert allowed == data
    assert blocked == {}


def test_out_verbs_filters_output():
    specs = {
        "visible": ColumnSpec(
            storage=S(type_=Integer),
            field=F(py_type=int),
            io=IO(out_verbs=("read",)),
        ),
        "hidden": ColumnSpec(
            storage=S(type_=Integer),
            field=F(py_type=int),
            io=IO(out_verbs=("list",)),
        ),
    }
    ov = K._compile_opview_from_specs(specs, SimpleNamespace(alias="read"))
    ctx = SimpleNamespace(opview=ov, temp={})
    collect_out.run(None, ctx)
    schema_out = ctx.temp["schema_out"]["by_field"]
    assert "visible" in schema_out
    assert "hidden" not in schema_out


def test_mutable_verbs_enforces_immutability():
    DummyModel.__tigrbl_colspecs__ = {
        "name": ColumnSpec(
            storage=S(type_=Integer),
            field=F(py_type=int),
            io=IO(in_verbs=("create",), mutable_verbs=("create",)),
        )
    }
    imm = helpers._immutable_columns(DummyModel, "update")
    assert "name" in imm


def test_alias_in_reflected_in_schema():
    spec = ColumnSpec(
        storage=S(type_=Integer),
        field=F(py_type=int),
        io=IO(alias_in="nickname", in_verbs=("create",)),
    )
    ov = K._compile_opview_from_specs({"name": spec}, SimpleNamespace(alias="create"))
    ctx = SimpleNamespace(opview=ov, temp={})
    collect_in.run(None, ctx)
    alias = ctx.temp["schema_in"]["by_field"]["name"]["alias_in"]
    assert alias == "nickname"


def test_alias_out_reflected_in_schema():
    spec = ColumnSpec(
        storage=S(type_=Integer),
        field=F(py_type=int),
        io=IO(alias_out="nickname", out_verbs=("read",)),
    )
    ov = K._compile_opview_from_specs({"name": spec}, SimpleNamespace(alias="read"))
    ctx = SimpleNamespace(opview=ov, temp={})
    collect_out.run(None, ctx)
    alias = ctx.temp["schema_out"]["by_field"]["name"]["alias_out"]
    assert alias == "nickname"


def test_sensitive_flag_has_no_masking_effect():
    spec = ColumnSpec(
        storage=S(type_=Integer),
        field=F(py_type=int),
        io=IO(sensitive=True, out_verbs=("read",)),
    )
    ov = K._compile_opview_from_specs({"secret": spec}, SimpleNamespace(alias="read"))
    ctx = SimpleNamespace(opview=ov, temp={"response_payload": {"secret": "topsecret"}})
    masking.run(None, ctx)
    assert ctx.temp["response_payload"]["secret"] == "topsecret"


def test_redact_last_flag_has_no_masking_effect():
    spec = ColumnSpec(
        storage=S(type_=Integer),
        field=F(py_type=int),
        io=IO(redact_last=2, out_verbs=("read",)),
    )
    ov = K._compile_opview_from_specs({"secret": spec}, SimpleNamespace(alias="read"))
    ctx = SimpleNamespace(opview=ov, temp={"response_payload": {"secret": "abcdef"}})
    masking.run(None, ctx)
    assert ctx.temp["response_payload"]["secret"] == "abcdef"


def test_filter_ops_restricts_filters():
    spec = ColumnSpec(
        storage=S(type_=Integer), field=F(py_type=int), io=IO(filter_ops=("eq", "gt"))
    )
    table = SimpleNamespace(columns=[SimpleNamespace(name="name")])
    Model = type(
        "Model", (), {"__tigrbl_colspecs__": {"name": spec}, "__table__": table}
    )
    filters = helpers._coerce_filters(Model, {"name": 1, "name__lt": 0, "name__gt": 2})
    assert filters == {"name": 1, "name__gt": 2}


def test_sortable_allows_sorting():
    sortable_spec = acol(
        storage=S(type_=Integer, primary_key=True), io=IO(sortable=True)
    )
    unsortable_spec = acol(storage=S(type_=Integer), io=IO(sortable=False))

    class SortModel(Base):
        __tablename__ = "sortables"
        __allow_unmapped__ = True

        sortable: Mapped[int] = sortable_spec
        unsortable: Mapped[int] = unsortable_spec
        __tigrbl_colspecs__ = {
            "sortable": sortable_spec,
            "unsortable": unsortable_spec,
        }

    from tigrbl.bindings.model import bind

    bind(SortModel)

    assert helpers._apply_sort(SortModel, "sortable")
    assert helpers._apply_sort(SortModel, "unsortable") is None


def test_allow_in_disables_field():
    spec = ColumnSpec(
        storage=S(type_=Integer), field=F(py_type=int), io=IO(allow_in=False)
    )
    specs = {"name": spec}
    ov = K._compile_opview_from_specs(specs, SimpleNamespace(alias="create"))
    ctx = SimpleNamespace(opview=ov, temp={})
    collect_in.run(None, ctx)
    assert "name" not in ctx.temp["schema_in"]["by_field"]


def test_allow_out_disables_field():
    spec = ColumnSpec(
        storage=S(type_=Integer), field=F(py_type=int), io=IO(allow_out=False)
    )
    specs = {"name": spec}
    ov = K._compile_opview_from_specs(specs, SimpleNamespace(alias="read"))
    ctx = SimpleNamespace(opview=ov, temp={})
    collect_out.run(None, ctx)
    assert "name" not in ctx.temp["schema_out"]["by_field"]
