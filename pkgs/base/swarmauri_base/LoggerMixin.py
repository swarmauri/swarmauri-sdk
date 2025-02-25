import logging
from pydantic import BaseModel, ConfigDict
from typing import Optional, ClassVar

from swarmauri_base import FullUnion
from swarmauri_base.logging.LoggerBase import LoggerBase
from swarmauri_base.DynamicBase import DynamicBase

@DynamicBase.register_model()
class LoggerMixin(BaseModel):
    # Class-level default logger is now a FullUnion[LoggerBase] instance.
    default_logger: ClassVar[Optional[FullUnion[LoggerBase]]] = LoggerBase()

    # Instance-level logger: expected to be a FullUnion[LoggerBase].
    logger: Optional[FullUnion[LoggerBase]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, logger: Optional[FullUnion[LoggerBase]] = None) -> None:
        # Directly assign the provided FullUnion[LoggerBase] or fallback to the class-level default.
        self.logger = logger or self.default_logger