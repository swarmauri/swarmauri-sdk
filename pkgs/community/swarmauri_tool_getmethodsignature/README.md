![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_getmethodsignature/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_getmethodsignature/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_getmethodsignature/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_getmethodsignature.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_getmethodsignature/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_getmethodsignature/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_getmethodsignature" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_getmethodsignature/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_getmethodsignature?label=swarmauri_tool_getmethodsignature&color=green" alt="PyPI - swarmauri_tool_getmethodsignature"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Get Method Signature

`swarmauri_tool_getmethodsignature` is a Swarmauri tool that parses Python
source code with the standard-library `ast` module and returns the
signature of a specified function or method, including its name,
parameters, and return type. It is useful for documentation generation,
refactoring assistants, agent-driven code review, and static
introspection workflows.

## Why Use Swarmauri Tool Get Method Signature

- Inspect function and method signatures without importing source code.
- Capture parameter names, annotations, and defaults in one call.
- Detect overloaded definitions that share a single function name.
- Distinguish synchronous functions from `async def` coroutines.
- Reuse the same tool in agents, notebooks, scripts, and backend
  workflows.

## FAQ

> **What does the tool return?**  
> A dictionary with `name`, `parameters`, `return_type`, `signature`,
> and `is_async`. When multiple definitions share the requested name, it
> returns `{"overloads": [...]}` instead.

> **Does the tool execute the source code?**  
> No. It uses `ast.parse` for purely static analysis and never imports
> or executes the supplied source.

> **What happens when the function is missing?**  
> The tool returns `{"error": "..."}` describing the failure, including
> cases where the source cannot be parsed.

> **Are parameter defaults and annotations captured?**  
> Yes. Each parameter entry includes `name`, `annotation` (when present),
> and `default` (when present), rendered back to source text via
> `ast.unparse`.

## Features

- Swarmauri `ToolBase` implementation registered as
  `GetMethodSignatureTool`.
- Static `ast`-based parsing with no dynamic code execution.
- Support for positional-only, keyword-only, `*args`, and `**kwargs`
  parameters.
- Detection of overloaded functions sharing a single name.
- Renders a human-readable `signature` string for each definition.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_getmethodsignature
```

```bash
pip install swarmauri_tool_getmethodsignature
```

## Usage

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = "def add(a: int, b: int = 0) -> int:\n    return a + b\n"
result = tool(source=source, method_name="add")

print(result["signature"])
# def add(a: int, b: int = 0) -> int
```

## Examples

### Inspect an async method inside a class

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = (
    "class Service:\n"
    "    async def fetch(self, url: str) -> bytes:\n"
    "        ...\n"
)
result = tool(source=source, method_name="fetch")

print(result["is_async"])  # True
print(result["return_type"])  # bytes
```

### Detect overloaded definitions

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = (
    "def process(x: int) -> int:\n"
    "    return x\n"
    "def process(x: str) -> str:\n"
    "    return x\n"
)
result = tool(source=source, method_name="process")

print(len(result["overloads"]))  # 2
```

### Register the tool inside a Swarmauri tool registry

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tools = ToolCollection(tools=[GetMethodSignatureTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_searchword](https://pypi.org/project/swarmauri_tool_searchword/)
- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Python ast module](https://docs.python.org/3/library/ast.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Pass complete, syntactically valid Python source for best results.
- Treat the `signature` string as a rendering hint rather than canonical
  source; round-trip formatting depends on the Python version.
- Use the `overloads` list when auditing code that relies on name reuse.
- Pair this tool with documentation generators to enrich API references.
- Avoid relying on dynamic imports; this tool performs static analysis
  only.

> **Note:** This tool performs static analysis on Python source code
> strings via the `ast` module. For runtime inspection of
> already-imported callables, see `MethodSignatureExtractor` in
> `swarmauri_standard.utils.method_signature_extractor_decorator`.

## License

This project is licensed under the Apache-2.0 License.
