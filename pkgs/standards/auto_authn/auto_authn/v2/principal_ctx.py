import contextvars
principal_var = contextvars.ContextVar("principal", default=None)
__all__ = ["principal_var"]