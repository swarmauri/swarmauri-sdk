"""Exceptions raised by the WebDAV storage adapter."""


class WebDAVError(RuntimeError):
    """Base exception for WebDAV protocol failures."""


class WebDAVLockedError(WebDAVError):
    """Raised when a WebDAV resource is locked."""


class WebDAVPreconditionError(WebDAVError):
    """Raised when a WebDAV precondition fails."""


class WebDAVInsufficientStorageError(WebDAVError, OSError):
    """Raised when the WebDAV server reports insufficient storage."""
