![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_sentimentanalysis/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentimentanalysis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentimentanalysis.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_sentimentanalysis" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_sentimentanalysis?label=swarmauri_tool_sentimentanalysis&color=green" alt="PyPI - swarmauri_tool_sentimentanalysis"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Sentiment Analysis

`swarmauri_tool_sentimentanalysis` is the Swarmauri sentiment-analysis tool
built on Hugging Face transformers. It wraps the
`pipeline("sentiment-analysis")` surface and returns a simple dictionary with a
single `sentiment` label for the input text.

## Why Use Swarmauri Tool Sentiment Analysis

- Add fast text sentiment classification to agent and tool-calling workflows.
- Return a compact structured output that is easy to route, log, or attach to
  larger decisions.
- Use transformer-based sentiment inference without building a custom model
  wrapper.
- Pair sentiment labels with entity extraction, parsing, or downstream
  automation in Swarmauri pipelines.

## FAQ

> **What does this tool return?**  
> A dictionary in the shape `{"sentiment": "<LABEL>"}`.

> **What labels should I expect?**  
> Labels depend on the underlying Hugging Face pipeline model. In practice the
> current tests allow `POSITIVE`, `NEGATIVE`, or `NEUTRAL`.

> **Does it download a model on first use?**  
> Yes. The underlying transformers pipeline downloads model assets if they are
> not already cached.

> **Can I use it inside tool-calling or orchestration workflows?**  
> Yes. It is packaged as a Swarmauri `ToolBase` component.

## Features

- Transformer-backed sentiment analysis via Hugging Face pipelines.
- Swarmauri `ToolBase` integration with a single `text` parameter.
- Returns a compact dictionary response suitable for automation and routing.
- Works for quick sentiment checks in text review, feedback analysis, and
  content classification workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_sentimentanalysis
```

```bash
pip install swarmauri_tool_sentimentanalysis
```

## Usage

```python
from swarmauri_tool_sentimentanalysis import SentimentAnalysisTool

tool = SentimentAnalysisTool()
result = tool("I love this product!")
print(result)
```

## Examples

### Analyze customer feedback

```python
from swarmauri_tool_sentimentanalysis import SentimentAnalysisTool

tool = SentimentAnalysisTool()

print(tool("I love this product!"))
print(tool("I hate this product!"))
print(tool("This product is okay."))
```

### Use sentiment labels for routing

```python
from swarmauri_tool_sentimentanalysis import SentimentAnalysisTool

tool = SentimentAnalysisTool()
sentiment = tool("The latest release is disappointing.")["sentiment"]

if sentiment == "NEGATIVE":
    print("Escalate for review")
```

## Related Packages

- [swarmauri_tool_entityrecognition](https://pypi.org/project/swarmauri_tool_entityrecognition/)
- [swarmauri_parser_textblob](https://pypi.org/project/swarmauri_parser_textblob/)
- [swarmauri_parser_entityrecognition](https://pypi.org/project/swarmauri_parser_entityrecognition/)
- [swarmauri_parser_bertembedding](https://pypi.org/project/swarmauri_parser_bertembedding/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Hugging Face text classification task guide](https://huggingface.co/docs/transformers/tasks/sequence_classification)
- [Transformers pipeline documentation](https://huggingface.co/docs/transformers/main_classes/pipelines)

## Best Practices

- Cache Hugging Face assets in CI or deployment environments to avoid repeated
  downloads.
- Validate expected labels against the actual model in your deployment, because
  different models can emit different label vocabularies.
- Use explicit downstream mapping if your application needs stable polarity
  buckets.
- Pair sentiment output with other tools when you need richer reasoning than a
  single label.

## License

This project is licensed under the Apache-2.0 License.



