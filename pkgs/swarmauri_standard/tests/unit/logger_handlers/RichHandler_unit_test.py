import unittest
import pytest
import logging
from unittest.mock import patch, MagicMock
from typing import Any

from swarmauri_standard.logger_handlers.RichHandler import RichHandler
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase


@pytest.mark.unit
class TestRichHandler(unittest.TestCase):
    """
    Unit tests for the RichHandler class.

    Tests the functionality of the RichHandler class, including initialization,
    handler compilation, and dictionary conversion.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.handler = RichHandler()

    @pytest.mark.unit
    def test_inheritance(self):
        """Test that RichHandler inherits from HandlerBase."""
        self.assertIsInstance(self.handler, HandlerBase)

    @pytest.mark.unit
    def test_default_attributes(self):
        """Test the default attribute values of RichHandler."""
        self.assertEqual(self.handler.type, "RichHandler")
        self.assertEqual(self.handler.level, logging.INFO)
        self.assertIsNone(self.handler.formatter)
        self.assertTrue(self.handler.show_time)
        self.assertTrue(self.handler.show_path)
        self.assertTrue(self.handler.show_level)
        self.assertTrue(self.handler.rich_tracebacks)
        self.assertEqual(self.handler.tracebacks_extra_lines, 3)
        self.assertIsNone(self.handler.tracebacks_theme)
        self.assertTrue(self.handler.tracebacks_word_wrap)
        self.assertFalse(self.handler.tracebacks_show_locals)
        self.assertTrue(self.handler.omit_repeated_times)
        self.assertTrue(self.handler.markup)
        self.assertTrue(self.handler.highlighter)
        self.assertIsNone(self.handler.keywords)

    @pytest.mark.unit
    @patch("swarmauri_standard.logger_handlers.RichHandler.RichHandlerLib")
    def test_compile_handler_with_default_values(self, mock_rich_handler_lib):
        """Test that compile_handler creates a RichHandler with default values."""
        mock_instance = MagicMock()
        mock_rich_handler_lib.return_value = mock_instance

        result = self.handler.compile_handler()

        mock_rich_handler_lib.assert_called_once_with(
            level=logging.INFO,
            show_time=True,
            show_path=True,
            show_level=True,
            rich_tracebacks=True,
            tracebacks_extra_lines=3,
            tracebacks_theme=None,
            tracebacks_word_wrap=True,
            tracebacks_show_locals=False,
            omit_repeated_times=True,
            markup=True,
            highlighter=True,
            keywords={},
        )
        self.assertEqual(result, mock_instance)

    @pytest.mark.unit
    @patch("swarmauri_standard.logger_handlers.RichHandler.RichHandlerLib")
    def test_compile_handler_with_custom_values(self, mock_rich_handler_lib):
        """Test that compile_handler creates a RichHandler with custom values."""
        mock_instance = MagicMock()
        mock_rich_handler_lib.return_value = mock_instance

        custom_handler = RichHandler(
            level=logging.DEBUG,
            show_time=False,
            show_path=False,
            show_level=False,
            rich_tracebacks=False,
            tracebacks_extra_lines=5,
            tracebacks_theme="monokai",
            tracebacks_word_wrap=False,
            tracebacks_show_locals=True,
            omit_repeated_times=False,
            markup=False,
            highlighter=False,
            keywords={"error": "red"},
        )

        result = custom_handler.compile_handler()

        mock_rich_handler_lib.assert_called_once_with(
            level=logging.DEBUG,
            show_time=False,
            show_path=False,
            show_level=False,
            rich_tracebacks=False,
            tracebacks_extra_lines=5,
            tracebacks_theme="monokai",
            tracebacks_word_wrap=False,
            tracebacks_show_locals=True,
            omit_repeated_times=False,
            markup=False,
            highlighter=False,
            keywords={"error": "red"},
        )
        self.assertEqual(result, mock_instance)

    @pytest.mark.unit
    @patch("swarmauri_standard.logger_handlers.RichHandler.RichHandlerLib")
    @patch("swarmauri_standard.logger_handlers.RichHandler.logging.Formatter")
    def test_compile_handler_with_string_formatter(
        self, mock_formatter, mock_rich_handler_lib
    ):
        """Test that compile_handler correctly applies a string formatter."""
        mock_handler = MagicMock()
        mock_rich_handler_lib.return_value = mock_handler
        mock_formatter_instance = MagicMock()
        mock_formatter.return_value = mock_formatter_instance

        handler_with_formatter = RichHandler(
            formatter="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler_with_formatter.compile_handler()

        mock_formatter.assert_called_once_with(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        mock_handler.setFormatter.assert_called_once_with(mock_formatter_instance)

    @pytest.mark.unit
    @patch("swarmauri_standard.logger_handlers.RichHandler.RichHandlerLib")
    def test_compile_handler_with_formatter_object(self, mock_rich_handler_lib):
        """Test that compile_handler correctly applies a FormatterBase object."""
        mock_handler = MagicMock()
        mock_rich_handler_lib.return_value = mock_handler

        mock_formatter = MagicMock()
        mock_formatter_instance = MagicMock()
        mock_formatter.compile_formatter.return_value = mock_formatter_instance

        handler_with_formatter = RichHandler(formatter=mock_formatter)
        handler_with_formatter.compile_handler()

        mock_formatter.compile_formatter.assert_called_once()
        mock_handler.setFormatter.assert_called_once_with(mock_formatter_instance)

    @pytest.mark.unit
    def test_to_dict_with_default_values(self):
        """Test that to_dict returns the correct dictionary with default values."""
        result = self.handler.to_dict()

        # Check that all required keys are present
        expected_keys = [
            "type",
            "level",
            "show_time",
            "show_path",
            "show_level",
            "rich_tracebacks",
            "tracebacks_extra_lines",
            "omit_repeated_times",
            "markup",
            "highlighter",
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # Check that optional keys with None values are not included
        self.assertNotIn("tracebacks_theme", result)
        self.assertNotIn("keywords", result)

        # Check specific values
        self.assertEqual(result["type"], "RichHandler")
        self.assertEqual(result["level"], logging.INFO)
        self.assertTrue(result["show_time"])
        self.assertTrue(result["show_path"])
        self.assertTrue(result["show_level"])
        self.assertTrue(result["rich_tracebacks"])
        self.assertEqual(result["tracebacks_extra_lines"], 3)
        self.assertTrue(result["omit_repeated_times"])
        self.assertTrue(result["markup"])
        self.assertTrue(result["highlighter"])

    @pytest.mark.unit
    def test_to_dict_with_custom_values(self):
        """Test that to_dict returns the correct dictionary with custom values."""
        custom_handler = RichHandler(
            level=logging.DEBUG,
            show_time=False,
            show_path=False,
            show_level=False,
            rich_tracebacks=False,
            tracebacks_extra_lines=5,
            tracebacks_theme="monokai",
            tracebacks_word_wrap=False,
            tracebacks_show_locals=True,
            omit_repeated_times=False,
            markup=False,
            highlighter=False,
            keywords={"error": "red"},
        )

        result = custom_handler.to_dict()

        # Check that optional keys with non-None values are included
        self.assertIn("tracebacks_theme", result)
        self.assertEqual(result["tracebacks_theme"], "monokai")

        self.assertIn("keywords", result)
        self.assertEqual(result["keywords"], {"error": "red"})

        # Check specific custom values
        self.assertEqual(result["level"], logging.DEBUG)
        self.assertFalse(result["show_time"])
        self.assertFalse(result["show_path"])
        self.assertFalse(result["show_level"])
        self.assertFalse(result["rich_tracebacks"])
        self.assertEqual(result["tracebacks_extra_lines"], 5)
        self.assertFalse(result["omit_repeated_times"])
        self.assertFalse(result["markup"])
        self.assertFalse(result["highlighter"])


@pytest.mark.unit
@pytest.mark.parametrize(
    "attribute,value,expected",
    [
        ("level", logging.DEBUG, logging.DEBUG),
        ("show_time", False, False),
        ("show_path", False, False),
        ("show_level", False, False),
        ("rich_tracebacks", False, False),
        ("tracebacks_extra_lines", 10, 10),
        ("tracebacks_theme", "dark", "dark"),
        ("tracebacks_word_wrap", False, False),
        ("tracebacks_show_locals", True, True),
        ("omit_repeated_times", False, False),
        ("markup", False, False),
        ("highlighter", False, False),
        ("keywords", {"warning": "yellow"}, {"warning": "yellow"}),
    ],
)
def test_attribute_setting(attribute: str, value: Any, expected: Any):
    """
    Test that attributes can be correctly set and retrieved.

    Args:
        attribute: The attribute name to test
        value: The value to set
        expected: The expected value after setting
    """
    handler = RichHandler(**{attribute: value})
    assert getattr(handler, attribute) == expected
