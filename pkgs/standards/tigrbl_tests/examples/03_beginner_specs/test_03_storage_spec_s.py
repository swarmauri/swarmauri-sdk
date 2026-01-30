from tigrbl.specs import S
from tigrbl.types import Integer


def test_storage_spec_captures_column_metadata():
    """Test storage spec captures column metadata."""
    storage = S(type_=Integer, nullable=False, primary_key=True)
    assert storage.type_ is Integer
    assert storage.primary_key is True
