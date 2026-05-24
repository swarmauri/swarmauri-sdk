![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://static.pepy.tech/badge/swarmauri_evaluatorpool_accessibility/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluatorpool_accessibility.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluatorpool_accessibility" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluatorpool_accessibility?label=swarmauri_evaluatorpool_accessibility&color=green" alt="PyPI - swarmauri_evaluatorpool_accessibility"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Evaluatorpool Accessibility

Accessibility-focused evaluator pool for Swarmauri programs. The pool bundles a
set of classic readability metrics (Automated Readability Index, Colemanâ€“Liau,
Fleschâ€“Kincaid Grade, Flesch Reading Ease, and Gunning Fog) and normalises their
scores onto a single 0â€“1 scale where higher values mean easier-to-read content.

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

- `score`: the weighted mean of the evaluator scores mapped to the 0â€“1 range.
- `metadata["evaluator_scores"]`: raw scores keyed by evaluator name.
- `metadata["evaluator_metadata"]`: evaluator-specific metadata (e.g. sentence
  counts, syllable estimates, interpretation strings).
- `metadata["aggregate_score"]`: mirrors `.score` for convenience.

You can customise the weighting of each evaluator by passing a `weights`
dictionary (name â†’ float) when constructing the pool.

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



