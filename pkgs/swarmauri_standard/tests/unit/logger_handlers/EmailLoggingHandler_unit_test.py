import logging
import unittest.mock as mock
from email.utils import formataddr

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.EmailLoggingHandler import EmailLoggingHandler


@pytest.mark.unit
class TestEmailLoggingHandler:
    """
    Unit tests for the EmailLoggingHandler class.
    """

    @pytest.fixture
    def basic_handler(self) -> EmailLoggingHandler:
        """
        Creates a basic EmailLoggingHandler instance for testing.

        Returns:
            EmailLoggingHandler: A configured handler instance.
        """
        return EmailLoggingHandler(toaddrs=["recipient@example.com"])

    @pytest.mark.unit
    def test_initialization(self, basic_handler: EmailLoggingHandler) -> None:
        """
        Test that the handler initializes with correct default values.

        Args:
            basic_handler: The fixture providing a basic handler instance.
        """
        assert basic_handler.type == "EmailLoggingHandler"
        assert basic_handler.mailhost == "localhost"
        assert basic_handler.fromaddr == "logger@example.com"
        assert basic_handler.toaddrs == ["recipient@example.com"]
        assert basic_handler.subject == "Logging Message"
        assert basic_handler.credentials is None
        assert basic_handler.secure is None
        assert basic_handler.timeout is None
        assert basic_handler.mail_from_display_name is None
        assert basic_handler.send_empty_entries is False
        assert basic_handler.html is False
        assert basic_handler.formatter is None

    @pytest.mark.unit
    def test_compile_handler_with_required_fields(
        self, basic_handler: EmailLoggingHandler
    ) -> None:
        """
        Test that the handler compiles correctly with only required fields.

        Args:
            basic_handler: The fixture providing a basic handler instance.
        """
        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            basic_handler.compile_handler()

            # Verify SMTPHandler was created with correct parameters
            mock_smtp_handler.assert_called_once_with(
                mailhost="localhost",
                fromaddr="logger@example.com",
                toaddrs=["recipient@example.com"],
                subject="Logging Message",
                credentials=None,
                secure=None,
                timeout=None,
            )

    @pytest.mark.unit
    def test_compile_handler_missing_toaddrs(self) -> None:
        """
        Test that the handler raises ValueError when toaddrs is empty.
        """
        handler = EmailLoggingHandler()
        with pytest.raises(ValueError, match="Email recipients .* must be specified"):
            handler.compile_handler()

    @pytest.mark.unit
    def test_from_address_with_display_name(self) -> None:
        """
        Test that the from address is formatted correctly when display name is provided.
        """
        handler = EmailLoggingHandler(
            toaddrs=["recipient@example.com"],
            fromaddr="sender@example.com",
            mail_from_display_name="Log System",
        )

        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            handler.compile_handler()

            # Verify the fromaddr was formatted with the display name
            expected_from = formataddr(("Log System", "sender@example.com"))
            mock_smtp_handler.assert_called_once()
            call_args = mock_smtp_handler.call_args[1]
            assert call_args["fromaddr"] == expected_from

    @pytest.mark.unit
    def test_html_formatting(self) -> None:
        """
        Test that HTML formatting is correctly applied when enabled.
        """
        handler = EmailLoggingHandler(toaddrs=["recipient@example.com"], html=True)

        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            mock_instance = mock_smtp_handler.return_value
            compiled_handler = handler.compile_handler()

            # Verify a formatter was set
            mock_instance.setFormatter.assert_called_once()

            # Test the monkey-patched getSubject method
            mock_instance.getSubject.return_value = "Test Subject"
            record = mock.MagicMock()
            subject = compiled_handler.getSubject(record)
            assert "Content-Type: text/html" in subject

    @pytest.mark.unit
    def test_custom_formatter(self) -> None:
        """
        Test that a custom formatter is correctly applied.
        """
        # Test with string formatter
        handler_with_str_formatter = EmailLoggingHandler(
            toaddrs=["recipient@example.com"], formatter="%(levelname)s: %(message)s"
        )

        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            mock_instance = mock_smtp_handler.return_value
            handler_with_str_formatter.compile_handler()

            # Verify setFormatter was called
            mock_instance.setFormatter.assert_called_once()

        # Test with FormatterBase instance
        mock_formatter = mock.MagicMock(spec=FormatterBase)
        mock_formatter.type = "FormatterBase"
        mock_formatter.compile_formatter.return_value = logging.Formatter("%(message)s")

        handler_with_obj_formatter = EmailLoggingHandler(
            toaddrs=["recipient@example.com"], formatter=mock_formatter
        )

        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            mock_instance = mock_smtp_handler.return_value
            handler_with_obj_formatter.compile_handler()

            # Verify the formatter's compile_formatter method was called
            mock_formatter.compile_formatter.assert_called_once()
            mock_instance.setFormatter.assert_called_once_with(
                mock_formatter.compile_formatter.return_value
            )

    @pytest.mark.unit
    def test_empty_entries_handling(self) -> None:
        """
        Test that empty log entries are handled according to configuration.
        """
        handler = EmailLoggingHandler(
            toaddrs=["recipient@example.com"], send_empty_entries=False
        )

        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            mock_instance = mock_smtp_handler.return_value

            original_emit = mock.MagicMock()
            mock_instance.emit = original_emit

            compiled_handler = handler.compile_handler()

            # Create test records
            empty_record = mock.MagicMock()
            empty_record.getMessage.return_value = "   "  # Only whitespace

            non_empty_record = mock.MagicMock()
            non_empty_record.getMessage.return_value = "This is a message"

            # Test that empty record is filtered out
            compiled_handler.emit(empty_record)
            original_emit.assert_not_called()

            # Test that non-empty record is processed
            compiled_handler.emit(non_empty_record)
            original_emit.assert_called_once_with(non_empty_record)

    @pytest.mark.unit
    def test_get_configuration(self, basic_handler: EmailLoggingHandler) -> None:
        """
        Test that get_configuration returns the correct configuration dictionary.

        Args:
            basic_handler: The fixture providing a basic handler instance.
        """
        config = basic_handler.get_configuration()

        assert config["type"] == "EmailLoggingHandler"
        assert config["mailhost"] == "localhost"
        assert config["fromaddr"] == "logger@example.com"
        assert config["toaddrs"] == ["recipient@example.com"]
        assert config["subject"] == "Logging Message"
        assert config["credentials"] is None
        assert config["secure"] is None
        assert config["html"] is False
        assert config["formatter"] is None

    @pytest.mark.unit
    def test_credentials_redaction(self) -> None:
        """
        Test that credentials are properly redacted in the configuration.
        """
        handler = EmailLoggingHandler(
            toaddrs=["recipient@example.com"], credentials=("username", "password")
        )

        config = handler.get_configuration()
        assert config["credentials"] == "***REDACTED***"

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "secure_param, expected_result",
        [
            (True, True),
            (False, False),
            (None, None),
            (("keyfile", "certfile", "password"), True),
        ],
    )
    def test_secure_parameter_handling(self, secure_param, expected_result) -> None:
        """
        Test that the secure parameter is handled correctly in the configuration.

        Args:
            secure_param: The value to set for the secure parameter.
            expected_result: The expected result in the configuration.
        """
        handler = EmailLoggingHandler(
            toaddrs=["recipient@example.com"], secure=secure_param
        )

        config = handler.get_configuration()
        assert config["secure"] == expected_result

    @pytest.mark.unit
    def test_mailhost_tuple(self) -> None:
        """
        Test that mailhost can be specified as a (host, port) tuple.
        """
        handler = EmailLoggingHandler(
            toaddrs=["recipient@example.com"], mailhost=("smtp.example.com", 587)
        )

        with mock.patch("logging.handlers.SMTPHandler") as mock_smtp_handler:
            handler.compile_handler()

            mock_smtp_handler.assert_called_once()
            call_args = mock_smtp_handler.call_args[1]
            assert call_args["mailhost"] == ("smtp.example.com", 587)
