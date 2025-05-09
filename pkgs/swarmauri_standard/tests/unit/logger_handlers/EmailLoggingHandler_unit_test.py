import logging
from email.message import EmailMessage
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_standard.logger_handlers.EmailLoggingHandler import (
    CustomSMTPHandler,
    EmailLoggingHandler,
)


@pytest.fixture
def basic_email_handler():
    """
    Fixture providing a basic EmailLoggingHandler instance with minimal configuration.
    """
    return EmailLoggingHandler(
        smtp_server="smtp.example.com",
        from_addr="sender@example.com",
        to_addrs=["recipient@example.com"],
    )


@pytest.fixture
def full_email_handler():
    """
    Fixture providing a fully configured EmailLoggingHandler instance.
    """
    return EmailLoggingHandler(
        smtp_server="smtp.example.com",
        smtp_port=465,
        use_tls=False,
        use_ssl=True,
        username="user",
        password="pass",
        from_addr="sender@example.com",
        to_addrs=["recipient1@example.com", "recipient2@example.com"],
        subject="Critical Log Alert",
        level=logging.CRITICAL,
        formatter="%(levelname)s - %(message)s",
    )


@pytest.mark.unit
def test_email_handler_type():
    """
    Test that the EmailLoggingHandler has the correct type attribute.
    """
    assert EmailLoggingHandler.type == "EmailLoggingHandler"


@pytest.mark.unit
def test_email_handler_default_values():
    """
    Test the default values of EmailLoggingHandler.
    """
    handler = EmailLoggingHandler(
        smtp_server="smtp.example.com",
        from_addr="sender@example.com",
        to_addrs=["recipient@example.com"],
    )

    assert handler.smtp_port == 587
    assert handler.use_tls is True
    assert handler.use_ssl is False
    assert handler.username is None
    assert handler.password is None
    assert handler.subject == "Log Message"
    assert handler.level == logging.ERROR
    assert handler.formatter is None


@pytest.mark.unit
def test_compile_handler_basic(basic_email_handler):
    """
    Test that compile_handler creates a CustomSMTPHandler with basic configuration.
    """
    with patch(
        "swarmauri_standard.logger_handlers.EmailLoggingHandler.CustomSMTPHandler"
    ) as mock_handler:
        basic_email_handler.compile_handler()

        # Verify the handler was created with the right parameters
        mock_handler.assert_called_once()
        args, kwargs = mock_handler.call_args

        assert kwargs["mailhost"] == ("smtp.example.com", 587)
        assert kwargs["fromaddr"] == "sender@example.com"
        assert kwargs["toaddrs"] == ["recipient@example.com"]
        assert kwargs["subject"] == "Log Message"
        assert kwargs["credentials"] is None
        assert kwargs["secure"] == ()  # Using TLS by default
        assert kwargs["use_ssl"] is False


@pytest.mark.unit
def test_compile_handler_full(full_email_handler):
    """
    Test that compile_handler creates a CustomSMTPHandler with full configuration.
    """
    with patch(
        "swarmauri_standard.logger_handlers.EmailLoggingHandler.CustomSMTPHandler"
    ) as mock_handler:
        full_email_handler.compile_handler()

        # Verify the handler was created with the right parameters
        mock_handler.assert_called_once()
        args, kwargs = mock_handler.call_args

        assert kwargs["mailhost"] == ("smtp.example.com", 465)
        assert kwargs["fromaddr"] == "sender@example.com"
        assert kwargs["toaddrs"] == ["recipient1@example.com", "recipient2@example.com"]
        assert kwargs["subject"] == "Critical Log Alert"
        assert kwargs["credentials"] == ("user", "pass")
        assert kwargs["secure"] is None  # Not using TLS
        assert kwargs["use_ssl"] is True


@pytest.mark.unit
def test_compile_handler_formatter_string(basic_email_handler):
    """
    Test that compile_handler correctly sets a string formatter.
    """
    basic_email_handler.formatter = "%(levelname)s: %(message)s"

    with patch(
        "swarmauri_standard.logger_handlers.EmailLoggingHandler.CustomSMTPHandler"
    ) as mock_handler:
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance

        basic_email_handler.compile_handler()

        # Verify a formatter was set
        mock_instance.setFormatter.assert_called_once()
        formatter = mock_instance.setFormatter.call_args[0][0]
        assert isinstance(formatter, logging.Formatter)
        assert formatter._fmt == "%(levelname)s: %(message)s"


@pytest.mark.unit
def test_compile_handler_formatter_object(basic_email_handler):
    """
    Test that compile_handler correctly sets a formatter object.
    """
    mock_formatter = MagicMock()
    mock_compiled_formatter = MagicMock()
    mock_formatter.compile_formatter.return_value = mock_compiled_formatter

    basic_email_handler.formatter = mock_formatter

    with patch(
        "swarmauri_standard.logger_handlers.EmailLoggingHandler.CustomSMTPHandler"
    ) as mock_handler:
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance

        basic_email_handler.compile_handler()

        # Verify the formatter was compiled and set
        mock_formatter.compile_formatter.assert_called_once()
        mock_instance.setFormatter.assert_called_once_with(mock_compiled_formatter)


@pytest.mark.unit
def test_compile_handler_default_formatter(basic_email_handler):
    """
    Test that compile_handler sets a default formatter when none is provided.
    """
    with patch(
        "swarmauri_standard.logger_handlers.EmailLoggingHandler.CustomSMTPHandler"
    ) as mock_handler:
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance

        basic_email_handler.compile_handler()

        # Verify a formatter was set
        mock_instance.setFormatter.assert_called_once()
        formatter = mock_instance.setFormatter.call_args[0][0]
        assert isinstance(formatter, logging.Formatter)
        assert "Time: %(asctime)s" in formatter._fmt


@pytest.mark.unit
def test_custom_smtp_handler_init():
    """
    Test the initialization of CustomSMTPHandler.
    """
    # Test with host and port as tuple
    handler1 = CustomSMTPHandler(
        mailhost=("smtp.example.com", 587),
        fromaddr="sender@example.com",
        toaddrs=["recipient@example.com"],
        subject="Test Subject",
    )
    assert handler1.mailhost == "smtp.example.com"
    assert handler1.mailport == 587

    # Test with host as string (default port)
    handler2 = CustomSMTPHandler(
        mailhost="smtp.example.com",
        fromaddr="sender@example.com",
        toaddrs="recipient@example.com",  # Test single recipient as string
        subject="Test Subject",
    )
    assert handler2.mailhost == "smtp.example.com"
    assert handler2.mailport == 25
    assert handler2.toaddrs == ["recipient@example.com"]  # Should be converted to list


@pytest.mark.unit
def test_custom_smtp_handler_emit_tls():
    """
    Test the emit method of CustomSMTPHandler with TLS.
    """
    handler = CustomSMTPHandler(
        mailhost=("smtp.example.com", 587),
        fromaddr="sender@example.com",
        toaddrs=["recipient@example.com"],
        subject="Test Subject",
        credentials=("user", "pass"),
        secure=(),  # Use TLS
    )

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test_path",
        lineno=42,
        msg="Test error message",
        args=(),
        exc_info=None,
    )

    # Mock the format method
    handler.format = MagicMock(return_value="Formatted log message")

    # Mock SMTP
    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = MagicMock()
        mock_smtp.return_value = smtp_instance

        handler.emit(record)

        # Verify SMTP was initialized correctly
        mock_smtp.assert_called_once_with("smtp.example.com", 587)

        # Verify TLS was started
        smtp_instance.ehlo.assert_called()
        smtp_instance.starttls.assert_called_once()

        # Verify login
        smtp_instance.login.assert_called_once_with("user", "pass")

        # Verify email was sent
        smtp_instance.send_message.assert_called_once()
        email_msg = smtp_instance.send_message.call_args[0][0]
        assert isinstance(email_msg, EmailMessage)
        assert email_msg["From"] == "sender@example.com"
        assert email_msg["To"] == "recipient@example.com"
        assert email_msg["Subject"] == "Test Subject: ERROR"

        # Verify connection was closed
        smtp_instance.quit.assert_called_once()


@pytest.mark.unit
def test_custom_smtp_handler_emit_ssl():
    """
    Test the emit method of CustomSMTPHandler with SSL.
    """
    handler = CustomSMTPHandler(
        mailhost=("smtp.example.com", 465),
        fromaddr="sender@example.com",
        toaddrs=["recipient1@example.com", "recipient2@example.com"],
        subject="Test Subject",
        use_ssl=True,
    )

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.CRITICAL,
        pathname="test_path",
        lineno=42,
        msg="Test critical message",
        args=(),
        exc_info=None,
    )

    # Mock the format method
    handler.format = MagicMock(return_value="Formatted log message")

    # Mock SMTP_SSL
    with patch("smtplib.SMTP_SSL") as mock_smtp_ssl:
        smtp_instance = MagicMock()
        mock_smtp_ssl.return_value = smtp_instance

        handler.emit(record)

        # Verify SMTP_SSL was initialized correctly
        mock_smtp_ssl.assert_called_once_with("smtp.example.com", 465)

        # Verify no TLS (using SSL instead)
        assert (
            not hasattr(smtp_instance, "starttls") or not smtp_instance.starttls.called
        )

        # Verify no login (no credentials provided)
        assert not smtp_instance.login.called

        # Verify email was sent
        smtp_instance.send_message.assert_called_once()
        email_msg = smtp_instance.send_message.call_args[0][0]
        assert isinstance(email_msg, EmailMessage)
        assert email_msg["From"] == "sender@example.com"
        assert email_msg["To"] == "recipient1@example.com, recipient2@example.com"
        assert email_msg["Subject"] == "Test Subject: CRITICAL"
