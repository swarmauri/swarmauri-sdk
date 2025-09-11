import re
import string
from typing import Any, Dict, Literal, Tuple

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_standard.programs.Program import Program


@ComponentBase.register_type(EvaluatorBase, "FleschKincaidGradeEvaluator")
class FleschKincaidGradeEvaluator(EvaluatorBase, ComponentBase):
    """
    Evaluator that computes the Flesch-Kincaid Grade Level of text.

    This evaluator analyzes text to determine its readability according to the
    Flesch-Kincaid Grade Level formula, which estimates the U.S. grade level
    required to understand the text. The formula considers average sentence length
    and average syllables per word.

    Formula: FKGL = 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59

    Attributes:
        type: The type identifier for this evaluator
    """

    type: Literal["FleschKincaidGradeEvaluator"] = "FleschKincaidGradeEvaluator"

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
        Compute the Flesch-Kincaid Grade Level score for a program's text output.

        This method analyzes the text produced by a program, counting sentences,
        words, and syllables to calculate the FKGL score.

        Args:
            program: The program whose output text will be evaluated
            **kwargs: Additional parameters (unused in this implementation)

        Returns:
            A tuple containing:
                - float: The Flesch-Kincaid Grade Level score
                - Dict[str, Any]: Metadata including sentence count, word count,
                                 syllable count, and the breakdown of the calculation

        Raises:
            ValueError: If the program has no text output or if text analysis fails
        """
        # Get the text from the program's output
        text = self._get_program_text(program)

        if not text:
            if self.logger:
                self.logger.warning("No text found in program output")
            return 0.0, {"error": "No text to evaluate"}

        # Count sentences, words, and syllables
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        syllables = self._count_syllables(text)

        if self.logger:
            self.logger.debug(
                f"Text analysis: {sentences} sentences, {words} words, {syllables} syllables"
            )

        # Calculate the Flesch-Kincaid Grade Level
        if sentences == 0 or words == 0:
            if self.logger:
                self.logger.warning(
                    "Text lacks sufficient content for FKGL calculation"
                )
            return 0.0, {
                "error": "Text lacks sufficient content for analysis",
                "sentences": sentences,
                "words": words,
                "syllables": syllables,
            }

        # Calculate average sentence length and average syllables per word
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words

        # Apply the FKGL formula: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
        fkgl_score = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59

        # Ensure the score is not negative (which would be meaningless for grade levels)
        fkgl_score = float(max(0, fkgl_score))

        # Prepare detailed metadata
        metadata = {
            "sentences": sentences,
            "words": words,
            "syllables": syllables,
            "avg_sentence_length": avg_sentence_length,
            "avg_syllables_per_word": avg_syllables_per_word,
            "formula": "0.39*(words/sentences) + 11.8*(syllables/words) - 15.59",
            "formula_calculation": {
                "term1": 0.39 * avg_sentence_length,
                "term2": 11.8 * avg_syllables_per_word,
                "constant": -15.59,
            },
        }

        if self.logger:
            self.logger.info(f"Calculated FKGL score: {fkgl_score:.2f}")
        return fkgl_score, metadata

    def _get_program_text(self, program: Program) -> str:
        """
        Extract text content from a program's output.

        Args:
            program: The program to extract text from

        Returns:
            The extracted text as a string
        """
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

        This method uses regex to split text by common sentence terminators
        (periods, question marks, exclamation points) followed by spaces or
        end of text.

        Args:
            text: The text to analyze

        Returns:
            The number of sentences detected
        """
        # Split by common sentence terminators followed by space or end of text
        sentences = re.split(r"[.!?]+[\s$]", text)

        # Filter out empty strings
        sentences = [s for s in sentences if s.strip()]

        # If no sentences were found but there's text, count it as one sentence
        if not sentences and text.strip():
            return 1

        return len(sentences)

    def _count_words(self, text: str) -> int:
        """
        Count the number of words in the text.

        Words are defined as sequences of characters separated by whitespace,
        after removing punctuation.

        Args:
            text: The text to analyze

        Returns:
            The number of words detected
        """
        # Remove punctuation and split by whitespace
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)
        words = text.split()

        return len(words)

    def _count_syllables(self, text: str) -> int:
        """
        Count the total number of syllables in the text.

        This method uses a heuristic approach to estimate syllables based on
        vowel sequences and common English syllable patterns.

        Args:
            text: The text to analyze

        Returns:
            The estimated total number of syllables
        """
        # Remove punctuation and convert to lowercase
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator).lower()

        # Split into words
        words = text.split()

        total_syllables = 0
        for word in words:
            syllable_count = self._count_word_syllables(word)
            total_syllables += syllable_count

        return total_syllables

    def _count_word_syllables(self, word: str) -> int:
        """
        Count the number of syllables in a single word.

        This uses a combination of rules to estimate syllable count:
        1. Count groups of vowels (a, e, i, o, u, y) as potential syllables
        2. Apply adjustments for common patterns like silent 'e' at end of words
        3. Ensure every word has at least one syllable

        Args:
            word: The word to analyze

        Returns:
            The estimated number of syllables in the word
        """
        # Convert to lowercase
        word = word.lower()

        # Handle special cases
        if not word:
            return 0

        # Count of syllables
        count = 0

        # Define vowels
        vowels = "aeiouy"

        # Flag to track if previous character was a vowel
        prev_is_vowel = False

        # Process each character
        for i, char in enumerate(word):
            is_vowel = char in vowels

            # Count syllable when we find a vowel that doesn't immediately follow another vowel
            if is_vowel and not prev_is_vowel:
                count += 1

            # Update previous character status
            prev_is_vowel = is_vowel

        # Adjust for common patterns

        # Silent 'e' at the end of words
        if word.endswith("e") and len(word) > 2 and word[-2] not in vowels:
            count = max(1, count - 1)  # Reduce count but ensure at least 1 syllable

        # Words ending in 'le' where the 'l' follows a consonant
        if len(word) > 2 and word.endswith("le") and word[-3] not in vowels:
            count = max(1, count)  # Ensure proper counting for words like "simple"

        # Words ending in 'ed' often have a silent 'e'
        if word.endswith("ed") and len(word) > 2 and word[-3] not in vowels:
            count = max(1, count - 1)

        # Ensure every word has at least one syllable
        return max(1, count)
