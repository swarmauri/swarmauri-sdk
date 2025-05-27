# File: peagen/evaluators/AutomatedReadabilityIndexEvaluator.py

import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple

import markdown
from bs4 import BeautifulSoup
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_standard.programs.Program import Program


@ComponentBase.register_type(EvaluatorBase, "AutomatedReadabilityIndexEvaluator")
class AutomatedReadabilityIndexEvaluator(EvaluatorBase, ComponentBase):
    """
    Computes the Automated Readability Index (ARI) for a Program’s textual sources.

    Conforms to the IEvaluate interface by returning a dict:
        { "score": <float>, "metadata": <dict> }
    """

    type: Literal["AutomatedReadabilityIndexEvaluator"] = (
        "AutomatedReadabilityIndexEvaluator"
    )
    model_config = {"arbitrary_types_allowed": True, "exclude": {"logger"}}

    # ────────────────────────────────────────────────────────────────────
    # public IEvaluate API
    # ────────────────────────────────────────────────────────────────────
    def evaluate(self, program: Program, **kwargs) -> Dict[str, Any]:  # IEvaluate
        score, meta = self._compute_score(program, **kwargs)
        return {"score": score, "metadata": meta}

    # ────────────────────────────────────────────────────────────────────
    # internals
    # ────────────────────────────────────────────────────────────────────
    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Return (score, metadata) tuple; wrapper packs it into the dict
        expected by EvaluatorPoolBase.
        """

        text = self._collect_text(program)

        if not text.strip():
            return 0.0, {"error": "no_text"}

        chars = len(text)
        words = len(self._tokenize_words(text))
        sents = len(self._tokenize_sentences(text))

        if words == 0 or sents == 0:
            return 0.0, {
                "error": "division_by_zero",
                "chars": chars,
                "words": words,
                "sentences": sents,
            }

        ari = 4.71 * (chars / words) + 0.5 * (words / sents) - 21.43
        ari = max(0.0, ari)

        return ari, {"chars": chars, "words": words, "sentences": sents}

    # -------------------------------------------------------------------
    # helpers
    # -------------------------------------------------------------------
    def _collect_text(self, program: Program) -> str:
        """
        Aggregate plain text from all source files in the program.
        Supports .txt, .md, .html and any text-like files present
        in program.get_source_files() or program.content.
        """
        files = (
            program.get_source_files()
            if hasattr(program, "get_source_files")
            else program.content
        )

        segments: List[str] = []
        for rel_path, data in files.items():
            ext = Path(rel_path).suffix.lower()
            try:
                if ext in (".md", ".markdown"):
                    html = markdown.markdown(data)
                    segments.append(BeautifulSoup(html, "html.parser").get_text())
                elif ext in (".html", ".htm"):
                    segments.append(BeautifulSoup(data, "html.parser").get_text())
                else:  # plain text
                    segments.append(data)
            except Exception as exc:
                if self.logger:
                    self.logger.error("Error parsing %s: %s", rel_path, exc)

        return " ".join(segments)

    @staticmethod
    def _tokenize_words(text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    @staticmethod
    def _tokenize_sentences(text: str) -> List[str]:
        sents = re.split(r"(?<=[.!?])\s+", text)
        return [s for s in sents if s.strip()] or [text.strip()]
