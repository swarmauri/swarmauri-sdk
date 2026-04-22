import math
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Tuple


DEFAULT_FIELD_WEIGHTS: Dict[str, float] = {
    "file_name": 5.0,
    "relative_path": 4.0,
    "directory_path": 2.5,
    "file_extension": 1.5,
    "chunk_identity": 1.0,
    "content": 1.0,
}


class BM25FScorer:
    def __init__(
        self,
        field_weights: Dict[str, float] | None = None,
        k1: float = 1.2,
        b: float = 0.75,
    ) -> None:
        self.field_weights = dict(field_weights or DEFAULT_FIELD_WEIGHTS)
        self.k1 = k1
        self.b = b
        self.document_fields: List[Dict[str, str]] = []
        self._field_term_frequencies: List[Dict[str, Counter[str]]] = []
        self._field_lengths: List[Dict[str, int]] = []
        self._average_field_lengths: Dict[str, float] = {}
        self._document_frequencies: Counter[str] = Counter()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        tokens: List[str] = []
        for raw_token in re.findall(r"[A-Za-z0-9_]+", text.replace("\\", "/")):
            token = raw_token.lower()
            if token:
                tokens.append(token)
            parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|[0-9]+", raw_token.replace("_", " "))
            for part in parts:
                lowered = part.lower()
                if lowered and lowered != token:
                    tokens.append(lowered)
        return tokens

    def fit(self, document_fields: Iterable[Dict[str, str]]) -> None:
        self.document_fields = [dict(fields) for fields in document_fields]
        self._field_term_frequencies = []
        self._field_lengths = []
        self._average_field_lengths = {}
        self._document_frequencies = Counter()

        field_length_totals: Dict[str, int] = defaultdict(int)
        for fields in self.document_fields:
            doc_frequencies: Dict[str, Counter[str]] = {}
            doc_lengths: Dict[str, int] = {}
            doc_terms = set()
            for field_name in self.field_weights:
                tokens = self.tokenize(fields.get(field_name, ""))
                frequencies = Counter(tokens)
                doc_frequencies[field_name] = frequencies
                doc_lengths[field_name] = len(tokens)
                field_length_totals[field_name] += len(tokens)
                doc_terms.update(frequencies)
            self._field_term_frequencies.append(doc_frequencies)
            self._field_lengths.append(doc_lengths)
            for term in doc_terms:
                self._document_frequencies[term] += 1

        doc_count = max(1, len(self.document_fields))
        self._average_field_lengths = {
            field_name: field_length_totals[field_name] / doc_count
            for field_name in self.field_weights
        }

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        query_terms = self.tokenize(query)
        if not query_terms or not self.document_fields:
            return []

        scores = [
            (index, self._score_document(index, query_terms))
            for index in range(len(self.document_fields))
        ]
        matches = [(index, score) for index, score in scores if score > 0.0]
        matches.sort(key=lambda item: item[1], reverse=True)
        return matches[:top_k]

    def _score_document(self, document_index: int, query_terms: List[str]) -> float:
        score = 0.0
        for term in query_terms:
            document_frequency = self._document_frequencies.get(term, 0)
            if document_frequency == 0:
                continue
            weighted_frequency = self._weighted_term_frequency(document_index, term)
            if weighted_frequency <= 0:
                continue
            score += self._idf(document_frequency) * (
                (weighted_frequency * (self.k1 + 1.0))
                / (self.k1 + weighted_frequency)
            )
        return score

    def _weighted_term_frequency(self, document_index: int, term: str) -> float:
        weighted_frequency = 0.0
        for field_name, weight in self.field_weights.items():
            field_frequency = self._field_term_frequencies[document_index][
                field_name
            ].get(term, 0)
            if field_frequency == 0:
                continue
            field_length = self._field_lengths[document_index].get(field_name, 0)
            average_length = self._average_field_lengths.get(field_name, 1.0) or 1.0
            normalized_length = 1.0 - self.b + self.b * (field_length / average_length)
            weighted_frequency += weight * (field_frequency / normalized_length)
        return weighted_frequency

    def _idf(self, document_frequency: int) -> float:
        doc_count = len(self.document_fields)
        return math.log(1.0 + ((doc_count - document_frequency + 0.5) / (document_frequency + 0.5)))

    def to_dict(self) -> Dict:
        return {
            "field_weights": self.field_weights,
            "k1": self.k1,
            "b": self.b,
            "document_fields": self.document_fields,
        }

    @classmethod
    def from_dict(cls, payload: Dict) -> "BM25FScorer":
        scorer = cls(
            field_weights=payload.get("field_weights"),
            k1=payload.get("k1", 1.2),
            b=payload.get("b", 0.75),
        )
        scorer.fit(payload.get("document_fields", []))
        return scorer
