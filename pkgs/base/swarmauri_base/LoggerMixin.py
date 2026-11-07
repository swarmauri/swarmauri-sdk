"""Mixin providing configurable loggers for models."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from swarmauri_base import FullUnion
from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.loggers.LoggerBase import LoggerBase


@DynamicBase.register_model()
class LoggerMixin(BaseModel):
    """Provide logger configuration fields to derived models."""

    # Class-level default logger is now a FullUnion[LoggerBase] instance.
    default_logger: ClassVar[FullUnion[LoggerBase] | None] = None

    # Instance-level logger: expected to be a FullUnion[LoggerBase].
    logger: FullUnion[LoggerBase] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(
        self, logger: FullUnion[LoggerBase] | None = None
    ) -> None:
        """Assign a logger instance after model initialization."""

        # Directly assign the provided FullUnion[LoggerBase] or fallback to the
        # class-level default.
        self.logger = self.logger or logger or self.default_logger
