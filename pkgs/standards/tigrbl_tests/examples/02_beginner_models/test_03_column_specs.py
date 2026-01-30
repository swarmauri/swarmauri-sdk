from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String


def test_column_specs_create_io_ready_columns():
    class SpecWidget(Base, GUIDPk):
        __tablename__ = "spec_widgets"
        __allow_unmapped__ = True

        display = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    assert "display" in SpecWidget.__table__.c
