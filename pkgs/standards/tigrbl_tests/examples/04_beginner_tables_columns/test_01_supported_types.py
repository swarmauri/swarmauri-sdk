from examples._support import build_type_gallery_model


def test_type_gallery_defines_all_supported_columns():
    """Test type gallery defines all supported columns."""
    Gallery = build_type_gallery_model()
    column_names = set(Gallery.__table__.c.keys())
    expected = {
        "text",
        "boolean",
        "integer",
        "numeric",
        "json",
        "datetime",
        "tzdatetime",
        "binary",
        "enum",
        "array",
        "jsonb",
        "pgenum",
        "pguuid",
        "tsvector",
    }
    assert expected.issubset(column_names)
