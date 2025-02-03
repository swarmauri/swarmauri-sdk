![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_measurement_tokencountestimator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_measurement_tokencountestimator)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_measurement_tokencountestimator)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_measurement_tokencountestimator?label=swarmauri_measurement_tokencountestimator&color=green)

</div>

---

# Token Count Estimator Measurement

A measurement class to estimate the number of tokens in a given text.

## Installation

```bash
pip install swarmauri_measurement_tokencountestimator
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri_measurement_tokencountestimator.TokenCountEstimatorMeasurement import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
text = "Lorem ipsum odor amet, consectetuer adipiscing elit."
token_count = measurement.calculate(text)
print(f"Token count: {token_count}")
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
