![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_measurement_mutualinformation/">
        <img src="https://static.pepy.tech/badge/swarmauri_measurement_mutualinformation/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_mutualinformation/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_mutualinformation.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/pypi/l/swarmauri_measurement_mutualinformation" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/">
        <img src="https://img.shields.io/pypi/v/swarmauri_measurement_mutualinformation?label=swarmauri_measurement_mutualinformation&color=green" alt="PyPI - swarmauri_measurement_mutualinformation"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Measurement Mutual Information

`swarmauri_measurement_mutualinformation` is the Swarmauri feature-signal
measurement for supervised classification datasets. It wraps
`sklearn.feature_selection.mutual_info_classif` and returns the average mutual
information across all non-target columns in a Pandas DataFrame.

## Why Use Swarmauri Measurement Mutual Information

- Estimate how strongly each feature depends on a discrete target before model
  training.
- Reduce low-signal columns earlier in a Swarmauri data or evaluation pipeline.
- Reuse a standard `MeasurementBase` component instead of hand-wiring feature
  scoring logic.
- Pair feature screening with downstream metrics, vectorization, or model
  selection flows.

## FAQ

> **What input does this measurement expect?**  
> A Pandas `DataFrame` plus the name of the target column.

> **What does it return?**  
> A single float: the mean of the per-feature mutual-information scores
> produced by `mutual_info_classif`.

> **Does it return one score per feature?**  
> No. This component averages the feature scores. If you need per-feature
> values, call `mutual_info_classif` directly.

> **What units are the underlying scores in?**  
> Scikit-learn documents `mutual_info_classif` outputs in natural-log units.

## Features

- Supervised mutual-information scoring for discrete targets.
- Automatic exclusion of the target column from the feature matrix.
- Returns one aggregate score that is easy to log, compare, or threshold.
- Uses the Swarmauri measurement interface for pipeline compatibility.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_measurement_mutualinformation
```

```bash
pip install swarmauri_measurement_mutualinformation
```

## Usage

```python
import pandas as pd
from swarmauri_measurement_mutualinformation import MutualInformationMeasurement

frame = pd.DataFrame(
    {
        "feature_a": [0, 1, 1, 0, 1, 0],
        "feature_b": [5.1, 5.0, 4.9, 5.2, 5.1, 5.0],
        "target": [0, 1, 1, 0, 1, 0],
    }
)

measurement = MutualInformationMeasurement()
score = measurement.calculate(frame, target_column="target")
print(score)
```

## Examples

### Screen a small classification dataset

```python
import pandas as pd
from swarmauri_measurement_mutualinformation import MutualInformationMeasurement

data = pd.DataFrame(
    {
        "clicked_email": [1, 0, 1, 1, 0, 0],
        "days_active": [4, 2, 5, 6, 1, 2],
        "plan_tier": [2, 1, 2, 3, 1, 1],
        "converted": [1, 0, 1, 1, 0, 0],
    }
)

measurement = MutualInformationMeasurement()
print(measurement.calculate(data, target_column="converted"))
```

### Inspect per-feature scores directly

```python
from sklearn.feature_selection import mutual_info_classif

X = frame.drop(columns=["target"])
y = frame["target"]

scores = mutual_info_classif(X, y)
for column, score in zip(X.columns, scores):
    print(column, score)
```

## Related Packages

- [swarmauri_measurement_tokencountestimator](https://pypi.org/project/swarmauri_measurement_tokencountestimator/)
- [swarmauri_metric_hamming](https://pypi.org/project/swarmauri_metric_hamming/)
- [swarmauri_measurement_mutualinformation](https://pypi.org/project/swarmauri_measurement_mutualinformation/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)

## More Documentation

- [scikit-learn `mutual_info_classif` docs](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_classif.html)
- [Pandas documentation](https://pandas.pydata.org/docs/)

## Best Practices

- Encode categorical columns numerically before calling this measurement.
- Remove or impute missing values before scoring.
- Use a stable preprocessing pipeline when comparing MI across experiments.
- Inspect the raw per-feature scores if feature-level ranking matters more than
  a single aggregate summary.

## License

This project is licensed under the Apache-2.0 License.


