![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluator_constanttime/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluator_constanttime" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_constanttime/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_constanttime.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_constanttime/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluator_constanttime" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_constanttime/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluator_constanttime" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_constanttime/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluator_constanttime?label=swarmauri_evaluator_constanttime&color=green" alt="PyPI - swarmauri_evaluator_constanttime"/>
    </a>
</p>

---

# Swarmauri Evaluator Constanttime

Evaluator that detects timing side channels using a fixed-vs-random strategy.
It times a callable with repeated fixed inputs and compares those timings against
randomly generated inputs. Welch's t-test and Cliff's delta are used to decide
whether the observed runtime differences are statistically significant. The
evaluator reports a score of `1.0` for constant-time behaviour and `0.0`
otherwise, together with rich metadata about the underlying measurements.

## Installation

### pip

```bash
pip install swarmauri_evaluator_constanttime
```

### Poetry

```bash
poetry add swarmauri_evaluator_constanttime
```

### uv

```bash
uv venv
source .venv/bin/activate
uv pip install swarmauri_evaluator_constanttime
```

## Usage

The example below evaluates a deliberately leaky string comparison that sleeps
for every matching byte. Fixed inputs run all the way through the comparison and
take measurably longer than random guesses that fail fast, so the evaluator
flags the function as *not* constant time.

```python
import secrets
import time

from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_constanttime import ConstantTimeEvaluator


class DummyProgram(IProgram):
    def diff(self, other: "IProgram"):
        return ()

    def apply_diff(self, diff):
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> "IProgram":
        return DummyProgram()


def insecure_compare(secret: bytes, guess: bytes) -> bool:
    for secret_byte, guess_byte in zip(secret, guess):
        if secret_byte != guess_byte:
            return False
        time.sleep(0.0001)
    return len(secret) == len(guess)


def make_input_pair() -> tuple[bytes, bytes]:
    return secrets.token_bytes(16), secrets.token_bytes(16)


def main() -> None:
    evaluator = ConstantTimeEvaluator()
    score, metadata = evaluator._compute_score(
        program=DummyProgram(),
        fn=insecure_compare,
        make_input_pair=make_input_pair,
        fixed_pair=(b"A" * 16, b"A" * 16),
        n_samples=20,
        iters_per=5,
    )

    print(f"Score: {score:.1f}")
    print(f"Constant time? {metadata['constant_time']}")
    print(f"t-statistic: {metadata['t_stat']:.2f}")
    print(f"Cliff's delta: {metadata['cliff_delta']:.3f}")

    assert metadata["constant_time"] is False


if __name__ == "__main__":
    main()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

