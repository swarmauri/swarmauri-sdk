from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_class_creation_builds_table_and_columns():
    """Ensure model class creation wires table metadata and columns.

    Purpose: demonstrate that subclassing the Tigrbl Base automatically
    registers SQLAlchemy table metadata, even before any database connection.
    This helps new users verify that their models are discoverable and that
    columns are ready for migrations or schema inspection.

    Best practice: define an explicit ``__tablename__`` and declarative
    columns so table metadata is deterministic and readable in reviews.
    """

    # Setup: declare a minimal model with a required column.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonwidgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: class declaration triggers table metadata generation.
    assert Widget.__tablename__ == "lessonwidgets"
    # Exercise: inspect the column registry on the SQLAlchemy table.
    assert "name" in Widget.__table__.c


def test_class_creation_sets_column_nullability_and_type():
    """Teach how column configuration flows into table metadata.

    Purpose: highlight that class declarations yield concrete SQLAlchemy column
    objects, so you can introspect nullability and type choices without needing
    a live engine.

    Best practice: check nullability on required fields to ensure your model
    enforces data integrity at both the API and database layers.
    """

    # Setup: define a model with a required name field.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonwidgetrules"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: materialize the mapped table on class creation.
    name_column = Widget.__table__.c.name
    # Exercise: read the column metadata without touching a database.
    assert name_column.nullable is False
    # Assertion: confirm the storage type matches the declared String type.
    assert isinstance(name_column.type, String)
