from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import S, acol
from tigrbl.types import Column, String


def test_mapped_column_specs_still_materialize_columns():
    """Explain that column specs still yield concrete SQLAlchemy columns.

    Purpose:
        Demonstrate that ``acol`` specs create real table columns even when
        a higher-level spec API is used.

    What this shows:
        - Spec-based columns appear in ``__table__`` just like explicit ones.
        - Storage specs keep schema details declarative and centralized.

    Best practice:
        Use specs for reusable column policies while retaining predictable
        SQLAlchemy metadata output.
    """

    # Setup: define a spec-based column with acol to generate metadata.
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_specs"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        tag = acol(storage=S(type_=String, nullable=False))

    # Deployment: not required; metadata exists on the mapped class.
    # Assertion: the spec-based column materializes as a real SQLAlchemy column.
    assert "tag" in Widget.__table__.c


def test_column_specs_preserve_storage_nullability():
    """Verify storage spec nullability flows into the table column.

    Purpose:
        Confirm that ``S(nullable=False)`` is honored when using ``acol``.

    What this shows:
        - Storage constraints are enforced at the column level.
        - Specs remain a safe abstraction over SQLAlchemy internals.

    Best practice:
        Encode constraints in storage specs to keep validation consistent across
        table definitions and schema generation.
    """

    # Setup: define a spec-based column and set nullable=False.
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_specs_nullable"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        tag = acol(storage=S(type_=String, nullable=False))

    # Deployment: not required; inspect the column metadata directly.
    # Assertion: column nullability follows the storage spec.
    assert Widget.__table__.c.tag.nullable is False
