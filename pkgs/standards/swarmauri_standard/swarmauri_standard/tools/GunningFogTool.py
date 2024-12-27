from swarmauri_core.typing import SubclassUnion
import re
from typing import Any, Dict, List, Literal
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class GunningFogTool(ToolBase):
    """
    A tool for calculating the Gunning-Fog readability score.

    Attributes:
        version (str): The version of the tool.
        name (str): The name of the tool.
        type (Literal["GunningFogTool"]): The type of the tool.
        description (str): A brief description of what the tool does.
        parameters (List[Parameter]): The parameters for configuring the tool.
    """

    version: str = "0.1.dev1"
    name: str = "GunningFogTool"
    type: Literal["GunningFogTool"] = "GunningFogTool"
    description: str = "Calculates the Gunning-Fog score for a given text."
    parameters: List[Parameter] = [
        Parameter(
            name="input_text",
            type="string",
            description="The input text for which to calculate the Gunning-Fog score.",
            required=True,
        )
    ]

    def __call__(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Executes the Gunning-Fog tool and returns the readability score.

        Gunning-Fog formula:
        0.4 * [(words/sentences) + 100 * (complex words/words)]

        Parameters:
            data (Dict[str, Any]): The input data containing "input_text".

        Returns:
            float: The Gunning-Fog readability score.

        Raises:
            ValueError: If the input data is invalid.
        """
        if self.validate_input(data):
            text = data["input_text"]
            num_sentences = self.count_sentences(text)
            num_words = self.count_words(text)
            num_complex_words = self.count_complex_words(text)
            if num_sentences == 0 or num_words == 0:
                return {"gunning_fog_score": 0.0}
            words_per_sentence = num_words / num_sentences
            complex_words_per_word = num_complex_words / num_words
            gunning_fog_score = 0.4 * (
                words_per_sentence + 100 * complex_words_per_word
            )
            return {"gunning_fog_score": gunning_fog_score}
        else:
            raise ValueError("Invalid input for GunningFogTool.")

    def count_sentences(self, text: str) -> int:
        """
        Counts the number of sentences in the text.

        Parameters:
            text (str): The input text.

        Returns:
            int: The number of sentences in the text.
        """
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])

    def count_words(self, text: str) -> int:
        """
        Counts the number of words in the text.

        Parameters:
            text (str): The input text.

        Returns:
            int: The number of words in the text.
        """
        words = re.findall(r"\b\w+\b", text)
        return len(words)

    def count_complex_words(self, text: str) -> int:
        """
        Counts the number of complex words (3 or more syllables) in the text.

        Parameters:
            text (str): The input text.

        Returns:
            int: The number of complex words in the text.
        """
        words = re.findall(r"\b\w+\b", text)
        complex_word_count = 0
        for word in words:
            if self.is_complex_word(word):
                complex_word_count += 1
        return complex_word_count

    def is_complex_word(self, word: str) -> bool:
        """
        Determines if a word is complex (3 or more syllables).

        Parameters:
            word (str): The input word.

        Returns:
            bool: True if the word is complex, False otherwise.
        """
        syllable_count = self.count_syllables_in_word(word)
        return syllable_count >= 3

    def count_syllables_in_word(self, word: str) -> int:
        """
        Counts the number of syllables in a word.

        Parameters:
            word (str): The word to count syllables in.

        Returns:
            int: The number of syllables in the word.
        """
        word = word.lower()
        syllable_count = len(re.findall(r"[aeiouy]+", word))
        return syllable_count

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validates the input data to ensure it contains the required 'input_text' key.

        Parameters:
            data (Dict[str, Any]): The input data to validate.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        return (
            isinstance(data, dict)
            and "input_text" in data
            and isinstance(data["input_text"], str)
        )


SubclassUnion.update(baseclass=ToolBase, type_name="GunningFogTool", obj=GunningFogTool)
