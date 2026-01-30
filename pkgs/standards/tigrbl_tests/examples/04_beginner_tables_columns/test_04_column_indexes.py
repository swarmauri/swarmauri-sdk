from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Index, String


def test_index_metadata_registered():
    """Confirm index metadata is captured on the table.

    Purpose: show that index definitions are part of table metadata and can be
    queried for documentation or optimization checks.

    Best practice: keep index names explicit and stable for migration tooling.
    """

    # Setup: add an index via ``__table_args__``.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonindexmeta"
        __allow_unmapped__ = True
        __table_args__ = (Index("ix_name", "name"),)
        name = Column(String, nullable=False)

    # Deployment: the table collects index metadata on class creation.
    assert {idx.name for idx in Widget.__table__.indexes} == {"ix_name"}


def test_index_columns_are_recorded():
    """Demonstrate that indexes remember which columns they cover.

    Purpose: provide an example of inspecting index definitions without hitting
    a database, useful for schema documentation and reviews.

    Best practice: only index columns with clear query patterns to balance
    performance with storage overhead.
    """

    # Setup: define another indexed model to inspect column bindings.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonindexmetacols"
        __allow_unmapped__ = True
        __table_args__ = (Index("ix_name", "name"),)
        name = Column(String, nullable=False)

    # Deployment: read the index definition from table metadata.
    index = next(iter(Widget.__table__.indexes))
    # Assertion: the index points at the expected column.
    assert set(index.columns.keys()) == {"name"}
