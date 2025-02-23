import logging
from typing import List, Optional
from swarmauri_core.loggers.ILogger import ILogger
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

@ComponentBase.register_model()
class BaseLogger(ILogger, ComponentBase):
    handlers: Optional[List[BaseHandler]] = None
    default_level: int = logging.INFO
    default_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    resource: Optional[str] = Field(default=ResourceTypes.LOGGER, frozen=True)
    
    def compile_logger(self, logger_name: str = __name__) -> logging.Logger:
        """
        Compiles and returns a logging.Logger object with the configured handlers.
        If no handlers are provided, a default StreamHandler is attached.
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.default_level)
        
        # Remove any existing handlers to avoid duplicates
        logger.handlers = []
        
        if self.handlers:
            for handler_model in self.handlers:
                handler = handler_model.compile_handler()
                logger.addHandler(handler)
        else:
            # Fallback: add a default StreamHandler
            default_handler = logging.StreamHandler()
            default_handler.setLevel(self.default_level)
            default_formatter = logging.Formatter(self.default_format)
            default_handler.setFormatter(default_formatter)
            logger.addHandler(default_handler)
        
        return logger
