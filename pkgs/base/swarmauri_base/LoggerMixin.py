import logging
from pydantic import BaseModel, ConfigDict
from typing import Optional, ClassVar, Union

from swarmauri_base import FullUnion
from swarmauri_base.logging.LoggerBase import LoggerBase
from swarmauri_base.DynamicBase import DynamicBase

@DynamicBase.register_model()
class LoggerMixin(BaseModel):
    # Class-level default logger is now a FullUnion[LoggerBase] instance.
    default_logger: ClassVar[Optional[FullUnion[LoggerBase]]] = None

    # Instance-level logger: expected to be a FullUnion[LoggerBase].
    logger: Optional[FullUnion[LoggerBase]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args, logger: Optional[FullUnion[LoggerBase]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        # Directly assign the provided FullUnion[LoggerBase] or fallback to the class-level default.
        self.logger = logger or LoggerBase(name=self.__class__.__name__)