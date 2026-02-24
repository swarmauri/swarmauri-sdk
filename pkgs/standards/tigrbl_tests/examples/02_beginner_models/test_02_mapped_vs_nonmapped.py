from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, Mapped, String


def test_mapped_and_nonmapped_columns_coexist():
    """Show that mapped and classic SQLAlchemy columns can live together.

    Purpose: illustrate that Tigrbl supports SQLAlchemy 2.0-style ``Mapped``
    annotations while still relying on explicit ``Column`` declarations (the
    preferred pattern for clarity and long-term maintainability).

    Best practice: pick one style per codebase for consistency, but understand
    how to mix them when integrating legacy models.
    """

    # Setup: define a model using ``Mapped`` annotations with explicit Columns.
    class MappedWidget(Base, GUIDPk):
        __tablename__ = "mapped_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity: Mapped[int] = Column(Integer, default=0)

    # Setup: define the same model with classic Column declarations.
    class PlainWidget(Base, GUIDPk):
        __tablename__ = "plain_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity = Column(Integer, default=0)

    # Deployment: class creation generates table metadata for both styles.
    # Assertion: ensure the ``quantity`` column is present in both tables.
    assert "quantity" in MappedWidget.__table__.c
    assert "quantity" in PlainWidget.__table__.c


def test_mapped_and_nonmapped_share_column_defaults():
    """Compare defaults and types across mapped and classic columns.

    Purpose: confirm that both declaration styles end up with the same table
    metadata, which keeps downstream tooling consistent.

    Best practice: keep defaults in one place (the model) so that API and
    persistence layers agree on initial values.
    """

    # Setup: declare Mapped annotations with explicit Columns and defaults.
    class MappedWidget(Base, GUIDPk):
        __tablename__ = "mapped_widgets_defaults"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity: Mapped[int] = Column(Integer, default=0)

    # Setup: declare a classic Column-only model for comparison.
    class PlainWidget(Base, GUIDPk):
        __tablename__ = "plain_widgets_defaults"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        quantity = Column(Integer, default=0)

    # Deployment: inspect defaults on the generated table metadata.
    mapped_default = MappedWidget.__table__.c.quantity.default
    plain_default = PlainWidget.__table__.c.quantity.default

    # Assertion: both styles preserve the default value.
    assert mapped_default is not None
    assert plain_default is not None
    assert mapped_default.arg == 0
    assert plain_default.arg == 0
