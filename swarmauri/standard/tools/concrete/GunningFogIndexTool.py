import re
from typing import Any, Dict, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase

class GunningFogIndex(ToolBase):
    """
    A tool for calculating the Gunning Fog Index readability score.
    """
    version: str = "0.1.dev1"
    name: str = "GunningFogIndex"
    type: Literal["GunningFogIndex"] = "GunningFogIndex"
    description: str = "Calculates the GunningFogIndex for a given text."

    def execute(self, data: Dict[str, Any]) -> float:
        """
        Executes the Gunning Fog Index tool and returns the readability score.
        
        Gunning Fog Index formula:
        0.4 * ((words/sentences) + 100 * (complex words/words))
        
        Arguments:
        - data (Dict[str, Any]): The input data containing "input_text".
        
        Returns:
        - float: The Gunning Fog Index readability score.
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
            raise ValueError("Invalid input for GunningFogIndex.")

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validates the input data.
        """
        required_keys = ["input_text"]
        return all(key in data for key in required_keys)

    def count_sentences(self, text: str) -> int:
        """
        Counts the number of sentences in the text.
        """
        sentence_endings = re.compile(r'[.!?]')
        sentences = sentence_endings.split(text)
        return len([s for s in sentences if s.strip()])  # Count non-empty sentences

    def count_words(self, text: str) -> int:
        """
        Counts the number of words in the text.
        """
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def count_complex_words(self, text: str) -> int:
        """
        Counts the number of complex words (three or more syllables) in the text.
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
