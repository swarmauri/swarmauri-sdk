"""peagen.exceptions

Exception classes used by the Peagen package.
"""

class PatchTargetMissingError(ValueError):
    """Patch operation refers to a non-existent path in the template."""

