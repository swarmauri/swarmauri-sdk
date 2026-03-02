from tigrbl import TableBase
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import S, acol
from tigrbl.types import Column, String


def test_mapped_column_specs_still_materialize_columns():
    """Test mapped column specs still materialize columns."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "mapped_specs"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        tag = acol(storage=S(type_=String, nullable=False))

    assert "tag" in Widget.__table__.c
