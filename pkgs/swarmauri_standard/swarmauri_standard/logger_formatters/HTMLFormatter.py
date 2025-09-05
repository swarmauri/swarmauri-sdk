import html
import logging
from typing import Dict, Optional

from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class HTMLFormatter(FormatterBase):
    """
    Formatter that renders log messages as HTML for embedding in web pages.

    This formatter outputs log records as HTML snippets with appropriate tags for
    timestamp, level, message, and exception information. It supports custom CSS
    classes and inline styling options.

    Attributes:
        include_timestamp: Whether to include timestamp in the formatted output
        date_format: Format string for the timestamp
        css_class: CSS class to apply to the main log container
        level_css_classes: Dictionary mapping log levels to CSS classes
        use_colors: Whether to use colors for different log levels
        level_colors: Dictionary mapping log levels to HTML color codes
        include_line_breaks: Whether to add line breaks between log elements
    """

    include_timestamp: bool = True
    date_format: str = "%Y-%m-%d %H:%M:%S"
    css_class: Optional[str] = "log-entry"
    level_css_classes: Dict[str, str] = {
        "DEBUG": "log-debug",
        "INFO": "log-info",
        "WARNING": "log-warning",
        "ERROR": "log-error",
        "CRITICAL": "log-critical",
    }
    use_colors: bool = True
    level_colors: Dict[str, str] = {
        "DEBUG": "#888888",
        "INFO": "#0000FF",
        "WARNING": "#FF8C00",
        "ERROR": "#FF0000",
        "CRITICAL": "#8B0000",
    }
    include_line_breaks: bool = True

    def model_post_init(self, *args, **kwargs):
        """
        Initialize the formatter after the model is created.

        This method sets up the format string that will be used by the formatter.
        """
        # We'll override the compile_formatter method instead of setting format
        # since HTML formatting requires more complex logic than a simple format string
        pass

    def escape_html(self, text: str) -> str:
        """
        Escape HTML special characters in the given text.

        Args:
            text: The text to escape

        Returns:
            HTML-escaped text
        """
        return html.escape(str(text))

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a custom HTML logging.Formatter.

        Returns:
            A logging.Formatter that formats log records as HTML
        """
        return HTMLLoggingFormatter(self)


class HTMLLoggingFormatter(logging.Formatter):
    """
    Custom logging.Formatter implementation that outputs HTML-formatted logs.

    This class handles the actual formatting of log records into HTML.
    """

    def __init__(self, config: HTMLFormatter):
        """
        Initialize the HTML formatter with the given configuration.

        Args:
            config: The HTMLFormatter configuration to use
        """
        super().__init__()
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified log record as HTML.

        Args:
            record: The log record to format

        Returns:
            HTML-formatted log message
        """
        # Start with the main container div
        container_attrs = (
            f'class="{self.config.css_class}"' if self.config.css_class else ""
        )
        html_output = f"<div {container_attrs}>"

        # Add timestamp if configured
        if self.config.include_timestamp:
            timestamp = self.formatTime(record, self.config.date_format)
            html_output += f'<span class="log-timestamp">{timestamp}</span>'
            if self.config.include_line_breaks:
                html_output += " "

        # Add log level with appropriate styling
        level_name = record.levelname
        level_style = ""
        if self.config.use_colors and level_name in self.config.level_colors:
            level_style = f' style="color: {self.config.level_colors[level_name]}"'

        level_class = ""
        if level_name in self.config.level_css_classes:
            level_class = f' class="{self.config.level_css_classes[level_name]}"'

        html_output += f"<span{level_class}{level_style}>[{level_name}]</span>"

        # Add logger name
        html_output += f' <span class="log-name">[{record.name}]</span>'

        # Add the log message (escaped to prevent HTML injection)
        message = self.config.escape_html(record.getMessage())
        html_output += f' <span class="log-message">{message}</span>'

        # Add exception info if present
        if record.exc_info:
            # Format the exception info
            exc_text = self.formatException(record.exc_info)
            # Escape HTML characters and replace newlines with <br> tags
            exc_html = self.config.escape_html(exc_text).replace("\n", "<br>")
            html_output += f'<pre class="log-exception">{exc_html}</pre>'

        # Close the container div
        html_output += "</div>"

        return html_output
