from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, Mapped, String, mapped_column


def test_mapped_mixins_extend_base_model():
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_mixins"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        rating: Mapped[int] = mapped_column(Integer, default=5)

    column_default = Widget.__table__.c.rating.default
    assert column_default is not None
    assert column_default.arg == 5
