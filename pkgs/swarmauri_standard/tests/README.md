# Swarmauri-SDK Test Cases
This project demonstrates how to classify pytest errors using GitHub Actions and handle the workflow based on the severity of the failures.

## Test Classification

Tests are classified into three categories:
- Unit tests
- Integration tests
- Acceptance tests

## Running the Tests

The tests can be run locally using pytest:
```sh
pytest --junitxml=results.xml
python classify_test_results.py results.xml
```

### Performance Tests

Performance benchmarks are located under `tests/perf`. Execute them with:
```sh
uv run --package swarmauri-standard --directory swarmauri_standard pytest -k perf
```
