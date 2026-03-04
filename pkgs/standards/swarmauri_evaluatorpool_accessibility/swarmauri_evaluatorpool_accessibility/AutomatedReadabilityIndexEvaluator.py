# File: peagen/evaluators/AutomatedReadabilityIndexEvaluator.py

import os
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

        text = self._extract_text_from_program(program)

        if not text.strip():
            return 0.0, {"error": "no_text", "chars": 0, "words": 0, "sentences": 0}

        chars = len(text)
        words_list = self._count_words(text)
        sentences_list = self._count_sentences(text)
        words = len(words_list)
        sents = len(sentences_list)

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
    def _extract_text_from_program(self, program: Program) -> str:
        """
        Extract text from a program's artifacts or source-files.
        """
        if hasattr(program, "get_artifacts"):
            segments: List[str] = []
            for artifact in program.get_artifacts() or []:
                path = artifact.get_path()
                if not os.path.exists(path):
                    continue
                ext = Path(path).suffix.lower()
                try:
                    with open(path, encoding="utf-8") as f:
                        raw = f.read()
                    if ext in (".md", ".markdown"):
                        html = markdown.markdown(raw)
                        segments.append(BeautifulSoup(html, "html.parser").get_text())
                    elif ext in (".html", ".htm"):
                        segments.append(BeautifulSoup(raw, "html.parser").get_text())
                    else:
                        segments.append(raw)
                except Exception as exc:
                    if self.logger:
                        self.logger.error("Error parsing %s: %s", path, exc)
            return " ".join(segments)

        files = (
            program.get_source_files()
            if hasattr(program, "get_source_files")
            else getattr(program, "content", {})
        )
        segments: List[str] = []
        for rel_path, data in files.items():
            if not isinstance(data, str):
                continue
            ext = Path(rel_path).suffix.lower()
            try:
                if ext in (".md", ".markdown"):
                    html = markdown.markdown(data)
                    segments.append(BeautifulSoup(html, "html.parser").get_text())
                elif ext in (".html", ".htm"):
                    segments.append(BeautifulSoup(data, "html.parser").get_text())
                else:
                    segments.append(data)
            except Exception as exc:
                if self.logger:
                    self.logger.error("Error parsing %s: %s", rel_path, exc)
        return " ".join(segments)

    @staticmethod
    def _count_words(text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    @staticmethod
    def _count_sentences(text: str) -> List[str]:
        if not text.strip():
            return []
        sents = re.split(r"(?<=[.!?])\s+", text)
        filtered = [s for s in sents if s.strip()]
        return filtered if filtered else [text.strip()]
