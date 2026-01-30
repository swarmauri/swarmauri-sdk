from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, String


def test_column_defaults_apply_on_instantiation():
    class DefaultWidget(Base, GUIDPk):
        __tablename__ = "default_widgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)
        count = Column(Integer, default=7)

    column_default = DefaultWidget.__table__.c.count.default
    assert column_default is not None
    assert column_default.arg == 7
