"""This module defines the DisplayThemeEnum enumeration."""

from enum import Enum


class DisplayThemeEnum(str, Enum):
    """
    Enumeration for display theme options.

    This enum provides a limited set of choices for the display theme, ensuring that only
    valid values can be assigned to the display theme attribute in user settings.
    """

    LIGHT = "LIGHT"
    DARK = "DARK"
