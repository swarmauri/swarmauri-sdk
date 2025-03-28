# swarmauri_base/logging/logger_formatters/LoggerFormatterBase.py
import logging
from swarmauri_core.logger_formatters.IFormatter import IFormatter
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class FormatterBase(IFormatter, ObserveBase):
    """Base implementation of a logger formatter."""

    format: str = "[%(name)s][%(levelname)s] %(message)s"
    date_format: str = None

    def compile_formatter(self) -> logging.Formatter:
        """Create and return a logging.Formatter with the configured format."""
        return logging.Formatter(self.format, self.date_format)
