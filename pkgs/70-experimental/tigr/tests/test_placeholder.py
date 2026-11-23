from tigr import placeholder


def test_placeholder_message() -> None:
    assert placeholder() == "tigr-placeholder"
