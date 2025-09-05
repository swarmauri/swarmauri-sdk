# SDK Style Guide

This document outlines the coding and documentation standards for our SDK. Our goal is to ensure a consistent, clear, and maintainable codebase. We adhere to established Python standards (PEP 8 and PEP 257) and specifically utilize spaCy’s docstring style.

---

## Table of Contents

- [General Coding Standards](#general-coding-standards)
- [Testing Conventions](#testing-conventions)
- [Docstring Conventions](#docstring-conventions)
  - [Overview](#overview)
  - [Structure](#structure)
  - [Example](#example)
- [Packaging Standards](#packaging-standards)
- [Contributing](#contributing)
- [References](#references)

---

## General Coding Standards

- **PEP 8 Compliance:**  
  Follow PEP 8 for overall code style, including naming conventions, line lengths, and whitespace usage.
  
- **Readable and Maintainable Code:**  
  Write clear, self-explanatory code. Refactor and comment where necessary to improve clarity.
  
- **Consistent Formatting:**
  Use our style guide and formatting tools (e.g., linters, formatters) to maintain consistency across the codebase.

## Testing Conventions

All tests must reside in directories named for their pytest marker. Example locations include:
- `tests/unit/`
- `tests/i9n/`
- `tests/r8n/`

Each test module must also include the corresponding `@pytest.mark.<marker>` annotation.

---

## Docstring Conventions

We follow spaCy’s docstring style to ensure our documentation is clear and consistent.

### Overview

- **Triple Double Quotes:**  
  Use `"""` for all docstrings.
  
- **Placement:**  
  Place the docstring immediately after the function, method, class, or module definition.

- **Imperative Mood:**  
  Write summaries in the imperative mood (e.g., "Return", "Process", "Compute").

### Structure

1. **One-Line Summary:**  
   - A concise description of what the function/class/module does.
   
2. **Blank Line:**  
   - Insert a blank line after the summary if the docstring contains additional detail.
   
3. **Extended Description:**  
   - Provide any extra information necessary to understand the code’s purpose or behavior.
   
4. **Parameter Section (Args):**  
   - List each parameter, its type, and a brief description.
   
5. **Returns Section:**  
   - Describe the return type and the meaning of the returned value.
   
6. **Raises Section (if applicable):**  
   - List any exceptions that might be raised by the function.

### Example

Below is an example demonstrating the spaCy docstring style at the method level:

```python
def process_text(text: str) -> Doc:
    """
    Process a text string and return a spaCy Doc object.

    This function tokenizes and annotates the input text using spaCy's NLP pipeline.

    Args:
        text (str): The input text to be processed.

    Returns:
        Doc: The processed spaCy Doc object.

    Raises:
        ValueError: If the input text is empty.
    """
    if not text:
        raise ValueError("Input text must not be empty.")
    # Processing code goes here
```

Below is an example demonstrating the spaCy docstring style at the module level:

```python
"""
text_utils.py

This module provides utilities for processing text data. It leverages spaCy's NLP
pipeline to tokenize, annotate, and analyze text, offering helper classes and functions
to simplify common text processing tasks.
"""

import spacy
```

Below is an example demonstrating spaCy docstring style at the class level:

```python
class TextProcessor:
    """
    A class for processing and analyzing text data using spaCy.

    This class provides methods to tokenize, lemmatize, and extract named entities from text.
    It utilizes spaCy's NLP pipeline to annotate the text and offers helper methods for
    common text processing tasks.

    Attributes:
        nlp (spacy.language.Language): The spaCy NLP model used for processing text.
    """

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize the TextProcessor with the specified spaCy model.

        Args:
            model (str): The name of the spaCy model to load (default is "en_core_web_sm").
        """
        self.nlp = spacy.load(model)

    def process(self, text: str):
        """
        Process the input text and return the annotated spaCy Doc object.

        Args:
            text (str): The input text to process.

        Returns:
            spacy.tokens.Doc: The processed document with tokens, entities, and annotations.

        Raises:
            ValueError: If the input text is empty.
        """
        if not text:
            raise ValueError("Input text must not be empty.")
        return self.nlp(text)
```

## Packaging Standards

All standalone packages follow a consistent layout and metadata style.

### pyproject.toml Pattern

Use the standard project table with a GitHub repository link and reference
internal dependencies via `tool.uv.sources`:

```toml
[project]
name = "your_package"
version = "<version>"
readme = "README.md"
repository = "https://github.com/swarmauri/swarmauri-sdk"

[tool.uv.sources]
swarmauri_core = { workspace = true }
swarmauri_base = { workspace = true }
```

### README Branding

Every package README begins with the Swarmauri logo and PyPI badges showing
downloads, supported Python versions, and the latest release.

### Standalone Package Layout

```
pkgs/<tier>/<package>/
    pyproject.toml
    README.md
    <package>/
        __init__.py
        ...
```

### Entry Points

Plugins are exposed through `[project.entry-points]` groups. Example:

```toml
[project.entry-points."peagen.publishers"]
rabbitmq = "peagen.plugins.publishers.rabbitmq_publisher:RabbitMQPublisher"
```

### Monorepo Workspace

Add new packages to `pkgs/pyproject.toml` under `tool.uv.workspace.members` so
they are installed and tested with the rest of the SDK.
