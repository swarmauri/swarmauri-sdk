import logging
from pydantic import BaseModel
from typing import List, Optional

class BaseLoggingHandler(BaseModel):
    level: int = logging.INFO
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    resource: Optional[str] = Field(default=ResourceTypes.LOGGINGHANDLER, frozen=True)

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a logging handler using the specified level and format.
        In this example, a StreamHandler is created.
        """
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        formatter = logging.Formatter(self.format)
        handler.setFormatter(formatter)
        return handler
