import re
from typing import Literal, List, Dict, Any
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class TextLengthTool(ToolBase):
    """
    A tool for measuring text length in terms of characters, words, and sentences.

    Attributes:
        name (str): The name of the tool.
        description (str): A brief description of the tool.
        type (Literal['TextLengthTool']): The type of the tool.
        parameters (List[Parameter]): The parameters for configuring the tool.
    """
    version: str = "1.0.0"
    name: str = "TextLengthTool"
    description: str = "This tool calculates the length of a given text."
    type: Literal['TextLengthTool'] = 'TextLengthTool'
    parameters: List[Parameter] = [
        Parameter(
            name="data",
            type="string",
            description="The input text to measure.",
            required=True
        )
    ]

    def execute(self, data: str) -> Dict[str, Any]:
        """
        Measure the length of the input text.
        
        Parameters:
            data (str): The input text.
        
        Returns:
            dict: A dictionary containing the number of characters, words, and sentences in the text.

        Raises:
            ValueError: If the input data is not a string.
        """
        if not isinstance(data, str):
            raise ValueError("Input data should be a string.")
        
        char_count = len(data)
        word_count = len(re.findall(r'\b\w+\b', data))
        sentence_count = len(re.findall(r'[.!?]', data))

        return {
            'characters': char_count,
            'words': word_count,
            'sentences': sentence_count
        }

    def __call__(self, data: str) -> Dict[str, Any]:
        """
        Calls the execute method to measure the length of the input text.
        
        Parameters:
            data (str): The input text.
        
        Returns:
            dict: A dictionary containing the number of characters, words, and sentences in the text.
        """
        return self.execute(data)