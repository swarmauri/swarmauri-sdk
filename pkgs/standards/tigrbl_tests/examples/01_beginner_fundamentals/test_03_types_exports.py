import logging
import re

import pytest
from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, JSON, String, Text


def test_types_exports_cover_column_basics():
    """Verify that Tigrbl exports SQLAlchemy-compatible column types.

    Purpose: show that the ``tigrbl.types`` module re-exports familiar SQLAlchemy
    building blocks so learners can stay within the Tigrbl namespace.

    Best practice: import column types from a single module to keep model files
    tidy and avoid dependency sprawl.
    """

    # Setup: define a minimal gallery model using exported types.
    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery_basic"
        __allow_unmapped__ = True
        text = Column(Text)
        integer = Column(Integer)

    # Deployment: the class declaration registers a SQLAlchemy table.
    assert isinstance(Gallery.__table__.c.text, Column)
    # Exercise: check column type metadata.
    assert isinstance(Gallery.__table__.c.integer.type, Integer)
    assert isinstance(Gallery.__table__.c.text.type, String)


def test_types_exports_support_json_columns():
    """Show how JSON columns appear in the generated table metadata.

    Purpose: validate that richer types like JSON are still regular SQLAlchemy
    column objects, making them easy to inspect and migrate.

    Best practice: pick explicit JSON-capable types for structured data instead
    of overloading text columns, keeping schemas self-describing.
    """

    # Setup: declare a model that includes a JSON column.
    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery_json"
        __allow_unmapped__ = True
        payload = Column(JSON)

    # Deployment: table metadata is available immediately.
    # Assertion: JSON columns are typed as JSON in metadata.
    assert isinstance(Gallery.__table__.c.payload.type, JSON)


def test_types_exports_allow_json_column_name_without_shadowing_json_type():
    """Ensure a ``json`` SQL column name can be used without model attribute shadowing.

    Purpose: keep ``json`` available as a column name while avoiding collisions
    with Pydantic ``BaseModel.json`` method names.

    Best practice: use a Python-safe attribute name plus explicit DB column name
    when names could collide with framework attributes.
    """

    class Gallery(Base, GUIDPk):
        __tablename__ = "type_gallery_json_shadow"
        __allow_unmapped__ = True
        json_data = Column("json", JSON)
        json_backup = Column(JSON)

    assert isinstance(Gallery.__table__.c.json.type, JSON)
    assert isinstance(Gallery.__table__.c.json_backup.type, JSON)


def test_types_exports_warn_when_json_attribute_shadows_basemodel_json():
    """Document Pydantic warning behavior when model attribute ``json`` is used."""

    warning_pattern = re.compile(
        r'Field name "json" in "Gallery(?:Read|Create|Update|Replace|Delete)?" shadows an attribute in parent "BaseModel"'
    )

    with pytest.warns(UserWarning) as captured_warnings:

        class Gallery(Base, GUIDPk):
            __tablename__ = "type_gallery_json_warning"
            __allow_unmapped__ = True
            json = Column(JSON)

    warning_messages = [str(warning.message) for warning in captured_warnings]
    assert any(warning_pattern.search(message) for message in warning_messages)

    logger = logging.getLogger(__name__)
    for message in warning_messages:
        logger.info("Captured expected schema warning: %s", message)

    assert isinstance(Gallery.__table__.c.json.type, JSON)
