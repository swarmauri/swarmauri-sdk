from types import SimpleNamespace

from tigrbl._spec import F, IO, S, acol
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.runtime.atoms.route import payload_select
from tigrbl.runtime.kernel.opview_compiler import compile_opview_from_specs
from tigrbl.types import Mapped, String


class Item(TableBase, GUIDPk):
    __tablename__ = "items_payload_select"
    __resource__ = "item"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read")),
    )
    worker_key: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create",),
            out_verbs=("create", "read"),
            header_in="X-Worker-Key",
            header_required_in=True,
        ),
    )


class _ColumnsBomb:
    @staticmethod
    def mro_collect_columns(_model):
        raise AssertionError("payload_select must not call mapping columns collectors")


def test_payload_select_merges_header_values_without_mapping_collectors(monkeypatch):
    monkeypatch.setattr(
        "tigrbl.mapping.column_mro_collect.mro_collect_columns",
        _ColumnsBomb.mro_collect_columns,
    )

    specs = dict(Item.__tigrbl_cols__)
    opview = compile_opview_from_specs(specs, SimpleNamespace(alias="create"))
    schema_in = {
        "fields": opview.schema_in.fields,
        "by_field": opview.schema_in.by_field,
        "required": tuple(
            name
            for name, meta in opview.schema_in.by_field.items()
            if meta.get("required")
        ),
    }

    ctx = SimpleNamespace(
        payload={"name": "foo", "worker_key": "body"},
        temp={
            "schema_in": schema_in,
            "ingress": {"headers": {"x-worker-key": "alpha"}},
            "route": {"params": {}},
        },
    )

    payload_select.run(None, ctx)

    assert ctx.payload["worker_key"] == "alpha"
