# EnsembleBase

Base class for ensemble components in Swarmauri.

## Hierarchy

```
ComponentBase
└── EnsembleBase
```

## Module

`swarmauri.ensembles.base.EnsembleBase`

## Method Signatures

### `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the ensemble base.

### `add`

```python
def add(self, component) -> None
```

Add a component to the ensemble.

| Parameter | Type | Description |
|-----------|------|-------------|
| `component` | `ComponentBase` | Component to add |

### `remove`

```python
def remove(self, component) -> None
```

Remove a component from the ensemble.

| Parameter | Type | Description |
|-----------|------|-------------|
| `component` | `ComponentBase` | Component to remove |

### `predict`

```python
def predict(self, *args, **kwargs)
```

Run prediction across ensemble members. Subclasses must implement aggregation.

### `get_members`

```python
def get_members(self) -> list
```

Return the list of ensemble members.

## Specialization

Subclass `EnsembleBase` to define aggregation strategy:

- Override `predict` to combine member outputs
- Use `add` / `remove` to manage membership
- Call `get_members` when iterating members

## Extension Example

```python
from swarmauri.ensembles.base import EnsembleBase

class VotingEnsemble(EnsembleBase):
    def predict(self, *args, **kwargs):
        votes = [m.predict(*args, **kwargs) for m in self.get_members()]
        return max(set(votes), key=votes.count)
```
