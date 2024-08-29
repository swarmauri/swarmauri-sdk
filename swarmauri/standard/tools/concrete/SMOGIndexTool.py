from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 
import re
import math

class SMOGIndex(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="text",
            type="string",
            description="The text to analyze for SMOG Index",
            required=True
        )
    ])
    name: str = 'SMOGIndex'
    description: str = "Calculates the SMOG Index for the provided text."
    type: Literal['SMOGIndex'] = 'SMOGIndex'

    def __call__(self, text: str) -> float:
        """
        Calculates the SMOG Index for the provided text.
        
        Parameters:
            text (str): The text to analyze.
        
        Returns:
            float: The calculated SMOG Index.
        """
        return self.calculate_smog_index(text)

    def calculate_smog_index(self, text: str) -> float:
        sentences = self.count_sentences(text)
        polysyllables = self.count_polysyllables(text)
        if sentences >= 30:
            smog_index = 1.0430 * math.sqrt(polysyllables * (30 / sentences)) + 3.1291
        else:
            smog_index = 1.0430 * math.sqrt(polysyllables * (30 / sentences)) + 3.1291

        return round(smog_index, 1)

    def count_sentences(self, text: str) -> int:
        sentences = re.split(r'[.?!]', text)
        return len([s for s in sentences if s.strip()])

    def count_polysyllables(self, text: str) -> int:
        words = re.findall(r'\w+', text)
        return len([word for word in words if self.count_syllables(word) >= 3])

    def count_syllables(self, word: str) -> int:
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        if word and word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count = 1
        return count