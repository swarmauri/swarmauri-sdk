import pytest
from cayaml import round_trip_loads


@pytest.mark.xfail(
    reason="Unicode characters beyond basic ASCII not yet supported by cayaml."
)
def test_unicode_support():
    """
    Tests that YAML can handle various Unicode characters.
    Example includes accented characters, emojis, etc.
    """
    yaml_str = """
    emoji: "😀"
    accented: "Café"
    non_latin: "こんにちは"  # Japanese for 'Hello'
    """
    data = round_trip_loads(yaml_str)
    assert data["emoji"] == "😀"
    assert data["accented"] == "Café"
    assert data["non_latin"] == "こんにちは"
