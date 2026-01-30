from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, Mapped, String


def test_mapped_columns_use_typed_annotations():
    """Explain how mapped columns use typed annotations for clarity and tooling.

    Purpose:
        Demonstrate that ``Mapped`` annotations can be paired with explicit
        ``Column(...)`` definitions to keep ORM intent clear without relying on
        ``mapped_column``.

    What this shows:
        - ``Column(...)`` participates in SQLAlchemy table construction.
        - The annotated field is still visible in ``__annotations__``.

    Best practice:
        Use ``Mapped[T]`` for ORM-managed attributes alongside ``Column(...)`` or
        ``ColumnSpec`` helpers like ``acol``/``vcol`` to keep models explicit.
    """

    # Setup: define a model that mixes typed annotations with explicit columns.
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_adv_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity: Mapped[int] = Column(Integer, default=3)

    # Deployment: not required; metadata is available on the mapped class.
    # Assertion: the mapped column is real SQLAlchemy metadata and typed.
    assert "quantity" in Widget.__table__.c
    assert "quantity" in Widget.__annotations__


def test_mapped_column_defaults_materialize_on_table():
    """Show mapped column defaults appear on the generated table.

    Purpose:
        Verify that defaults declared via ``Column(...)`` are preserved on the
        SQLAlchemy ``Column`` object even with typed annotations.

    What this shows:
        - ``Column`` defaults are stored on ``Column.default``.
        - Declarative mapping keeps model intent and database schema aligned.

    Best practice:
        Declare defaults at the column level so the schema and runtime behavior
        stay in sync across migrations and tests, avoiding ``mapped_column``.
    """

    # Setup: define a column default using explicit Column(...).
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_defaults"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity: Mapped[int] = Column(Integer, default=7)

    # Deployment: not required; we inspect table metadata directly.
    # Test: fetch the SQLAlchemy Column default recorded on the table.
    column_default = Widget.__table__.c.quantity.default
    # Assertion: the default is present and matches the configured value.
    assert column_default is not None
    assert column_default.arg == 7
