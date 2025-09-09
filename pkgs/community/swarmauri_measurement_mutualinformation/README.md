
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_measurement_mutualinformation" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_mutualinformation/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_mutualinformation.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_measurement_mutualinformation" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/pypi/l/swarmauri_measurement_mutualinformation" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/pypi/v/swarmauri_measurement_mutualinformation?label=swarmauri_measurement_mutualinformation&color=green" alt="PyPI - swarmauri_measurement_mutualinformation"/></a>
</p>

---

# Swarmauri Measurement Mutual Information

A package to calculate mutual information between features and a target column in a given dataset.

## Installation

```bash
pip install swarmauri_measurement_mutualinformation
```

## Usage

Basic usage example with code snippets:

```python
import pandas as pd
from swarmauri.measurements.MutualInformationMeasurement import MutualInformationMeasurement

# Sample DataFrame
data = pd.DataFrame({
    'feature1': [1, 2, 3, 4, 5],
    'feature2': [5, 4, 3, 2, 1],
    'target': [0, 1, 0, 1, 0]
})

# Initialize the measurement
measurement = MutualInformationMeasurement(value=10)

# Calculate mutual information
mi_score = measurement.calculate(data, target_column='target')
print(f"Average Mutual Information: {mi_score} bits")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
