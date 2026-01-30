"""Lesson 09.3: Customizing default op wiring via providers."""

from tigrbl.types import OpConfigProvider


def test_op_config_provider_defaults_mode():
    """Explain how providers can opt out of default operations.

    Purpose: show that a provider can override the defaults mode to "none" and
    thus take full control over op registration.
    Design practice: set defaults mode explicitly when customizing ops.
    """

    # Setup: define a provider that disables default op wiring.
    class LessonOpProvider(OpConfigProvider):
        __tigrbl_defaults_mode__ = "none"

    # Assertion: the defaults mode reflects the declared configuration.
    assert LessonOpProvider.__tigrbl_defaults_mode__ == "none"


def test_op_config_provider_sets_include_exclude_sets():
    """Show that include/exclude sets can be configured.

    Purpose: demonstrate that providers can narrow or expand canonical ops
    without defining every spec manually.
    Design practice: use include/exclude for clarity and maintainability.
    """

    # Setup: define a provider that whitelists and blacklists ops.
    class LessonSelectiveProvider(OpConfigProvider):
        __tigrbl_defaults_mode__ = "some"
        __tigrbl_defaults_include__ = {"create", "read"}
        __tigrbl_defaults_exclude__ = {"delete"}

    # Assertion: include/exclude sets match the declared intent.
    assert LessonSelectiveProvider.__tigrbl_defaults_mode__ == "some"
    assert "create" in LessonSelectiveProvider.__tigrbl_defaults_include__
    assert "delete" in LessonSelectiveProvider.__tigrbl_defaults_exclude__
