import re
from typing import Any, Dict, Literal, Tuple

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_standard.programs.Program import Program


@ComponentBase.register_type(EvaluatorBase, "ColemanLiauIndexEvaluator")
class ColemanLiauIndexEvaluator(EvaluatorBase, ComponentBase):
    """
    Coleman–Liau Index evaluator compliant with the Program/Evaluator contracts.

    • ``evaluate()`` returns ``{"score": float, "metadata": dict}``.
    • ``_compute_score()`` returns ``Tuple[float, Dict[str, Any]]`` for internal use.
    """

    type: Literal["ColemanLiauIndexEvaluator"] = "ColemanLiauIndexEvaluator"

    normalize_scores: bool = Field(default=True)
    target_grade_level: int = Field(default=8, ge=1)
    max_grade_level: int = Field(default=16, ge=1)

    # ──────────────────────────────────────────────────────────────────────
    # Public API – called by the pool / runner
    # ──────────────────────────────────────────────────────────────────────
    def evaluate(self, program: Program, **kwargs) -> Dict[str, Any]:
        """Return ``{"score": float, "metadata": dict}`` for the given program."""
        score, meta = self._compute_score(program, **kwargs)
        return {"score": score, "metadata": meta}

    # ──────────────────────────────────────────────────────────────────────
    # Core scoring logic
    # ──────────────────────────────────────────────────────────────────────
    def _compute_score(self, program: Program, **__) -> Tuple[float, Dict[str, Any]]:
        text = self._extract_text(program)

        if not text.strip():
            return 0.0, {
                "error": "Empty text",
                "grade_level": 0,
                "letters": 0,
                "words": 0,
                "sentences": 0,
            }

        letters = self._count_letters(text)
        words = self._count_words(text)
        sentences = self._count_sentences(text)

        if words == 0:
            return 0.0, {
                "error": "No words found",
                "grade_level": 0,
                "letters": letters,
                "words": words,
                "sentences": sentences,
            }

        L = (letters / words) * 100
        S = (sentences / words) * 100
        raw_cli = 0.0588 * L - 0.296 * S - 15.8
        grade_level = max(1, round(raw_cli))

        score = (
            self._normalise(grade_level)
            if self.normalize_scores
            else float(grade_level)
        )

        return score, {
            "grade_level": grade_level,
            "raw_index": raw_cli,
            "letters": letters,
            "words": words,
            "sentences": sentences,
            "letters_per_100_words": L,
            "sentences_per_100_words": S,
            "target_grade_level": self.target_grade_level,
        }

    # ──────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────
    def _extract_text(self, program: Program) -> str:
        for attr in ("output", "source", "content"):
            val = getattr(program, attr, None)
            if isinstance(val, str):
                return val
            if isinstance(val, dict):
                joined = "\n".join(v for v in val.values() if isinstance(v, str))
                if joined.strip():
                    return joined

        if hasattr(program, "get_source_files"):
            files = program.get_source_files()
            if isinstance(files, dict):
                joined = "\n".join(v for v in files.values() if isinstance(v, str))
                if joined.strip():
                    return joined

        return str(program)

    @staticmethod
    def _count_letters(text: str) -> int:
        return sum(1 for ch in text if ch.isalpha())

    @staticmethod
    def _count_words(text: str) -> int:
        return len([w for w in re.split(r"\s+", text) if re.search(r"\w", w)])

    @staticmethod
    def _count_sentences(text: str) -> int:
        hits = re.findall(r"[.!?]+", text)
        return len(hits) if hits else 1

    def _normalise(self, grade_level: int) -> float:
        if grade_level == self.target_grade_level:
            return 1.0
        if grade_level <= 1 or grade_level >= self.max_grade_level:
            return 0.0

        distance = abs(grade_level - self.target_grade_level)
        max_distance = max(
            abs(self.target_grade_level - 1),
            abs(self.target_grade_level - self.max_grade_level),
        )
        return max(0.0, 1.0 - distance / max_distance)
