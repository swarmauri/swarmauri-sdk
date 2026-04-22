"""Evidence, quorum, and certification-state operators."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import TypeVar

Voter = TypeVar("Voter", bound=Hashable)
Claim = TypeVar("Claim", bound=Hashable)


@dataclass(frozen=True, slots=True)
class QuorumState:
    voters: frozenset[Hashable]

    def reached(self, k: int) -> bool:
        if k <= 0:
            raise ValueError("k must be positive")
        return len(self.voters) >= k


def quorum_merge(a: QuorumState, b: QuorumState) -> QuorumState:
    return QuorumState(a.voters | b.voters)


@dataclass(frozen=True, slots=True)
class WeightedEvidence:
    weights: Mapping[Hashable, float]

    def __post_init__(self) -> None:
        if any(value < 0 for value in self.weights.values()):
            raise ValueError("weights must be non-negative")

    @property
    def total(self) -> float:
        return sum(self.weights.values())

    def reached(self, threshold: float) -> bool:
        return self.total >= threshold


def weighted_evidence_merge(a: WeightedEvidence, b: WeightedEvidence) -> WeightedEvidence:
    """Merge voter weights by pointwise max, preventing duplicate inflation."""

    keys = a.weights.keys() | b.weights.keys()
    return WeightedEvidence({key: max(a.weights.get(key, 0.0), b.weights.get(key, 0.0)) for key in keys})


@dataclass(frozen=True, slots=True)
class ClaimEvidence:
    """Claim-indexed supporting voters."""

    support: Mapping[Hashable, frozenset[Hashable]]


def claim_evidence_merge(a: ClaimEvidence, b: ClaimEvidence) -> ClaimEvidence:
    keys = a.support.keys() | b.support.keys()
    return ClaimEvidence(
        {key: a.support.get(key, frozenset()) | b.support.get(key, frozenset()) for key in keys}
    )


def certified_claims(state: ClaimEvidence, quorum: int) -> frozenset[Hashable]:
    if quorum <= 0:
        raise ValueError("quorum must be positive")
    return frozenset(claim for claim, voters in state.support.items() if len(voters) >= quorum)


@dataclass(frozen=True, slots=True)
class ScoreCard:
    scores: Mapping[Hashable, float]
    cap: float = float("inf")

    def __post_init__(self) -> None:
        if self.cap < 0 or any(value < 0 for value in self.scores.values()):
            raise ValueError("scores and cap must be non-negative")


def scorecard_merge(a: ScoreCard, b: ScoreCard) -> ScoreCard:
    """Feature-wise saturating score accumulation."""

    if a.cap != b.cap:
        raise ValueError("scorecards must use the same cap")
    keys = a.scores.keys() | b.scores.keys()
    return ScoreCard(
        {key: min(a.cap, a.scores.get(key, 0.0) + b.scores.get(key, 0.0)) for key in keys},
        a.cap,
    )


def thresholded_features(card: ScoreCard, threshold: float) -> frozenset[Hashable]:
    return frozenset(key for key, value in card.scores.items() if value >= threshold)


def support_ratio(state: ClaimEvidence, claim: Hashable, universe_size: int) -> float:
    if universe_size <= 0:
        raise ValueError("universe_size must be positive")
    return len(state.support.get(claim, frozenset())) / universe_size
