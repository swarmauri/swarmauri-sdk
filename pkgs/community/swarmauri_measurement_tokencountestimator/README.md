![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://static.pepy.tech/badge/swarmauri_measurement_tokencountestimator/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_tokencountestimator/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_measurement_tokencountestimator.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/pypi/l/swarmauri_measurement_tokencountestimator" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_measurement_tokencountestimator/">
        <img src="https://img.shields.io/pypi/v/swarmauri_measurement_tokencountestimator?label=swarmauri_measurement_tokencountestimator&color=green" alt="PyPI - swarmauri_measurement_tokencountestimator"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Measurement Token Count Estimator

`swarmauri_measurement_tokencountestimator` is the Swarmauri token-budget
measurement for estimating text length with OpenAI's
[tiktoken](https://github.com/openai/tiktoken). It helps you approximate prompt
size before sending text into LLM, embedding, or chat-completion workflows.

## Why Use Swarmauri Measurement Token Count Estimator

- Estimate prompt size before dispatching expensive model calls.
- Compare token usage across multiple `tiktoken` encodings.
- Reuse a standard Swarmauri `MeasurementBase` component in observability,
  cost-control, and prompt-construction flows.
- Add quick token-budget checks to preprocessing or routing pipelines.

## FAQ

> **What does this measurement return?**  
> An integer token count, or `None` when the requested encoding is invalid.

> **What encoding does it use by default?**  
> `cl100k_base`.

> **Can I use another tokenizer?**  
> Yes. Pass a different `encoding` name supported by `tiktoken`.

> **Does it raise on unknown encodings?**  
> No. The current implementation prints the error and returns `None`.

## Features

- Token-count estimation backed by `tiktoken`.
- Configurable encoding name for different model families.
- Simple Swarmauri measurement component for cost and context-window checks.
- Useful for prompt budgeting, chunk sizing, and preflight validation.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_measurement_tokencountestimator
```

```bash
pip install swarmauri_measurement_tokencountestimator
```

## Usage

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
text = "Lorem ipsum odor amet, consectetuer adipiscing elit."
count = measurement.calculate(text)
print(count)
```

## Examples

### Compare encodings for the same text

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

text = "Swarmauri agents coordinate over shared memory."
measurement = TokenCountEstimatorMeasurement()

for encoding in ["cl100k_base", "o200k_base", "p50k_base"]:
    print(encoding, measurement.calculate(text, encoding=encoding))
```

### Preflight a prompt budget

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
prompt = "Summarize the following customer support conversation..."

token_count = measurement.calculate(prompt)
if token_count is not None and token_count > 4000:
    print("Prompt should be chunked before dispatch.")
```

### Handle unsupported encodings

```python
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

measurement = TokenCountEstimatorMeasurement()
print(measurement.calculate("Hello", encoding="not-real"))
```

## Related Packages

- [swarmauri_measurement_mutualinformation](https://pypi.org/project/swarmauri_measurement_mutualinformation/)
- [swarmauri_metric_hamming](https://pypi.org/project/swarmauri_metric_hamming/)
- [swarmauri_measurement_tokencountestimator](https://pypi.org/project/swarmauri_measurement_tokencountestimator/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)

## More Documentation

- [OpenAI `tiktoken` repository](https://github.com/openai/tiktoken)
- [OpenAI cookbook token counting examples](https://cookbook.openai.com/)

## Best Practices

- Pin `tiktoken` if you need stable counts across builds and CI runs.
- Measure fully assembled prompts, not partial templates, when enforcing hard
  token budgets.
- Normalize whitespace consistently because tokenizers are sensitive to exact
  byte sequences.
- Treat `None` as an invalid-encoding signal and route it through explicit
  fallback logic.

## License

This project is licensed under the Apache-2.0 License.

