# swarmauri/standard/tools/concrete/LexicalDensityTool.py
from typing import Dict, Any
from collections import Counter
from sswarmauri.tandard.tools.base.ToolBase import ToolBase

class LexicalDensityTool(ToolBase):
    """
    Computes the ratio of unique words to total words in the text to gauge its lexical richness.
    """
    version: str = "0.1.dev1"
    name: str = "LexicalDensityTool"
    type: Literal["LexicalDensityTool"] = "LexicalDensityTool"
    description: str = "Calculates the LexicalDensityTool for a given text."

    def execute(self, text: str) -> Dict[str, Any]:
        """
        Calculate the lexical density of the given text.

        Parameters:
            text (str): The input text to analyze.

        Returns:
            Dict[str, Any]: A dictionary with total words count, unique words count, 
                            and the lexical density ratio.
        """
        words = text.split()
        total_words = len(words)
        unique_words = len(set(words))
        lexical_density = unique_words / total_words if total_words > 0 else 0
        
        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "lexical_density": lexical_density
        }