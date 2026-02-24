"""Lesson 08.1: Binding and rebinding models."""

from tigrbl import Base, bind, rebind
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_bind_and_rebind_update_specs():
    """Explain that bind/rebind rebuilds the same spec set.

    Purpose: show that calling `rebind` does not change the resolved OpSpecs
    when there are no mutations.
    Design practice: use `rebind` after changes to keep model state fresh.
    """

    # Setup: define a model so binding can build namespaces and columns.
    class LessonBind(Base, GUIDPk):
        __tablename__ = "lesson_bind"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind once to populate model metadata.
    bind(LessonBind)
    initial = LessonBind.__tigrbl_cols__

    # Test: rebind without changes.
    rebind(LessonBind)

    # Assertion: column metadata remains stable across rebind.
    assert LessonBind.__tigrbl_cols__ == initial


def test_bind_populates_ops_index():
    """Demonstrate that bind creates the ops index for discoverability.

    Purpose: verify that the model gains `ops.all` and alias-based lookups.
    Design practice: rely on `ops` for introspection rather than manual tracking.
    """

    # Setup: create a model with default operations.
    class LessonBindIndex(Base, GUIDPk):
        __tablename__ = "lesson_bind_index"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind to create the ops namespace.
    specs = bind(LessonBindIndex)

    # Test: inspect the ops index for aliases.
    assert LessonBindIndex.ops.all == specs

    # Assertion: default list is discoverable in the alias map.
    assert "list" in LessonBindIndex.ops.by_alias
