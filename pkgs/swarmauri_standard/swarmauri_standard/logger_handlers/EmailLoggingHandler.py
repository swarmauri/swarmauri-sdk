import logging
import smtplib
from email.message import EmailMessage
from typing import List, Optional, Union, Literal
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "EmailLoggingHandler")
class EmailLoggingHandler(HandlerBase):
    """
    A logging handler that sends log messages via email.
    
    This handler emails logging records to specified recipients using SMTP,
    with support for customizable subject lines and secure connections.
    """
    type: Literal["EmailLoggingHandler"] = "EmailLoggingHandler"
    
    # SMTP configuration
    smtp_server: str
    smtp_port: int = 587
    use_tls: bool = True
    use_ssl: bool = False
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Email configuration
    from_addr: str
    to_addrs: List[str]
    subject: str = "Log Message"
    
    # Logging configuration
    level: int = logging.ERROR  # Default to ERROR level to avoid excessive emails
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    
    def compile_handler(self) -> logging.Handler:
        """
        Compiles an SMTPHandler for sending log messages via email.
        
        Returns:
            logging.Handler: Configured SMTPHandler instance.
        """
        # Create a custom SMTP handler
        handler = CustomSMTPHandler(
            mailhost=(self.smtp_server, self.smtp_port),
            fromaddr=self.from_addr,
            toaddrs=self.to_addrs,
            subject=self.subject,
            credentials=(self.username, self.password) if self.username and self.password else None,
            secure=() if self.use_tls else None,
            use_ssl=self.use_ssl
        )
        
        # Set the logging level
        handler.setLevel(self.level)
        
        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Default email-friendly formatter with more details
            default_formatter = logging.Formatter(
                "Time: %(asctime)s\nLogger: %(name)s\nLevel: %(levelname)s\n\nMessage: %(message)s"
            )
            handler.setFormatter(default_formatter)
        
        return handler


class CustomSMTPHandler(logging.Handler):
    """
    A custom SMTP handler that extends the functionality of logging.handlers.SMTPHandler.
    
    This implementation provides better error handling and supports both TLS and SSL.
    """
    
    def __init__(self, mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None, use_ssl=False):
        """
        Initialize the handler with the SMTP server details.
        
        Args:
            mailhost: SMTP server host and port tuple (host, port)
            fromaddr: From email address
            toaddrs: List of recipient email addresses
            subject: Email subject line
            credentials: Authentication credentials as (username, password)
            secure: Use TLS if not None
            use_ssl: Use SSL instead of TLS if True
        """
        super().__init__()
        if isinstance(mailhost, (list, tuple)):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost = mailhost
            self.mailport = 25
        
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs if isinstance(toaddrs, list) else [toaddrs]
        self.subject = subject
        self.credentials = credentials
        self.secure = secure
        self.use_ssl = use_ssl
    
    def emit(self, record):
        """
        Emit a record by sending an email.
        
        Args:
            record: Log record to format and send
        """
        try:
            # Format the record
            msg = self.format(record)
            
            # Create email message
            email = EmailMessage()
            email['From'] = self.fromaddr
            email['To'] = ', '.join(self.toaddrs)
            email['Subject'] = f"{self.subject}: {record.levelname}"
            email.set_content(msg)
            
            # Connect to SMTP server
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.mailhost, self.mailport)
            else:
                smtp = smtplib.SMTP(self.mailhost, self.mailport)
            
            # Use TLS if specified
            if self.secure and not self.use_ssl:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            
            # Authenticate if credentials are provided
            if self.credentials:
                smtp.login(self.credentials[0], self.credentials[1])
            
            # Send the email
            smtp.send_message(email)
            smtp.quit()
            
        except Exception:
            self.handleError(record)