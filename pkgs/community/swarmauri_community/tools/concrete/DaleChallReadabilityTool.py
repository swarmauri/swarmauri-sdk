import textstat
from typing import Any, Dict, List, Literal
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class DaleChallReadabilityTool(ToolBase):
    """
    A tool for calculating the Dale-Chall Readability Score using the textstat library.

    Attributes:
        version (str): The version of the tool.
        name (str): The name of the tool.
        type (Literal["DaleChallReadabilityTool"]): The type of the tool.
        description (str): A brief description of what the tool does.
    """

    version: str = "0.1.dev1"
    name: str = "DaleChallReadabilityTool"
    type: Literal["DaleChallReadabilityTool"] = "DaleChallReadabilityTool"
    description: str = (
        "Calculates the Dale-Chall Readability Score for a given text using textstat."
    )
    parameters: List[Parameter] = [
        Parameter(
            name="input_text",
            type="string",
            description="The input text for which to calculate the Dale-Chall Readability Score.",
            required=True,
        )
    ]

    def __call__(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Executes the Dale-Chall Readability tool and returns the readability score using textstat.

        Parameters:
            data (Dict[str, Any]): The input data containing "input_text".

        Returns:
            Dict[str, float]: A dictionary containing the Dale-Chall Readability Score

        Raises:
            ValueError: If the input data is invalid.
        """
        if self.validate_input(data):
            text = data["input_text"]
            dale_chall_score = textstat.dale_chall_readability_score(text)
            return {"dale_chall_score": dale_chall_score}
        else:
            raise ValueError("Invalid input for DaleChallReadabilityTool.")

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validates the input data.

        Parameters:
            data (Dict[str, Any]): The input data to be validated.

        Returns:
            bool: True if the input data is valid, False otherwise.
        """
        required_keys = ["input_text"]
        return all(key in data for key in required_keys)
