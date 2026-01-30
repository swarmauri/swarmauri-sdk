from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, Mapped, String, mapped_column


def test_mapped_and_nonmapped_columns_coexist():
    class MappedWidget(Base, GUIDPk):
        __tablename__ = "mapped_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity: Mapped[int] = mapped_column(Integer, default=0)

    class PlainWidget(Base, GUIDPk):
        __tablename__ = "plain_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity = Column(Integer, default=0)

    assert "quantity" in MappedWidget.__table__.c
    assert "quantity" in PlainWidget.__table__.c
