from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class LoggerFormatter(FormatterBase):
    """Concrete implementation of FormatterBase"""

    include_timestamp: bool = False
    include_process: bool = False
    include_thread: bool = False
    date_format: str = "%Y-%m-%d %H:%M:%S"

    def model_post_init(self, *args, **kwargs):
        format_parts = []

        if self.include_timestamp:
            format_parts.append("%(asctime)s")

        format_parts.append("[%(name)s]")
        format_parts.append("[%(levelname)s]")

        if self.include_process:
            format_parts.append("Process:%(process)d")

        if self.include_thread:
            format_parts.append("Thread:%(thread)d")

        format_parts.append("%(message)s")

        self.format = " ".join(format_parts)
