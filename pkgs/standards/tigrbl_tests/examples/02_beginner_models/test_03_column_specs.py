from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String


def test_column_specs_create_io_ready_columns():
    """Ensure column specs generate table-ready columns.

    Purpose: demonstrate how field, storage, and IO specs compose into a single
    declarative column, keeping model definitions concise.

    Best practice: centralize IO rules in specs so API-level permissions are
    declared alongside storage metadata.
    """

    # Setup: define a model using ColumnSpec helpers for storage + IO.
    class SpecWidget(Base, GUIDPk):
        __tablename__ = "spec_widgets"
        __allow_unmapped__ = True

        display = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    # Deployment: class creation materializes the SQLAlchemy table.
    # Assertion: the spec-backed column is available in metadata.
    assert "display" in SpecWidget.__table__.c


def test_column_specs_preserve_storage_metadata():
    """Teach how storage specs flow into column metadata.

    Purpose: confirm that nullability and type selections in the storage spec
    are visible on the resulting SQLAlchemy column.

    Best practice: keep storage rules explicit to prevent unexpected nulls and
    to make schema validation predictable.
    """

    # Setup: declare a second model to validate spec metadata.
    class SpecWidget(Base, GUIDPk):
        __tablename__ = "spec_widgets_rules"
        __allow_unmapped__ = True

        display = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    # Deployment: extract the generated column from table metadata.
    display_column = SpecWidget.__table__.c.display
    # Assertion: storage rules are respected in the column configuration.
    assert display_column.nullable is False
    assert isinstance(display_column.type, String)
