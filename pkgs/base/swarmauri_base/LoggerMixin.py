import logging
from pydantic import BaseModel, ConfigDict
from typing import Optional, ClassVar

from swarmauri_base.logging.LoggerBase import LoggerBase
from .SubclassUnion import SubclassUnion
class LoggerMixin(BaseModel):
    # Class-level default logger is now a ObserveSubclassUnion[LoggerBase] instance.
    default_logger: ClassVar[Optional[SubclassUnion[LoggerBase]]] = None

    # Instance-level logger: expected to be a ObserveSubclassUnion[LoggerBase].
    logger: Optional[SubclassUnion[LoggerBase]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args, logger: Optional[SubclassUnion[LoggerBase]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        # Directly assign the provided SubclassUnion[LoggerBase] or fallback to the class-level default.
        self.logger = logger or self.__class__.default_logger or LoggerBase(name=self.__class__.__name__)