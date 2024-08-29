from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class ColemanLiauIndexTool(ToolBase):
    version: str = "0.1.dev1"
        
    # Define the parameters required by the tool
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="text",
            type="string",
            description="The text for which you want to calculate the Coleman-Liau Index readability score.",
            required=True,
        )
    ])
    name: str = 'ColemanLiauIndexTool'
    description: str = "Calculates the readability score of a given text using the Coleman-Liau Index."
    type: Literal['ColemanLiauIndexTool'] = 'ColemanLiauIndexTool'

    def __call__(self, text: str) -> str:
        """
        Calculates the Coleman-Liau Index readability score for the provided text.
        
        Parameters:
            text (str): The text for which the readability score is calculated.
        
        Returns:
            str: The Coleman-Liau Index readability score.
        """
        return self.calculate_coleman_liau_index(text)
    
    def calculate_coleman_liau_index(self, text: str) -> str:
        """
        Calculates the Coleman-Liau Index readability score for the provided text.

        Args:
            text (str): The text for which the readability score is calculated.

        Returns:
            str: The Coleman-Liau Index readability score.
        """
        num_sentences = text.count('.') + text.count('!') + text.count('?')
        num_words = len(text.split())
        num_characters = sum(len(word) for word in text.split())

        # Ensure there are no zero values to avoid division by zero errors
        if num_sentences == 0 or num_words == 0:
            return "The provided text is insufficient for readability calculation."

        num_letters_per_100_words = num_characters / num_words * 100
        num_sentences_per_100_words = num_sentences / num_words * 100

        coleman_liau_index = (0.0588 * num_letters_per_100_words) - (0.296 * num_sentences_per_100_words) - 15.8

        return f"The Coleman-Liau Index readability score is {coleman_liau_index:.2f}"