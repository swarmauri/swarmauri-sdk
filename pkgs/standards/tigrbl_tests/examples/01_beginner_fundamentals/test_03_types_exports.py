from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, JSON, String, Text


def test_types_exports_cover_column_basics():
    """Verify that Tigrbl exports SQLAlchemy-compatible column types.

    Purpose: show that the ``tigrbl.types`` module re-exports familiar SQLAlchemy
    building blocks so learners can stay within the Tigrbl namespace.

    Best practice: import column types from a single module to keep model files
    tidy and avoid dependency sprawl.
    """

    # Setup: define a minimal gallery model using exported types.
    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery_basic"
        __allow_unmapped__ = True
        text = Column(Text)
        integer = Column(Integer)

    # Deployment: the class declaration registers a SQLAlchemy table.
    assert isinstance(Gallery.__table__.c.text, Column)
    # Exercise: check column type metadata.
    assert isinstance(Gallery.__table__.c.integer.type, Integer)
    assert isinstance(Gallery.__table__.c.text.type, String)


def test_types_exports_support_json_columns():
    """Show how JSON columns appear in the generated table metadata.

    Purpose: validate that richer types like JSON are still regular SQLAlchemy
    column objects, making them easy to inspect and migrate.

    Best practice: pick explicit JSON-capable types for structured data instead
    of overloading text columns, keeping schemas self-describing.
    """

    # Setup: declare a model that includes a JSON column.
    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery_json"
        __allow_unmapped__ = True
        json = Column(JSON)

    # Deployment: table metadata is available immediately.
    # Assertion: JSON columns are typed as JSON in metadata.
    assert isinstance(Gallery.__table__.c.json.type, JSON)
