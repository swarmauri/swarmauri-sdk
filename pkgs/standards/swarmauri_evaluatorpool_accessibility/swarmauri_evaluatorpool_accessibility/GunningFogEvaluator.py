import re
import string
from typing import Any, Dict, Literal, Tuple

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_standard.programs.Program import Program


@ComponentBase.register_type(EvaluatorBase, "GunningFogEvaluator")
class GunningFogEvaluator(EvaluatorBase, ComponentBase):
    """
    Evaluator that computes the Gunning Fog Index (GFI) for text readability.

    The Gunning Fog Index estimates the years of formal education needed to
    understand text on a first reading. Higher scores indicate more complex text.
    The formula is: 0.4 * ((words/sentences) + 100 * (complex_words/words))

    A complex word is defined as having three or more syllables.

    Attributes:
        type: The literal type identifier for this evaluator
    """

    type: Literal["GunningFogEvaluator"] = "GunningFogEvaluator"

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def evaluate(self, program: Program, **kwargs) -> Dict[str, Any]:
        """Return ``{"score": float, "metadata": dict}`` for the given program."""
        score, meta = self._compute_score(program, **kwargs)
        return {"score": score, "metadata": meta}

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute the Gunning Fog Index for the program's text.

        Args:
            program: The program containing text to evaluate
            **kwargs: Additional parameters (unused)

        Returns:
            A tuple containing:
                - float: The Gunning Fog Index score (lower is better for readability)
                - Dict[str, Any]: Metadata including sentence count, word count, and complex word count
        """
        text = self._get_program_text(program)
        if not text or not isinstance(text, str):
            if self.logger:
                self.logger.warning("Program text is empty or not a string")
            return 0.0, {"error": "No valid text to analyze"}

        # Count sentences, words, and complex words
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        complex_words = self._count_complex_words(text)

        # Avoid division by zero
        if sentences == 0 or words == 0:
            if self.logger:
                self.logger.warning("Text has no sentences or words")
            return 0.0, {
                "sentences": sentences,
                "words": words,
                "complex_words": complex_words,
                "error": "Text has no sentences or words",
            }

        # Calculate Gunning Fog Index
        avg_sentence_length = words / sentences
        percent_complex_words = 100 * (complex_words / words)
        gunning_fog_index = 0.4 * (avg_sentence_length + percent_complex_words)

        # Higher score means more complex text, so we invert it for fitness
        # (assuming lower complexity is better for accessibility)
        # We cap at 20 as most fog index scores fall between 6-17
        capped_score = min(gunning_fog_index, 20)
        normalized_score = 1.0 - (capped_score / 20.0)

        metadata = {
            "gunning_fog_index": gunning_fog_index,
            "sentences": sentences,
            "words": words,
            "complex_words": complex_words,
            "avg_sentence_length": avg_sentence_length,
            "percent_complex_words": percent_complex_words,
        }

        if self.logger:
            self.logger.debug(f"Computed Gunning Fog Index: {gunning_fog_index:.2f}")
        return normalized_score, metadata

    def _get_program_text(self, program: Program) -> str:
        """Return a concatenated text representation of the program."""
        try:
            source_files = program.get_source_files()
            if isinstance(source_files, dict):
                return " \n".join(str(v) for v in source_files.values())
        except Exception as exc:
            if self.logger:
                self.logger.debug(f"Failed to obtain program text: {exc}")
        return ""

    def _count_sentences(self, text: str) -> int:
        """
        Count the number of sentences in the text.

        Args:
            text: The text to analyze

        Returns:
            int: The number of sentences
        """
        # Simple sentence detection based on common sentence terminators
        # This is a simplified approach; more sophisticated NLP could be used
        sentence_terminators = re.compile(r"[.!?]+")
        sentences = sentence_terminators.split(text)
        # Filter out empty strings that might result from multiple terminators
        sentences = [s for s in sentences if s.strip()]
        return len(sentences)

    def _count_words(self, text: str) -> int:
        """
        Count the number of words in the text.

        Args:
            text: The text to analyze

        Returns:
            int: The number of words
        """
        # Remove punctuation and split by whitespace
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)
        words = [word for word in text.split() if word]
        return len(words)

    def _count_complex_words(self, text: str) -> int:
        """
        Count the number of complex words (3+ syllables) in the text.

        Args:
            text: The text to analyze

        Returns:
            int: The number of complex words
        """
        # Remove punctuation and split by whitespace
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)
        words = text.split()

        complex_word_count = 0
        for word in words:
            if self._count_syllables(word) >= 3:
                complex_word_count += 1

        return complex_word_count

    def _count_syllables(self, word: str) -> int:
        """
        Count the number of syllables in a word.

        This is a heuristic approach that counts vowel groups.
        It handles common patterns but isn't perfect for all words.

        Args:
            word: The word to analyze

        Returns:
            int: The estimated number of syllables
        """
        word = word.lower()

        # Remove common suffix patterns that don't add syllables
        if word.endswith("es") or word.endswith("ed"):
            word = word[:-2]
        elif word.endswith("e"):
            word = word[:-1]

        # Count vowel groups (consecutive vowels count as one syllable)
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        # Every word has at least one syllable
        return max(1, count)
