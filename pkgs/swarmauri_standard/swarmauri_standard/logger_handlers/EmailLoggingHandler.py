import logging
import logging.handlers
from email.utils import formataddr
from typing import Any, Dict, List, Literal, Optional, Union

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class EmailLoggingHandler(HandlerBase):
    """
    A handler that sends log messages via email using SMTP.

    This handler extends the HandlerBase class to provide email logging functionality.
    It uses Python's SMTPHandler to send log records to specified recipients.
    """

    type: Literal["EmailLoggingHandler"] = "EmailLoggingHandler"

    # SMTP configuration
    mailhost: Union[str, tuple[str, int]] = (
        "localhost"  # Can be a host string or (host, port) tuple
    )
    credentials: Optional[tuple[str, str]] = None  # (username, password) tuple
    secure: Optional[Union[bool, tuple[str, str, str]]] = None  # Use TLS/SSL
    timeout: Optional[float] = None  # Connection timeout in seconds

    # Email content configuration
    fromaddr: str = "logger@example.com"
    toaddrs: List[str] = []
    subject: str = "Logging Message"

    # Additional email settings
    mail_from_display_name: Optional[str] = None
    send_empty_entries: bool = False

    # Email formatting
    html: bool = False
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles and returns an SMTPHandler configured with the provided settings.

        Returns:
            logging.Handler: A configured SMTPHandler instance.
        """
        # Validate required fields
        if not self.toaddrs:
            raise ValueError("Email recipients (toaddrs) must be specified")

        # Prepare from address with optional display name
        from_addr = self.fromaddr
        if self.mail_from_display_name:
            from_addr = formataddr((self.mail_from_display_name, self.fromaddr))

        # Create the SMTP handler
        handler = logging.handlers.SMTPHandler(
            mailhost=self.mailhost,
            fromaddr=from_addr,
            toaddrs=self.toaddrs,
            subject=self.subject,
            credentials=self.credentials,
            secure=self.secure,
            timeout=self.timeout,
        )

        # Set the log level
        handler.setLevel(self.level)

        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Default HTML or plain text formatter
            if self.html:
                default_formatter = logging.Formatter(
                    "<html><body><h2>%(levelname)s</h2>"
                    "<p><b>Logger:</b> %(name)s<br>"
                    "<b>Time:</b> %(asctime)s<br>"
                    "<b>Message:</b> %(message)s</p>"
                    "</body></html>",
                    "%Y-%m-%d %H:%M:%S",
                )
            else:
                default_formatter = logging.Formatter(
                    "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
                    "%Y-%m-%d %H:%M:%S",
                )
            handler.setFormatter(default_formatter)

        # Handle HTML content type if needed
        if self.html:
            # Add HTML content type header to emails
            # This is done by monkey patching the getSubject method
            original_get_subject = handler.getSubject

            def get_subject_with_content_type(record):
                subject = original_get_subject(record)
                return f"{subject}\nContent-Type: text/html"

            handler.getSubject = get_subject_with_content_type

        # Configure to not send empty log entries if specified
        if not self.send_empty_entries:
            original_emit = handler.emit

            def emit_if_not_empty(record):
                if record.getMessage().strip():
                    original_emit(record)

            handler.emit = emit_if_not_empty

        return handler

    def get_configuration(self) -> Dict[str, Any]:
        """
        Returns the configuration of this handler.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration.
        """
        return {
            "type": self.type,
            "level": self.level,
            "mailhost": self.mailhost,
            "fromaddr": self.fromaddr,
            "toaddrs": self.toaddrs,
            "subject": self.subject,
            "credentials": "***REDACTED***" if self.credentials else None,
            "secure": True if isinstance(self.secure, tuple) else self.secure,
            "html": self.html,
            "mail_from_display_name": self.mail_from_display_name,
            "send_empty_entries": self.send_empty_entries,
            "formatter": str(self.formatter) if self.formatter else None,
        }
