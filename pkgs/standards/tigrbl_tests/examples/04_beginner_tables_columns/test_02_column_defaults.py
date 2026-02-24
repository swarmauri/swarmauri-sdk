from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, String


def test_column_defaults_apply_on_instantiation():
    """Confirm default values are registered in column metadata.

    Purpose: show that defaults live on the column object and are discoverable
    without a running database.

    Best practice: declare defaults at the schema layer so API and persistence
    logic stay aligned.
    """

    # Setup: define a model with a defaulted column.
    class DefaultWidget(Base, GUIDPk):
        __tablename__ = "default_widgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)
        count = Column(Integer, default=7)

    # Deployment: access the SQLAlchemy column default metadata.
    column_default = DefaultWidget.__table__.c.count.default
    # Assertion: verify the default value is stored.
    assert column_default is not None
    assert column_default.arg == 7


def test_required_columns_remain_non_nullable():
    """Reinforce that required columns are marked non-nullable.

    Purpose: demonstrate that the ``nullable=False`` flag is reflected in the
    generated table metadata, making validation expectations clear.

    Best practice: explicitly mark required fields to protect data integrity.
    """

    # Setup: declare another model with a required column.
    class DefaultWidget(Base, GUIDPk):
        __tablename__ = "default_widgets_required"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)
        count = Column(Integer, default=7)

    # Assertion: required fields are non-nullable in metadata.
    assert DefaultWidget.__table__.c.name.nullable is False
