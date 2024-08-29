import re
from typing import Any, Dict, List, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class GunningFogIndexTool(ToolBase):
    """
    A tool for calculating the Gunning Fog Index readability score.

    Attributes:
        version (str): The version of the tool.
        name (str): The name of the tool.
        type (Literal["GunningFogIndexTool"]): The type of the tool.
        description (str): A brief description of what the tool does.
        parameters (List[Parameter]): The parameters for configuring the tool.
    """
    version: str = "0.1.dev1"
    name: str = "GunningFogIndexTool"
    type: Literal["GunningFogIndexTool"] = "GunningFogIndexTool"
    description: str = "Calculates the Gunning Fog Index for a given text."
    parameters: List[Parameter] = [
        Parameter(
            name="input_text",
            type="string",
            description="The input text for which to calculate the Gunning Fog Index.",
            required=True
        )
    ]

    def execute(self, data: Dict[str, Any]) -> float:
        """
        Executes the Gunning Fog Index tool and returns the readability score.
        
        Gunning Fog Index formula:
        0.4 * ((words/sentences) + 100 * (complex words/words))
        
        Parameters:
            data (Dict[str, Any]): The input data containing "input_text".
        
        Returns:
            float: The Gunning Fog Index readability score.

        Raises:
            ValueError: If the input data is invalid.
        """
        if self.validate_input(data):
            text = data['input_text']
            num_sentences = self.count_sentences(text)
            num_words = self.count_words(text)
            num_complex_words = self.count_complex_words(text)
            if num_sentences == 0 or num_words == 0:
                return 0.0
            words_per_sentence = num_words / num_sentences
            percent_complex_words = (num_complex_words / num_words) * 100
            gunning_fog_index = 0.4 * (words_per_sentence + percent_complex_words)
            return gunning_fog_index
        else:
            raise ValueError("Invalid input for GunningFogIndexTool.")

    def __call__(self, input_text: str) -> float:
        """
        Calls the execute method to calculate the Gunning Fog Index for the given input text.
        
        Parameters:
            input_text (str): The input text.
        
        Returns:
            float: The Gunning Fog Index readability score.
        
        Raises:
            ValueError: If the input text is invalid.
        """
        return self.execute({"input_text": input_text}) # 🚧 Can we simplify this and pass the data input_text directly as str?

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

    def count_complex_words(self, text: str) -> int:
        """
        Counts the number of complex words (three or more syllables) in the text.
        
        Parameters:
            text (str): The input text.
        
        Returns:
            int: The number of complex words in the text.
        """
        words = re.findall(r'\b\w+\b', text)
        complex_word_count = 0
        for word in words:
            if self.count_syllables_in_word(word) >= 3:
                complex_word_count += 1
        return complex_word_count

    def count_syllables_in_word(self, word: str) -> int:
        """
        Counts the number of syllables in a single word.
        
        Parameters:
            word (str): The input word.
        
        Returns:
            int: The number of syllables in the word.
        """
        word = word.lower()
        vowels = "aeiou"
        syllables = 0
        if len(word) == 0:
            return syllables
        if word[0] in vowels:
            syllables += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                syllables += 1
        return syllables if syllables > 0 else 1  # At least one syllable per word