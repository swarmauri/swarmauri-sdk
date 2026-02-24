from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, Mapped, String, mapped_column


def test_mapped_columns_use_typed_annotations():
    """Test mapped columns use typed annotations."""

    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_adv_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity: Mapped[int] = mapped_column(Integer, default=3)

    assert "quantity" in Widget.__table__.c
