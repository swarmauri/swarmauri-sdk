![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_textblob/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_textblob/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_textblob/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_textblob.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_textblob" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_textblob?label=swarmauri_parser_textblob&color=green" alt="PyPI - swarmauri_parser_textblob"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser TextBlob

`swarmauri_parser_textblob` provides two Swarmauri text parsing components built
on [TextBlob](https://textblob.readthedocs.io/): `TextBlobSentenceParser` for
sentence segmentation and `TextBlobNounParser` for noun-phrase extraction. It
is designed for lightweight NLP preprocessing before chunking, retrieval,
classification, or agent workflows.

## Why Use Swarmauri Parser TextBlob

- Split long passages into sentence-level documents for downstream processing.
- Extract noun phrases without introducing a larger transformer stack.
- Keep lightweight linguistic preprocessing aligned with the Swarmauri parser
  interface.
- Use simple NLP enrichment before embeddings, retrieval, or task routing.

## FAQ

> **What parser classes are included?**  
> `TextBlobSentenceParser` and `TextBlobNounParser`.

> **What does the sentence parser return?**  
> A `Document` per detected sentence, with metadata indicating the parser.

> **What does the noun parser return?**  
> A single `Document` containing the original text and a `noun_phrases` list in
> metadata.

> **Does it require NLTK resources?**  
> Yes. The package downloads required NLTK corpora during initialization unless
> they are already present.

## Features

- Sentence segmentation through `TextBlobSentenceParser`.
- Noun phrase extraction through `TextBlobNounParser`.
- Fits Swarmauri ingestion and preprocessing workflows using parser-style
  components.
- Useful for lightweight English NLP pipelines where a smaller dependency stack
  is preferred.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_textblob
```

```bash
pip install swarmauri_parser_textblob
```

Optional setup:

```bash
python -m textblob.download_corpora
```

## Usage

### Sentence parsing

```python
from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
documents = parser.parse("One more large chapula please. It should be extra spicy!")

for document in documents:
    print(document.content)
```

### Noun phrase extraction

```python
from swarmauri_parser_textblob import TextBlobNounParser

parser = TextBlobNounParser()
documents = parser.parse("One more large chapula please.")

print(documents[0].content)
print(documents[0].metadata["noun_phrases"])
```

## Examples

### Prepare sentence-level documents

```python
from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
sentences = parser.parse(
    "Swarmauri coordinates tools. It also routes data through composable components."
)

for sentence in sentences:
    print(sentence.metadata["parser"], sentence.content)
```

### Extract noun phrases for downstream tagging

```python
from swarmauri_parser_textblob import TextBlobNounParser

parser = TextBlobNounParser()
docs = parser.parse("The Swarmauri agent indexed a customer support knowledge base.")

print(docs[0].metadata["noun_phrases"])
```

## Related Packages

- [swarmauri_parser_entityrecognition](https://pypi.org/project/swarmauri_parser_entityrecognition/)
- [swarmauri_tool_entityrecognition](https://pypi.org/project/swarmauri_tool_entityrecognition/)
- [swarmauri_tool_sentimentanalysis](https://pypi.org/project/swarmauri_tool_sentimentanalysis/)
- [swarmauri_parser_bertembedding](https://pypi.org/project/swarmauri_parser_bertembedding/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [TextBlob documentation](https://textblob.readthedocs.io/)
- [NLTK documentation](https://www.nltk.org/)

## Best Practices

- Pre-download NLTK corpora in CI, containers, or production images to avoid
  runtime setup costs.
- Use these parsers for lightweight English NLP tasks; domain-specific or
  multilingual corpora may require a different component.
- Combine sentence parsing with embeddings or vector stores when building
  retrieval-oriented pipelines.
- Treat noun phrase extraction as heuristic enrichment rather than a strict
  ontology or entity-linking system.

## License

This project is licensed under the Apache-2.0 License.

