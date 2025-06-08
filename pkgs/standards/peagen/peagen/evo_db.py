from __future__ import annotations

import json
import random
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Tuple

Bucket = Tuple[int, int, int, int]


@dataclass
class Program:
    src: str
    gen: int
    speed_ms: float
    peak_kb: float
    bucket: Bucket | None = None


@dataclass
class Island:
    champ: Program
    hist: list[Program] = field(default_factory=list)


class EvoDB:
    def __init__(
        self,
        speed_bin_ms: int = 5,
        mem_bin_kb: int = 32,
        size_bin_ch: int = 40,
    ) -> None:
        self.grid: Dict[Bucket, Island] = {}
        self.speed_bin = speed_bin_ms
        self.mem_bin = mem_bin_kb
        self.size_bin = size_bin_ch

    # ------------------------------------------------------------------ helpers
    def _bucket(self, p: Program) -> Bucket:
        return (
            int(p.speed_ms // self.speed_bin),
            int(p.peak_kb // self.mem_bin),
            int(len(p.src) // self.size_bin),
            p.gen % 6,
        )

    # ------------------------------------------------------------------ API
    def insert(self, p: Program) -> None:
        b = self._bucket(p)
        p.bucket = b
        isl = self.grid.get(b)
        if isl is None:
            isl = Island(champ=p)
            self.grid[b] = isl
        if p.speed_ms < isl.champ.speed_ms:
            isl.champ = p
        isl.hist.append(p)

    def sample(self) -> Island:
        if not self.grid:
            raise ValueError("EvoDB empty")
        return random.choice(list(self.grid.values()))

    def save_checkpoint(self, path: str | Path = "evo_checkpoint.msgpack") -> None:
        data = {str(b): {"champ": asdict(i.champ), "hist": [asdict(p) for p in i.hist]} for b, i in self.grid.items()}
        Path(path).write_bytes(json.dumps(data).encode("utf-8"))
