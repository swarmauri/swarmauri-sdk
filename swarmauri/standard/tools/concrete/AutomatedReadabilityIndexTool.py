from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class AutomatedReadabilityIndex(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="text",
            type="string",
            description="The text to calculate the readability index for.",
            required=True
        )
    ])
    
    name: str = 'AutomatedReadabilityIndex'
    description: str = "Calculates the readability of a given text using the Automated Readability Index (ARI)."
    type: Literal['AutomatedReadabilityIndex'] = 'AutomatedReadabilityIndex'

    def __call__(self, text: str) -> float:
        """
        Calculates the readability of the given text using the Automated Readability Index (ARI).

        Parameters:
        - text (str): The text to calculate the readability index for.

        Returns:
        - float: The calculated ARI.
        """
        return self.calculate_ari(text)
    
    def calculate_ari(self, text: str) -> float:
        """
        Calculates the Automated Readability Index (ARI) for the provided text.

        Args:
            text (str): The input text to calculate the ARI for.

        Returns:
            float: The calculated ARI.
        """
        num_chars = len(text)
        num_words = len(text.split())
        num_sentences = text.count('.') + text.count('!') + text.count('?')

        if num_words == 0 or num_sentences == 0:
            return 0.0

        ari = 4.71 * (num_chars / num_words) + 0.5 * (num_words / num_sentences) - 21.43
        return max(0.0, ari)