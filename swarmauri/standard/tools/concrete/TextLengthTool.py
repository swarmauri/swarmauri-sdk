
from standard.tools.base.ToolBase import ToolBase
import re
from typing import Literal

class TextLengthTool(ToolBase):
    """
    A tool for measuring text length in terms of characters, words, and sentences.
    """
    name = "TextLengthTool"
    description: str = "This tool calculates the length of the text"
    type: Literal['TextLengthTool'] = 'TextLengthTool'

    def execute(self, data: str) -> dict:
        """
        Measure the length of the input text.
        
        Parameters:
        - data (str): The input text.
        
        Returns:
        - dict: A dictionary containing the number of characters, words, and sentences in the text.
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