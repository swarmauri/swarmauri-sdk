"""Evaluator that checks for constant-time behavior."""

from __future__ import annotations

import gc
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, List, Literal, Sequence, Tuple

from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_core.programs.IProgram import IProgram as Program


@dataclass
class TvlaResult:
    t_stat: float
    df: float
    mean_fixed: float
    mean_random: float
    n_fixed: int
    n_random: int


@dataclass
class CliffResult:
    delta: float


def welchs_t(fixed: Sequence[float], rnd: Sequence[float]) -> TvlaResult:
    n1 = len(fixed)
    n2 = len(rnd)
    m1 = sum(fixed) / n1 if n1 else 0.0
    m2 = sum(rnd) / n2 if n2 else 0.0
    v1 = (sum((x - m1) ** 2 for x in fixed) / n1) if n1 else 0.0
    v2 = (sum((x - m2) ** 2 for x in rnd) / n2) if n2 else 0.0
    num = m1 - m2
    den = ((v1 / n1) + (v2 / n2)) ** 0.5 if n1 and n2 else float("inf")
    t = num / den if den else float("inf")
    df_num = (v1 / n1 + v2 / n2) ** 2
    df_den = (v1**2 / (n1**2 * (n1 - 1) if n1 > 1 else float("inf"))) + (
        v2**2 / (n2**2 * (n2 - 1) if n2 > 1 else float("inf"))
    )
    df = df_num / df_den if df_den else float("inf")
    return TvlaResult(
        t_stat=t, df=df, mean_fixed=m1, mean_random=m2, n_fixed=n1, n_random=n2
    )


def cliffs_delta(a: Sequence[float], b: Sequence[float]) -> CliffResult:
    gt = lt = 0
    for x in a:
        for y in b:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    denom = len(a) * len(b)
    delta = (gt - lt) / denom if denom else 0.0
    return CliffResult(delta=delta)


def _prepare_env():
    gc.disable()
    try:
        if hasattr(os, "sched_setaffinity"):
            cpus = os.sched_getaffinity(0)
            if len(cpus) > 1:
                one = {sorted(list(cpus))[0]}
                os.sched_setaffinity(0, one)
    except Exception:  # pragma: no cover
        pass
    _busywait(50_000)


def _restore_env():
    gc.enable()


def _busywait(iters: int):
    x = 0
    for _ in range(iters):
        x ^= 1
    return x


def _now_ns() -> int:
    return time.perf_counter_ns()


def measure_timings(
    fn: Callable[..., Any],
    inputs: Sequence[Tuple[tuple, dict]],
    *,
    iters_per_input: int = 50,
    rounds: int = 1,
    shuffle_each_round: bool = True,
) -> List[float]:
    timings: List[float] = []
    _prepare_env()
    try:
        for _ in range(10_000):
            _busywait(10)
        for _ in range(rounds):
            seq = list(inputs)
            if shuffle_each_round:
                random.shuffle(seq)
            for args, kwargs in seq:
                for _ in range(iters_per_input):
                    t0 = _now_ns()
                    fn(*args, **kwargs)
                    t1 = _now_ns()
                    timings.append(t1 - t0)
    finally:
        _restore_env()
    return timings


def _mk_inputs_fixed_vs_random(
    make_input_pair: Callable[[], Tuple[bytes, bytes]],
    fixed_pair: Tuple[bytes, bytes],
    n_samples: int,
) -> Tuple[List[Tuple[tuple, dict]], List[Tuple[tuple, dict]]]:
    fixed_inputs = [((fixed_pair[0], fixed_pair[1]), {}) for _ in range(n_samples)]
    random_inputs = [make_input_pair() for _ in range(n_samples)]
    rnd_inputs = [((a, b), {}) for (a, b) in random_inputs]
    return fixed_inputs, rnd_inputs


class ConstantTimeEvaluator(EvaluatorBase):
    """Check whether a function exhibits constant-time behavior."""

    type: Literal["ConstantTimeEvaluator"] = "ConstantTimeEvaluator"

    TVLA_T_THRESHOLD: ClassVar[float] = 4.5
    CLIFF_ALERT: ClassVar[float] = 0.147

    def _compute_score(
        self,
        program: Program,
        *,
        fn: Callable[[bytes, bytes], Any],
        make_input_pair: Callable[[], Tuple[bytes, bytes]],
        fixed_pair: Tuple[bytes, bytes],
        n_samples: int = 50,
        iters_per: int = 20,
    ) -> Tuple[float, Dict[str, Any]]:
        fixed_inputs, rnd_inputs = _mk_inputs_fixed_vs_random(
            make_input_pair, fixed_pair, n_samples
        )
        t_fixed = measure_timings(fn, fixed_inputs, iters_per_input=iters_per)
        t_random = measure_timings(fn, rnd_inputs, iters_per_input=iters_per)
        tvla = welchs_t(t_fixed, t_random)
        cliff = cliffs_delta(t_fixed, t_random)
        constant_time = (
            abs(tvla.t_stat) <= self.TVLA_T_THRESHOLD
            and abs(cliff.delta) <= self.CLIFF_ALERT
        )
        score = 1.0 if constant_time else 0.0
        metadata: Dict[str, Any] = {
            "t_stat": tvla.t_stat,
            "cliff_delta": cliff.delta,
            "mean_fixed": tvla.mean_fixed,
            "mean_random": tvla.mean_random,
            "n_fixed": tvla.n_fixed,
            "n_random": tvla.n_random,
            "constant_time": constant_time,
        }
        return score, metadata
