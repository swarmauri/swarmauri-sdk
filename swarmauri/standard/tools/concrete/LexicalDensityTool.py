from typing import Dict, Any, List, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class LexicalDensityTool(ToolBase):
    """
    Computes the ratio of unique words to total words in the text to gauge its lexical richness.

    Attributes:
        version (str): The version of the tool.
        name (str): The name of the tool.
        type (Literal["LexicalDensityTool"]): The type of the tool.
        description (str): A brief description of what the tool does.
        parameters (List[Parameter]): The parameters for configuring the tool.
    """
    version: str = "0.1.dev1"
    name: str = "LexicalDensityTool"
    type: Literal["LexicalDensityTool"] = "LexicalDensityTool"
    description: str = "Calculates the Lexical Density for a given text."
    parameters: List[Parameter] = [
        Parameter(
            name="text",
            type="string",
            description="The input text to analyze.",
            required=True
        )
    ]

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

    def __call__(self, text: str) -> Dict[str, Any]:
        """
        Calls the execute method to calculate the lexical density of the given text.
        
        Parameters:
            text (str): The input text to analyze.
        
        Returns:
            Dict[str, Any]: A dictionary with total words count, unique words count,
                            and the lexical density ratio.
        """
        return self.execute(text)