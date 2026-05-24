![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_dalechallreadability/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_dalechallreadability/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_dalechallreadability/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_dalechallreadability.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_dalechallreadability" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_dalechallreadability?label=swarmauri_tool_dalechallreadability&color=green" alt="PyPI - swarmauri_tool_dalechallreadability"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Dale-Chall Readability

`swarmauri_tool_dalechallreadability` is a Swarmauri readability-analysis tool
that wraps `textstat` to calculate the Dale-Chall readability score for a block
of text. It is useful for education content, public-sector language review,
documentation QA, prompt inspection, and workflows that need a familiar
readability benchmark.

## Why Use Swarmauri Tool Dale-Chall Readability

- Estimate whether writing is easy enough for the intended audience.
- Add readability gates to content and documentation pipelines.
- Reuse a standard readability metric inside Swarmauri agents and tools.
- Compare revisions or content sets with a consistent score.

## FAQ

> **What does the tool return?**  
> A dictionary with one key: `dale_chall_score`.

> **What input shape does it expect?**  
> The current implementation expects a dictionary containing `input_text`.

> **What library does it use?**  
> It uses `textstat.dale_chall_readability_score`.

> **What does a lower score mean?**  
> Lower Dale-Chall scores generally indicate easier reading.

## Features

- Swarmauri `ToolBase` implementation registered as `DaleChallReadabilityTool`.
- Returns a standard Dale-Chall readability score.
- Works well for educational, policy, and editorial review workflows.
- Thin wrapper over `textstat`, keeping usage simple and predictable.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_dalechallreadability
```

```bash
pip install swarmauri_tool_dalechallreadability
```

## Usage

```python
from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

tool = DaleChallReadabilityTool()
result = tool({"input_text": "This is a simple sentence for testing purposes."})

print(result["dale_chall_score"])
```

## Examples

### Score a policy paragraph

```python
from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

tool = DaleChallReadabilityTool()
score = tool(
    {
        "input_text": "Applicants must complete the registration form and provide identity verification before approval."
    }
)

print(score)
```

### Compare plain-language and technical versions

```python
from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

tool = DaleChallReadabilityTool()

plain = {"input_text": "Read the guide and follow the steps."}
technical = {"input_text": "Administrative verification shall precede credential issuance and service activation."}

print("plain", tool(plain))
print("technical", tool(technical))
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

tools = ToolCollection(tools=[DaleChallReadabilityTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [textstat documentation](https://github.com/textstat/textstat)
- [Dale-Chall readability formula](https://en.wikipedia.org/wiki/Dale%E2%80%93Chall_readability_formula)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Clean markup and normalize whitespace before scoring text.
- Use the score comparatively across similar content types.
- Pair Dale-Chall with structural metrics for better editorial judgment.
- Wrap the input text into the expected `{"input_text": ...}` shape.

## License

This project is licensed under the Apache-2.0 License.
