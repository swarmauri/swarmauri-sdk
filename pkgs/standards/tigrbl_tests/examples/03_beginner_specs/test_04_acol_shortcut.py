from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import S, acol
from tigrbl.types import String


def test_acol_creates_storage_and_field_specs():
    """Show that ``acol`` builds a full column from specs.

    Purpose: teach that the shortcut combines field and storage specs into a
    declarative column, keeping model definitions succinct.

    Best practice: use ``acol`` for consistency so column rules are always
    expressed through the same spec vocabulary.
    """

    # Setup: use ``acol`` to define a column with storage specs.
    class LessonWidget(Base, GUIDPk):
        __tablename__ = "acol_widgets"
        __allow_unmapped__ = True
        label = acol(storage=S(type_=String, nullable=False))

    # Deployment: class creation yields table metadata.
    # Assertion: the column exists on the generated table.
    assert "label" in LessonWidget.__table__.c


def test_acol_respects_storage_configuration():
    """Verify that ``acol`` respects storage arguments like nullability.

    Purpose: demonstrate that storage specs remain the single source of truth
    for column constraints, even when using shortcuts.

    Best practice: keep storage rules explicit to avoid accidental schema
    drift between model definitions and database migrations.
    """

    # Setup: define another ``acol``-based column for nullability checks.
    class LessonWidget(Base, GUIDPk):
        __tablename__ = "acol_widgets_nullable"
        __allow_unmapped__ = True
        label = acol(storage=S(type_=String, nullable=False))

    # Deployment: inspect the generated column metadata.
    column = LessonWidget.__table__.c.label
    # Assertion: storage settings are honored.
    assert column.nullable is False
    assert isinstance(column.type, String)
