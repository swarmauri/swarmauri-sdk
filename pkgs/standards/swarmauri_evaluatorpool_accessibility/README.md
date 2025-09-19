![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluatorpool_accessibility" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluatorpool_accessibility.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluatorpool_accessibility" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluatorpool_accessibility" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluatorpool_accessibility?label=swarmauri_evaluatorpool_accessibility&color=green" alt="PyPI - swarmauri_evaluatorpool_accessibility"/>
    </a>
</p>

---

# Swarmauri Evaluatorpool Accessibility

Accessibility-focused evaluator pool for Swarmauri programs. The pool bundles a
set of classic readability metrics (Automated Readability Index, Coleman–Liau,
Flesch–Kincaid Grade, Flesch Reading Ease, and Gunning Fog) and normalises their
scores onto a single 0–1 scale where higher values mean easier-to-read content.

## Installation

### pip

```bash
pip install swarmauri_evaluatorpool_accessibility
```

### Poetry

```bash
poetry add swarmauri_evaluatorpool_accessibility
```

### uv

```bash
# Install into the current environment
uv pip install swarmauri_evaluatorpool_accessibility

# Or add it to the project pyproject.toml
uv add swarmauri_evaluatorpool_accessibility
```

## Usage

`AccessibilityEvaluatorPool` is a registered `EvaluatorPoolBase` component. It
expects a sequence of Swarmauri `Program` objects, runs the configured
evaluators concurrently, then returns standard `EvalResultBase` instances with
the aggregated score and detailed metadata for every evaluator.

### Example

```python
from swarmauri_evaluatorpool_accessibility.AccessibilityEvaluatorPool import AccessibilityEvaluatorPool
from swarmauri_standard.programs.Program import Program

program = Program(content={"example.txt": "This is a simple sentence. Here is another one."})

pool = AccessibilityEvaluatorPool()
pool.initialize()  # spin up the thread pool once before evaluating

results = pool.evaluate([program])
result = results[0]

print(f"Aggregate accessibility score: {result.score:.2f}")
print("Per-evaluator scores:", result.metadata["evaluator_scores"])
flesch_meta = result.metadata["evaluator_metadata"].get(
    "FleschReadingEaseEvaluator", {}
)
print(
    "Flesch interpretation:",
    flesch_meta.get("readability_interpretation", flesch_meta.get("error", "not available")),
)

pool.shutdown()  # release resources when finished
```

### Result structure

Each entry returned from `evaluate` is an `EvalResultBase` with:

- `score`: the weighted mean of the evaluator scores mapped to the 0–1 range.
- `metadata["evaluator_scores"]`: raw scores keyed by evaluator name.
- `metadata["evaluator_metadata"]`: evaluator-specific metadata (e.g. sentence
  counts, syllable estimates, interpretation strings).
- `metadata["aggregate_score"]`: mirrors `.score` for convenience.

You can customise the weighting of each evaluator by passing a `weights`
dictionary (name → float) when constructing the pool.

### Notes

- The pool automatically registers the bundled evaluators when no explicit list
  is provided. You can pass your own evaluators that satisfy the `IEvaluate`
  interface to override or extend the defaults.
- `FleschReadingEaseEvaluator` downloads NLTK's `punkt` tokenizer and
  `cmudict` pronunciation dictionary on first use. Set `NLTK_DATA_DIR` to point
  to a writable cache location if required. When these resources are not
  available the evaluator reports an `"error"` entry in its metadata instead of
  raising an exception.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

