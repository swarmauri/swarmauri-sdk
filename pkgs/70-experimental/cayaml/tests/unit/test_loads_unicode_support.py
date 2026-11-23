from cayaml import loads


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
    data = loads(yaml_str)
    assert data["emoji"] == "😀"
    assert data["accented"] == "Café"
    assert data["non_latin"] == "こんにちは"
