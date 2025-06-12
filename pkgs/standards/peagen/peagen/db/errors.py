class PeagenError(Exception):
    """Base class for provenance API errors."""


class PeagenHashMismatchError(PeagenError):
    """Raised when a parent hash reference is invalid."""
