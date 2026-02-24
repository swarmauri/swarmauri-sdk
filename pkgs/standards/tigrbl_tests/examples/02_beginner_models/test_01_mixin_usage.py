from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_guidpk_mixin_adds_id_column():
    """Confirm the GUIDPk mixin injects a primary key column.

    Purpose: demonstrate the ergonomic win of reusing mixins for shared
    behavior, so new models start with a consistent identifier.

    Best practice: standardize primary keys via mixins to avoid duplicated
    column definitions and to simplify migrations across models.
    """

    # Setup: define a model that inherits GUIDPk for shared ID behavior.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonmixins"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: the mixin contributes the ID column at class creation.
    assert hasattr(Widget, "id")
    # Assertion: confirm the mixin is part of the inheritance chain.
    assert issubclass(Widget, GUIDPk)


def test_guidpk_mixin_marks_id_as_primary_key():
    """Teach how to verify primary key metadata on a mixin column.

    Purpose: show that the generated ``id`` column is not just present but
    correctly configured as the table's primary key.

    Best practice: validate primary key configuration in early tests to avoid
    surprises in ORM relationships and CRUD operations.
    """

    # Setup: declare another model with GUIDPk.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonmixinprimarykeys"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: table metadata now includes the primary key collection.
    primary_key_columns = {column.name for column in Widget.__table__.primary_key}
    # Assertion: ensure the mixin-provided ``id`` is the primary key.
    assert "id" in primary_key_columns
