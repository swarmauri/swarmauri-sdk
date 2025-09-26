![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

Mutual-information measurement plugin for Swarmauri pipelines. Computes the average mutual information (in bits) between every feature column and a target column, letting you rank signal strength before training models.

## Features

- Wraps `sklearn.feature_selection.mutual_info_classif` behind the standard `MeasurementBase` API.
- Supports Pandas DataFrame inputs; automatically excludes the target column from the feature set.
- Returns the average mutual information across all features (in bits) for quick screening.

## Prerequisites

- Python 3.10 or newer.
- `scikit-learn` and `pandas` installed (pulled in as dependencies of this package).
- Clean, pre-processed categorical data (encode non-numeric columns before calling) since `mutual_info_classif` expects numerical inputs.

## Installation

```bash
# pip
pip install swarmauri_measurement_mutualinformation

# poetry
poetry add swarmauri_measurement_mutualinformation

# uv (pyproject-based projects)
uv add swarmauri_measurement_mutualinformation
```

## Quickstart

```python
import pandas as pd
from swarmauri_measurement_mutualinformation import MutualInformationMeasurement

# Example dataset
frame = pd.DataFrame(
    {
        "feature_a": [0, 1, 1, 0, 1, 0],
        "feature_b": [5.1, 5.0, 4.9, 5.2, 5.1, 5.0],
        "target": [0, 1, 1, 0, 1, 0],
    }
)

mi = MutualInformationMeasurement()
avg_mi = mi.calculate(frame, target_column="target")
print(f"Average mutual information: {avg_mi:.4f} bits")
```

## Per-Feature Scores

If you need the individual MI score per feature, compute it directly and inspect the array:

```python
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

frame = pd.DataFrame(
    {
        "feat1": [0, 1, 1, 0, 1, 0],
        "feat2": [5.1, 5.0, 4.9, 5.2, 5.1, 5.0],
        "target": [0, 1, 1, 0, 1, 0],
    }
)

scores = mutual_info_classif(frame[["feat1", "feat2"]], frame["target"])
for column, score in zip(["feat1", "feat2"], scores):
    print(column, score)
```

Use the per-feature scores to filter low-signal columns before passing the DataFrame back through Swarmauri.

## Tips

- Normalize or discretize continuous features when comparing very different scales; mutual information is sensitive to distribution assumptions.
- Handle missing values before calling `calculate`; `mutual_info_classif` does not accept NaNs.
- Binary targets work out of the box; for multi-class targets, ensure `target_column` contains integer encodings.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
