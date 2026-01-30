from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, String


def test_nonmapped_columns_use_column_instances():
    class Widget(Base, GUIDPk):
        __tablename__ = "nonmapped_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        priority = Column(Integer, default=1)

    assert "priority" in Widget.__table__.c
