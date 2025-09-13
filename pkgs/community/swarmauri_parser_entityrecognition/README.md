
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_entityrecognition" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_entityrecognition/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_entityrecognition.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_entityrecognition" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_entityrecognition" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_entityrecognition?label=swarmauri_parser_entityrecognition&color=green" alt="PyPI - swarmauri_parser_entityrecognition"/></a>
</p>

---

# Swarmauri Parser Entityrecognition

EntityRecognitionParser leverages NER capabilities to parse text and extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.

## Installation

```bash
pip install swarmauri_parser_entityrecognition
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.parsers.EntityRecognitionParser import EntityRecognitionParser

# Initialize the parser
parser = EntityRecognitionParser()

# Parse text to extract entities
text = "Barack Obama was born in Hawaii."
entities = parser.parse(text)

# Print extracted entities
for entity in entities:
    print(f"Entity: {entity.content}, Type: {entity.metadata['entity_type']}")
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
