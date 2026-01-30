from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    JSONB,
    LargeBinary,
    Numeric,
    PgEnum,
    PgUUID,
    SAEnum,
    TSVECTOR,
    TZDateTime,
    Text,
)


def test_type_gallery_defines_all_supported_columns():
    """Validate the curated list of supported column types.

    Purpose: show learners the breadth of out-of-the-box column types that
    Tigrbl models can use without custom extensions.

    Best practice: keep a representative "gallery" model so upgrades can be
    validated quickly and documentation stays aligned with reality.
    """

    # Setup: build a gallery model that enumerates supported column types.
    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery"
        __allow_unmapped__ = True

        text = Column(Text)
        boolean = Column(Boolean)
        integer = Column(Integer)
        numeric = Column(Numeric(10, 2))
        json = Column(JSON)
        datetime = Column(DateTime)
        tzdatetime = Column(TZDateTime)
        binary = Column(LargeBinary)
        enum = Column(SAEnum("alpha", "beta", name="enum_kind"))
        array = Column(ARRAY(Integer))
        jsonb = Column(JSONB)
        pgenum = Column(PgEnum("red", "blue", name="pg_enum_kind"))
        pguuid = Column(PgUUID(as_uuid=True))
        tsvector = Column(TSVECTOR)

    # Deployment: class creation materializes the table metadata.
    column_names = set(Gallery.__table__.c.keys())
    expected = {
        "text",
        "boolean",
        "integer",
        "numeric",
        "json",
        "datetime",
        "tzdatetime",
        "binary",
        "enum",
        "array",
        "jsonb",
        "pgenum",
        "pguuid",
        "tsvector",
    }
    # Assertion: ensure all expected column names are present.
    assert expected.issubset(column_names)


def test_type_gallery_includes_array_and_jsonb_types():
    """Highlight common advanced storage types in table metadata.

    Purpose: demonstrate that array and JSONB columns are first-class citizens
    and expose their metadata for inspection.

    Best practice: choose rich types for structured data to keep schemas
    expressive and avoid manual serialization.
    """

    # Setup: reuse a compact gallery model for advanced type inspection.
    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery_advanced"
        __allow_unmapped__ = True

        array = Column(ARRAY(Integer))
        jsonb = Column(JSONB)

    # Deployment: pull columns from metadata to examine types.
    array_column = Gallery.__table__.c.array
    jsonb_column = Gallery.__table__.c.jsonb

    # Assertion: confirm array item types and JSONB usage.
    assert isinstance(array_column.type, ARRAY)
    assert isinstance(array_column.type.item_type, Integer)
    assert isinstance(jsonb_column.type, JSONB)
