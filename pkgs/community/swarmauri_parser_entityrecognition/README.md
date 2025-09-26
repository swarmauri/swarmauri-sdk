![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

Named-entity recognition (NER) parser for Swarmauri built on spaCy. Extracts entities (PERSON, ORG, GPE, etc.) from unstructured text and returns `Document` objects with entity metadata.

## Features

- Uses spaCy's `en_core_web_sm` model by default (downloads automatically if missing).
- Falls back to a blank English pipeline with minimal regex-based tagging when the full model is unavailable (best-effort mode).
- Emits `Document` instances containing the entity text and metadata (`entity_type`, `entity_id`).

## Prerequisites

- Python 3.10 or newer.
- [spaCy](https://spacy.io) and its English model. The parser attempts to download `en_core_web_sm` if missing; set `SPACY_HOME` or pre-install the model in production deployments.
- If running without internet access, install the model ahead of time: `python -m spacy download en_core_web_sm`.

## Installation

```bash
# pip
pip install swarmauri_parser_entityrecognition

# poetry
poetry add swarmauri_parser_entityrecognition

# uv (pyproject-based projects)
uv add swarmauri_parser_entityrecognition
```

## Quickstart

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

text = "Barack Obama was born in Hawaii and served as President of the United States."
parser = EntityRecognitionParser()
entities = parser.parse(text)

for entity_doc in entities:
    print(entity_doc.content, entity_doc.metadata["entity_type"])
```

## Batch Processing

```python
texts = [
    "Apple Inc. unveiled new MacBooks in California.",
    "Tim Cook met investors in New York City.",
]

parser = EntityRecognitionParser()
results = [parser.parse(t) for t in texts]

for doc_set in results:
    for doc in doc_set:
        print(doc.content, doc.metadata["entity_type"])
```

## Handling Fallback Mode

When spaCy's English model is unavailable, the parser performs best-effort matching using a blank pipeline and simple regex patterns. Check for `entity_type` values and the `entity_id` metadata to understand which mode produced the result.

```python
parser = EntityRecognitionParser()
entities = parser.parse("Tim Cook announced new products in New York City for Apple Inc.")
print([d.metadata for d in entities])
```

Install spaCy models before production use to avoid fallback accuracy losses.

## Tips

- For languages beyond English, load a different spaCy model by changing the initialization logic (e.g., subclass the parser and load `es_core_news_sm`).
- Preprocess text to remove noise (HTML tags, markup) before parsing to improve NER accuracy.
- Combine with Swarmauri middleware or pipelines to fuse entity data with downstream tasks (e.g., knowledge graph enrichment, anonymization).

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
