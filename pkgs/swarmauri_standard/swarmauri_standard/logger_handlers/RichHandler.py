from typing import Optional, Union, Literal, Dict, Any
import logging
from rich.logging import RichHandler as RichHandlerLib
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "RichHandler")
class RichHandler(HandlerBase):
    """
    A handler that uses Rich library to provide colorized, formatted log output.
    
    This handler leverages the Rich library's RichHandler to produce visually appealing
    and informative log messages in the console with syntax highlighting, formatting,
    and other rich text features.
    """
    type: Literal["RichHandler"] = "RichHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    show_time: bool = True
    show_path: bool = True
    show_level: bool = True
    rich_tracebacks: bool = True
    tracebacks_extra_lines: int = 3
    tracebacks_theme: Optional[str] = None
    tracebacks_word_wrap: bool = True
    tracebacks_show_locals: bool = False
    omit_repeated_times: bool = True
    markup: bool = True
    highlighter: bool = True
    keywords: Optional[Dict[str, str]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a Rich logging handler with the specified configuration.
        
        The handler is configured with visual enhancements and formatting options
        based on the instance attributes.
        
        Returns:
            logging.Handler: A configured Rich logging handler
        """
        # Create Rich handler with specified options
        rich_handler = RichHandlerLib(
            level=self.level,
            show_time=self.show_time,
            show_path=self.show_path,
            show_level=self.show_level,
            rich_tracebacks=self.rich_tracebacks,
            tracebacks_extra_lines=self.tracebacks_extra_lines,
            tracebacks_theme=self.tracebacks_theme,
            tracebacks_word_wrap=self.tracebacks_word_wrap,
            tracebacks_show_locals=self.tracebacks_show_locals,
            omit_repeated_times=self.omit_repeated_times,
            markup=self.markup,
            highlighter=self.highlighter,
            keywords=self.keywords or {},
        )
        
        # Apply formatter if specified
        if self.formatter:
            if isinstance(self.formatter, str):
                # If formatter is a string, create a basic formatter
                rich_handler.setFormatter(logging.Formatter(self.formatter))
            else:
                # If formatter is a FormatterBase instance, compile and use it
                rich_handler.setFormatter(self.formatter.compile_formatter())
        
        # Note: Rich has its own default formatting, so we don't need to set a default formatter
        # if one isn't specified
        
        return rich_handler
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the handler configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the handler
        """
        base_dict = super().to_dict()
        # Add RichHandler specific properties
        rich_dict = {
            "show_time": self.show_time,
            "show_path": self.show_path,
            "show_level": self.show_level,
            "rich_tracebacks": self.rich_tracebacks,
            "tracebacks_extra_lines": self.tracebacks_extra_lines,
            "omit_repeated_times": self.omit_repeated_times,
            "markup": self.markup,
            "highlighter": self.highlighter,
        }
        
        # Only include non-None values
        if self.tracebacks_theme:
            rich_dict["tracebacks_theme"] = self.tracebacks_theme
        if self.keywords:
            rich_dict["keywords"] = self.keywords
            
        base_dict.update(rich_dict)
        return base_dict