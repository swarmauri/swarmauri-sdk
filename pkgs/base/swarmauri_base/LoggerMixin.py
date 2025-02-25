import logging
from pydantic import BaseModel, ConfigDict
from typing import Optional, ClassVar, Union

from swarmauri_base.logging.LoggerBase import LoggerBase
from .SubclassUnion import SubclassUnion
from .DynamicBase import DynamicBase

@DynamicBase.register_model()
class LoggerMixin(BaseModel):
    # Class-level default logger is now a ObserveSubclassUnion[LoggerBase] instance.
    default_logger: ClassVar[Optional[Union[LoggerBase, SubclassUnion[LoggerBase]]]] = LoggerBase()

    # Instance-level logger: expected to be a ObserveSubclassUnion[LoggerBase].
    logger: Optional[SubclassUnion[LoggerBase]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args, logger: Optional[Union[SubclassUnion[LoggerBase]]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        # Directly assign the provided SubclassUnion[LoggerBase] or fallback to the class-level default.
        self.logger = logger or self.__class__.default_logger or LoggerBase(name=self.__class__.__name__)