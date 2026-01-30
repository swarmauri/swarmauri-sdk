from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Index, String


def test_table_args_support_indexes():
    """Confirm indexes can be added via ``__table_args__``.

    Purpose: show that table-level indexes are registered alongside columns
    during model creation, enabling query tuning from day one.

    Best practice: name indexes explicitly so migration tools can track them
    and teammates can discuss query plans clearly.
    """

    # Setup: declare a model with an explicit index in ``__table_args__``.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonindex"
        __allow_unmapped__ = True
        __table_args__ = (Index("ix_widget_name", "name"),)
        name = Column(String, nullable=False)

    # Deployment: table metadata now includes the index.
    index_names = {index.name for index in Widget.__table__.indexes}
    # Assertion: the index name is discoverable in metadata.
    assert "ix_widget_name" in index_names


def test_indexes_capture_target_columns():
    """Demonstrate that index metadata records its target columns.

    Purpose: teach that you can introspect index definitions without a
    database, which helps in documentation and schema reviews.

    Best practice: keep indexes focused on the queryable columns to balance
    read performance with write overhead.
    """

    # Setup: define another indexed model to inspect index targets.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonindexcolumns"
        __allow_unmapped__ = True
        __table_args__ = (Index("ix_widget_name", "name"),)
        name = Column(String, nullable=False)

    # Deployment: pull the generated index object from metadata.
    index = next(iter(Widget.__table__.indexes))
    # Assertion: confirm the index is bound to the intended column.
    assert set(index.columns.keys()) == {"name"}
