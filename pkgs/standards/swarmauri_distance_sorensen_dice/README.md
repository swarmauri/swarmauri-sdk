![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)
<p align="center">
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>
# Swarmauri Distance Sorensen Dice

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Install it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Preferred import: `swarmauri_standard.similarities.DiceSimilarity.DiceSimilarity`

## Compatibility Scope

- Re-exports `SorensenDiceDistance` from `swarmauri_standard.distances`.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Migration Example

```python
from swarmauri_standard.similarities.DiceSimilarity import DiceSimilarity

similarity = DiceSimilarity()
score = similarity.similarity({1, 2, 3}, {2, 3, 4})
```

## Legacy Installation

```bash
uv pip install swarmauri_distance_sorensen_dice
```

```bash
pip install swarmauri_distance_sorensen_dice
```



