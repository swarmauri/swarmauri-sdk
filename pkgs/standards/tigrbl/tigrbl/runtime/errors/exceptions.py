from __future__ import annotations

from typing import Any, Dict, Optional

from .utils import _read_in_errors, _has_in_errors


class TigrblError(Exception):
    """Base class for runtime errors in Tigrbl v3."""

    code: str = "tigrbl_error"
    status: int = 400

    def __init__(
        self,
        message: str = "",
        *,
        code: Optional[str] = None,
        status: Optional[int] = None,
        details: Any = None,
        cause: Optional[BaseException] = None,
    ):
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause
        if code is not None:
            self.code = code
        if status is not None:
            self.status = status
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "type": self.__class__.__name__,
            "code": self.code,
            "status": self.status,
            "message": str(self),
        }
        if self.details is not None:
            d["details"] = self.details
        return d


class PlanningError(TigrblError):
    code = "planning_error"
    status = 500


class LabelError(TigrblError):
    code = "label_error"
    status = 400


class ConfigError(TigrblError):
    code = "config_error"
    status = 400


class SystemStepError(TigrblError):
    code = "system_step_error"
    status = 500


class ValidationError(TigrblError):
    code = "validation_error"
    status = 422

    @staticmethod
    def from_ctx(
        ctx: Any, message: str = "Input validation failed."
    ) -> "ValidationError":
        return ValidationError(message, status=422, details=_read_in_errors(ctx))


class TransformError(TigrblError):
    code = "transform_error"
    status = 400


class DeriveError(TigrblError):
    code = "derive_error"
    status = 400


class KernelAbort(TigrblError):
    code = "kernel_abort"
    status = 403


def coerce_runtime_error(exc: BaseException, ctx: Any | None = None) -> TigrblError:
    """
    Map arbitrary exceptions to a typed TigrblError for consistent kernel handling.
    - Already TigrblError → return as-is
    - ValueError + ctx.temp['in_errors'] → ValidationError
    - Otherwise → generic TigrblError
    """
    if isinstance(exc, TigrblError):
        return exc
    if isinstance(exc, ValueError) and ctx is not None and _has_in_errors(ctx):
        return ValidationError.from_ctx(
            ctx, message=str(exc) or "Input validation failed."
        )
    return TigrblError(str(exc) or exc.__class__.__name__)


def raise_for_in_errors(ctx: Any) -> None:
    """Raise a typed ValidationError if ctx.temp['in_errors'] indicates invalid input."""
    if _has_in_errors(ctx):
        raise ValidationError.from_ctx(ctx)


__all__ = [
    "TigrblError",
    "PlanningError",
    "LabelError",
    "ConfigError",
    "SystemStepError",
    "ValidationError",
    "TransformError",
    "DeriveError",
    "KernelAbort",
    "coerce_runtime_error",
    "raise_for_in_errors",
]
