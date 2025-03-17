"""
exceptions.py

This module defines custom exception classes for the HTTP client package.
"""

class HttpClientError(Exception):
    """Base exception class for HTTP client errors."""
    pass

class HTTP2Error(HttpClientError):
    """Exception raised for HTTP/2 specific errors."""
    pass

class TimeoutError(HttpClientError):
    """Exception raised when a connection or operation times out."""
    pass

class FlowControlError(HttpClientError):
    """Exception raised when flow control violations occur."""
    pass

class ProtocolError(HttpClientError):
    """Exception raised when the client encounters a protocol violation."""
    pass
