from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import List
from swarmauri_base.ComponentBase import ComponentBase

from peagen.evo_db import EvoDB, Program


class ISelectorBase(ABC):
    """Strategy object that picks parent programs from :class:`EvoDB`."""

    @abstractmethod
    def select(self, db: EvoDB) -> Program:
        """Return one parent program from the archive."""

    @abstractmethod
    def sample_inspirations(self, db: EvoDB, k: int) -> List[str]:
        """Return ``k`` source snippets used for prompt inspiration."""

    @abstractmethod
    def feedback(self, fitness_gain: float) -> None:
        """Update internal state given the last generation's fitness gain."""

class SelectorBase(ISelectorBase, ComponentBase):

    def select(self, db: EvoDB) -> Program:
        """Return one parent program from the archive."""
        raise NotImplementedError

    def sample_inspirations(self, db: EvoDB, k: int) -> List[str]:
        """Return ``k`` source snippets used for prompt inspiration."""
        raise NotImplementedError


    def feedback(self, fitness_gain: float) -> None:
        """Update internal state given the last generation's fitness gain."""
        raise NotImplementedError

class AdaptiveEpsilonSelector(SelectorBase):
    """Adaptive ε-greedy selector used by default."""

    def __init__(self, eps_init: float = 0.15, decay: float = 0.96, floor: float = 0.02) -> None:
        self.eps = eps_init
        self.decay = decay
        self.floor = floor

    # ------------------------------------------------------------------ API
    def select(self, db: EvoDB) -> Program:
        islands = list(db.grid.values())
        if not islands:
            raise ValueError("EvoDB is empty")
        if random.random() < self.eps:
            return random.choice(islands).champ
        return min((isl.champ for isl in islands), key=lambda p: p.speed_ms)

    def sample_inspirations(self, db: EvoDB, k: int) -> List[str]:
        islands = list(db.grid.values())
        srcs = [isl.champ.src for isl in islands]
        if k >= len(srcs):
            return srcs
        return random.sample(srcs, k)

    def feedback(self, fitness_gain: float) -> None:
        if fitness_gain > 0:
            self.eps = max(self.floor, self.eps * self.decay)
        else:
            self.eps = min(0.5, self.eps * 1.05)
