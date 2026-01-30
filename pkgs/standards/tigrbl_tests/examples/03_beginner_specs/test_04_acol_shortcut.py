from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import S, acol
from tigrbl.types import String


def test_acol_creates_storage_and_field_specs():
    """Test acol creates storage and field specs."""

    class LessonWidget(Base, GUIDPk):
        __tablename__ = "acol_widgets"
        __allow_unmapped__ = True
        label = acol(storage=S(type_=String, nullable=False))

    assert "label" in LessonWidget.__table__.c
