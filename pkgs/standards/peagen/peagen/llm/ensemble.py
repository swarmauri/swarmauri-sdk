from __future__ import annotations

import random
import time
from importlib.metadata import entry_points
from typing import Dict, Any

from peagen.cli_common import load_peagen_toml


class LLMEnsemble:
    _backends: Dict[str, type] = {}
    _metrics_tokens: Dict[str, int] = {}
    _metrics_latency: list[float] = []

    @classmethod
    def _discover(cls) -> None:
        if cls._backends:
            return
        for ep in entry_points(group="peagen.llm_backends"):
            cls._backends[ep.name] = ep.load()
            cls._metrics_tokens.setdefault(ep.name, 0)

    @classmethod
    def _choose_backend(cls, name: str) -> str:
        if name != "auto":
            return name
        cfg = load_peagen_toml()
        weights = cfg.get("llm", {}).get("backend_weights", {})
        backends = list(cls._backends)
        probs = [weights.get(b, 1) for b in backends]
        return random.choices(backends, weights=probs, k=1)[0]

    @classmethod
    def generate(
        cls,
        prompt: str,
        backend: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        cls._discover()
        bname = cls._choose_backend(backend)
        backend_cls = cls._backends[bname]
        start = time.time()
        result = backend_cls().generate(prompt, temperature=temperature, max_tokens=max_tokens)
        latency = time.time() - start
        cls._metrics_latency.append(latency)
        cls._metrics_tokens[bname] += len(result.split())
        return result
