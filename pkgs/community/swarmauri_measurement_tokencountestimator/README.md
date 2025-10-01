![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_measurement_tokencountestimator" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_tokencountestimator/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_tokencountestimator.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_measurement_tokencountestimator" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/pypi/l/swarmauri_measurement_tokencountestimator" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/pypi/v/swarmauri_measurement_tokencountestimator?label=swarmauri_measurement_tokencountestimator&color=green" alt="PyPI - swarmauri_measurement_tokencountestimator"/></a>
</p>

---

# Swarmauri Measurement Token Count Estimator

Token-count measurement plugin for Swarmauri pipelines. Uses OpenAI's `tiktoken` library to estimate how many tokens a piece of text will consume given a specific tokenizer (default `cl100k_base`).

## Features

- Implements the `MeasurementBase` API to slot into Swarmauri observability flows.
- Wraps `tiktoken` encoders for quick token-count estimation ahead of LLM calls.
- Configurable tokenizer name so you can match counts to different model families.

## Prerequisites

- Python 3.10 or newer.
- `tiktoken` installed (pulled in automatically as a dependency).
- If you use custom encodings, ensure they are registered with `tiktoken` before invoking the measurement.

## Installation

```bash
# pip
pip install swarmauri_measurement_tokencountestimator

# poetry
poetry add swarmauri_measurement_tokencountestimator

# uv (pyproject-based projects)
uv add swarmauri_measurement_tokencountestimator
```

## Quickstart

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
text = "Lorem ipsum odor amet, consectetuer adipiscing elit."
count = measurement.calculate(text)
print(f"Tokens (cl100k_base): {count}")
```

## Switching Encodings

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

text = "Swarmauri agents coordinate over shared memory"
measurement = TokenCountEstimatorMeasurement()

for encoding in ["cl100k_base", "o200k_base", "p50k_base"]:
    print(encoding, measurement.calculate(text, encoding=encoding))
```

Use this to check token budgets across different model families before dispatching a request.

## Handling Unknown Encodings

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
invalid_count = measurement.calculate("Hello", encoding="not-real")
print(invalid_count)  # Returns None and prints an error message
```

Wrap the call if you prefer structured error handling:

```python
try:
    count = measurement.calculate("Hello", encoding="not-real")
    if count is None:
        raise ValueError("Unsupported encoding")
except ValueError:
    # fallback logic
    pass
```

## Tips

- Token counts can change as tokenizers evolve; pin `tiktoken` to a known version for stable measurements.
- Normalize whitespace if your prompt assembly adds or strips spaces—tokenizers are sensitive to exact byte sequences.
- For batch estimation, combine this measurement with Pandas or list comprehensions to preprocess entire prompt sets before sending them to an LLM.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
