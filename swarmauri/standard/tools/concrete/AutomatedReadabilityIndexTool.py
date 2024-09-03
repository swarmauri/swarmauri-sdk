import re
from typing import Any, Dict, List, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class AutomatedReadabilityIndexTool(ToolBase):
    """
    A tool for calculating the Automated Readability Index (ARI).

    Attributes:
        version (str): The version of the tool.
        name (str): The name of the tool.
        type (Literal["AutomatedReadabilityIndexTool"]): The type of the tool.
        description (str): A brief description of what the tool does.
        parameters (List[Parameter]): The parameters for configuring the tool.
    """
    version: str = "0.1.dev1"
    name: str = "AutomatedReadabilityIndexTool"
    type: Literal["AutomatedReadabilityIndexTool"] = "AutomatedReadabilityIndexTool"
    description: str = "Calculates the Automated Readability Index (ARI) for a given text."
    parameters: List[Parameter] = [
        Parameter(
            name="input_text",
            type="string",
            description="The input text for which to calculate the ARI.",
            required=True
        )
    ]

    def __call__(self, input_text: str) -> str:
        """
        Executes the ARI tool and returns the readability score.

        ARI formula:
        4.71 * (characters/words) + 0.5 * (words/sentences) - 21.43
        
        Parameters:
            data (Dict[str, Any]): The input data containing "input_text".
        
        Returns:
            float: The Automated Readability Index.

        Raises:
            ValueError: If the input data is invalid.
        """
        if self.validate_input(input_text):
            text = input_text
            num_sentences = self.count_sentences(text)
            num_words = self.count_words(text)
            num_characters = self.count_characters(text)
            if num_sentences == 0 or num_words == 0:
                return 0.0
            characters_per_word = num_characters / num_words
            words_per_sentence = num_words / num_sentences
            ari_score = 4.71 * characters_per_word + 0.5 * words_per_sentence - 21.43
            return str(ari_score)
        else:
            raise ValueError("Invalid input for AutomatedReadabilityIndexTool.")

    def count_sentences(self, text: str) -> int:
        """
        Counts the number of sentences in the text.
        
        Parameters:
            text (str): The input text.
        
        Returns:
            int: The number of sentences in the text.
        """
        sentence_endings = re.compile(r'[.!?]')
        sentences = sentence_endings.split(text)
        return len([s for s in sentences if s.strip()])  # Count non-empty sentences

    def count_words(self, text: str) -> int:
        """
        Counts the number of words in the text.
        
        Parameters:
            text (str): The input text.
        
        Returns:
            int: The number of words in the text.
        """
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def count_characters(self, text: str) -> int:
        """
        Counts the number of characters in the text.
        
        Parameters:
            text (str): The input text.
        
        Returns:
            int: The number of characters in the text.
        """
        return len(text) - text.count(' ')  # Count characters excluding spaces

    def validate_input(self, input_text: str) -> bool:
        """
        Validates the input data for the ARI tool.
        
        Parameters:
            data (Dict[str, Any]): The input data to validate.
        
        Returns:
            bool: True if the input is valid, False otherwise.
        """
        if isinstance(input_text, str):
            return True
        return False
