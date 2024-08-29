import re
from typing import Any, Dict, Literal
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class FleschKincaid(ToolBase):
    """
    A tool for calculating the Flesch-Kincaid readability score.
    """
    version: str = "0.1.dev1"
    name: str = "FleschKincaidTool"
    type: Literal["FleschKincaidTool"] = "FleschKincaidTool"
    description: str = "Calculates the FleschKincard score for a given text."

    def execute(self, data: Dict[str, Any]) -> float:
        """
        Executes the Flesch-Kincaid tool and returns the readability score.
        
        Flesch-Kincaid formula:
        206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        
        Arguments:
        - data (Dict[str, Any]): The input data containing "input_text".
        
        Returns:
        - float: The Flesch-Kincaid readability score.
        """
        if self.validate_input(data):
            text = data['input_text']
            num_sentences = self.count_sentences(text)
            num_words = self.count_words(text)
            num_syllables = self.count_syllables(text)
            if num_sentences == 0 or num_words == 0:
                return 0.0
            words_per_sentence = num_words / num_sentences
            syllables_per_word = num_syllables / num_words
            flesch_kincaid_score = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
            return flesch_kincaid_score
        else:
            raise ValueError("Invalid input for FleschKincaidTool.")

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

    def count_syllables(self, text: str) -> int:
        """
        Counts the number of syllables in the text.
        """
        words = re.findall(r'\b\w+\b', text)
        syllable_count = 0
        for word in words:
            syllable_count += self.count_syllables_in_word(word)
        return syllable_count

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

