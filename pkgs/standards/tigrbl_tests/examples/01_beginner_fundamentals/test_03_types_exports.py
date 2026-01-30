from examples._support import build_type_gallery_model
from tigrbl.types import Column, Integer, String


def test_types_exports_cover_column_basics():
    """Test types exports cover column basics."""
    Gallery = build_type_gallery_model()
    assert isinstance(Gallery.__table__.c.text, Column)
    assert isinstance(Gallery.__table__.c.integer.type, Integer)
    assert isinstance(Gallery.__table__.c.text.type, String)
