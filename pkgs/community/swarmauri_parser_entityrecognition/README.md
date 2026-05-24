![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_entityrecognition/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_entityrecognition/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_entityrecognition/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_entityrecognition.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_entityrecognition" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_entityrecognition?label=swarmauri_parser_entityrecognition&color=green" alt="PyPI - swarmauri_parser_entityrecognition"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser Entity Recognition

`swarmauri_parser_entityrecognition` is the Swarmauri named-entity recognition
parser built on [spaCy](https://spacy.io/). It extracts named entities such as
people, organizations, and geopolitical entities from unstructured text and
returns Swarmauri `Document` objects containing the entity text and entity
metadata.

## Why Use Swarmauri Parser Entity Recognition

- Turn raw text into structured entity objects inside a Swarmauri parser
  workflow.
- Preserve entity labels and entity ids in a predictable `Document` shape for
  downstream enrichment, filtering, or indexing.
- Use spaCy's English NER pipeline when available, while still retaining a
  minimal fallback path for constrained environments.
- Fit entity extraction into larger ingestion, retrieval, anonymization, and
  knowledge-graph workflows.

## FAQ

> **What does this parser return?**  
> A list of Swarmauri `Document` objects, usually one per detected entity.

> **Which metadata fields are included?**  
> `entity_type`, `entity_id`, and `text`.

> **What spaCy model does it use?**  
> It tries to load `en_core_web_sm`.

> **What happens if the model is unavailable?**  
> The parser attempts to download the model. If that fails, it falls back to a
> blank English pipeline plus a small regex-based fallback used as a best-effort
> compatibility path.

## Features

- Named-entity extraction via spaCy's English NER model.
- Automatic attempt to download `en_core_web_sm` if the model is missing.
- Best-effort fallback behavior for environments where the full model cannot be
  loaded.
- Returns Swarmauri `Document` objects with entity label metadata.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_entityrecognition
```

```bash
pip install swarmauri_parser_entityrecognition
```

Optional model bootstrap:

```bash
python -m spacy download en_core_web_sm
```

## Usage

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

text = "Barack Obama was born in Hawaii and served as President of the United States."
parser = EntityRecognitionParser()
entities = parser.parse(text)

for entity in entities:
    print(entity.content, entity.metadata["entity_type"])
```

## Examples

### Parse organizations, places, and people

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

parser = EntityRecognitionParser()
docs = parser.parse(
    "Apple Inc. is planning to open a new office in New York City, according to CEO Tim Cook."
)

for doc in docs:
    print(doc.content, doc.metadata)
```

### Handle non-string input

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

parser = EntityRecognitionParser()
print(parser.parse(42))
```

### Inspect fallback-compatible metadata

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

parser = EntityRecognitionParser()
entities = parser.parse("Tim Cook announced new products in New York City for Apple Inc.")
print([entity.metadata for entity in entities])
```

## Related Packages

- [swarmauri_tool_entityrecognition](https://pypi.org/project/swarmauri_tool_entityrecognition/)
- [swarmauri_tool_sentimentanalysis](https://pypi.org/project/swarmauri_tool_sentimentanalysis/)
- [swarmauri_parser_textblob](https://pypi.org/project/swarmauri_parser_textblob/)
- [swarmauri_parser_bertembedding](https://pypi.org/project/swarmauri_parser_bertembedding/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [spaCy named entity recognition docs](https://spacy.io/usage/linguistic-features#named-entities)
- [spaCy model installation docs](https://spacy.io/usage/models)

## Best Practices

- Preinstall `en_core_web_sm` in CI and production environments to avoid
  runtime downloads.
- Treat the regex fallback as a compatibility path, not as production-quality
  entity recognition.
- Strip markup or noisy boilerplate before parsing to improve entity quality.
- Persist entity spans or link them to downstream IDs if you need durable
  knowledge-graph or indexing workflows.

## License

This project is licensed under the Apache-2.0 License.


