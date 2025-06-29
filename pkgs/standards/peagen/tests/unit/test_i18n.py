from peagen.i18n import get_message, set_language


def test_get_message_in_spanish() -> None:
    set_language("es")
    try:
        assert get_message("cli.app_help").startswith("Herramienta CLI")
    finally:
        set_language("en")
