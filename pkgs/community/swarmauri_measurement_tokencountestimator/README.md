
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

A measurement class to estimate the number of tokens in a given text.

## Installation

```bash
pip install swarmauri_measurement_tokencountestimator
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.measurements.TokenCountEstimatorMeasurement import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
text = "Lorem ipsum odor amet, consectetuer adipiscing elit."
token_count = measurement.calculate(text)
print(f"Token count: {token_count}")
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
