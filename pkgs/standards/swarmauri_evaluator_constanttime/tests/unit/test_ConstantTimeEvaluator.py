import os
import random
import tempfile
import time
from unittest.mock import MagicMock

import pytest

from swarmauri_evaluator_constanttime import ConstantTimeEvaluator
from swarmauri_core.programs.IProgram import IProgram


@pytest.mark.unit
def test_ubc_resource() -> None:
    assert ConstantTimeEvaluator().resource == "Evaluator"


@pytest.mark.unit
def test_ubc_type() -> None:
    assert ConstantTimeEvaluator().type == "ConstantTimeEvaluator"


@pytest.mark.unit
def test_initialization() -> None:
    assert isinstance(ConstantTimeEvaluator().id, str)


@pytest.mark.unit
def test_serialization() -> None:
    evaluator = ConstantTimeEvaluator()
    assert (
        evaluator.id
        == ConstantTimeEvaluator.model_validate_json(evaluator.model_dump_json()).id
    )


def _leaky_compare(a: bytes, b: bytes) -> bool:
    if a[0] != b[0]:
        time.sleep(0.005)
    return True


def _constant_delay(a: bytes, b: bytes) -> bool:
    for _ in range(100000):
        pass
    return True


def _gen_pair_random_same_len(n: int = 32):
    a = os.urandom(n)
    b = bytearray(a)
    b[0] ^= 0xFF
    return a, bytes(b)


def _fixed_pair(n: int = 32):
    a = b"x" * n
    return a, a


@pytest.fixture
def evaluator():
    return ConstantTimeEvaluator()


@pytest.fixture
def mock_program():
    with tempfile.TemporaryDirectory() as temp_dir:
        program = MagicMock(spec=IProgram)
        program.path = temp_dir
        yield program


@pytest.mark.unit
def test_leaky_function_shows_timing_difference(evaluator, mock_program):
    random.seed(1337)
    score, meta = evaluator.evaluate(
        mock_program,
        fn=_leaky_compare,
        make_input_pair=_gen_pair_random_same_len,
        fixed_pair=_fixed_pair(),
        n_samples=20,
        iters_per=5,
    )
    assert meta["mean_random"] > meta["mean_fixed"]
    assert isinstance(score, float)
    assert {"t_stat", "cliff_delta", "constant_time"} <= meta.keys()


@pytest.mark.unit
def test_constant_function_has_similar_means(evaluator, mock_program):
    random.seed(1337)
    score, meta = evaluator.evaluate(
        mock_program,
        fn=_constant_delay,
        make_input_pair=_gen_pair_random_same_len,
        fixed_pair=_fixed_pair(),
        n_samples=20,
        iters_per=5,
    )
    diff = abs(meta["mean_fixed"] - meta["mean_random"])
    assert diff < 0.5 * meta["mean_fixed"]
    assert isinstance(score, float)
    assert {"t_stat", "cliff_delta", "constant_time"} <= meta.keys()
