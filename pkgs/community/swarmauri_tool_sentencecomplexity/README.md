![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_sentencecomplexity/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentencecomplexity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentencecomplexity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_sentencecomplexity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_sentencecomplexity?label=swarmauri_tool_sentencecomplexity&color=green" alt="PyPI - swarmauri_tool_sentencecomplexity"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Sentence Complexity

`swarmauri_tool_sentencecomplexity` is a Swarmauri NLP tool for estimating how
complex a passage is by measuring average sentence length and average clauses
per sentence. It is useful for editorial review, readability scoring, prompt
inspection, educational feedback, and agent workflows that need quick writing
complexity signals.

## Why Use Swarmauri Tool Sentence Complexity

- Quantify whether writing is becoming harder or easier to parse.
- Detect long, clause-heavy sentences in documentation or prompts.
- Add sentence-level style checks to agent or publishing workflows.
- Pair structural complexity metrics with other readability measures.

## FAQ

> **What does the tool return?**  
> A dictionary with `average_sentence_length` and
> `average_clauses_per_sentence`.

> **How are clauses estimated?**  
> The current heuristic uses punctuation and a list of common conjunctions.

> **What happens with empty input?**  
> The tool raises `ValueError` if the input text is empty or whitespace only.

> **Does this replace full linguistic parsing?**  
> No. It provides a lightweight heuristic, not a full syntactic analysis.

## Features

- Swarmauri `ToolBase` implementation registered as `SentenceComplexityTool`.
- Calculates average sentence length in words.
- Estimates average clause count per sentence using simple heuristics.
- Useful for prompt QA, editorial review, and readability checks.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_sentencecomplexity
```

```bash
pip install swarmauri_tool_sentencecomplexity
```

## Usage

```python
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

tool = SentenceComplexityTool()
metrics = tool("This is a simple sentence. This is another sentence, with a clause.")

print(metrics)
```

## Examples

### Flag overly complex prose

```python
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

tool = SentenceComplexityTool()
metrics = tool("While the system scales across regions, it introduces queues, retries, and latency spikes.")

if metrics["average_sentence_length"] > 25:
    print("Sentence length is high.")
```

### Compare two revisions of a document

```python
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

tool = SentenceComplexityTool()

draft = "The system runs. It works."
final = "Although the system runs reliably, it requires careful coordination across services."

print("draft", tool(draft))
print("final", tool(final))
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

tools = ToolCollection(tools=[SentenceComplexityTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)
- [swarmauri_tool_dalechallreadability](https://pypi.org/project/swarmauri_tool_dalechallreadability/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [NLTK documentation](https://www.nltk.org/)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Use this metric as a heuristic, not as a full grammar parser.
- Compare results across texts of similar genre and purpose.
- Pre-download NLTK tokenizer data in offline environments.
- Pair sentence complexity with lexical density and readability scores for a
  broader text-quality view.

## License

This project is licensed under the Apache-2.0 License.
