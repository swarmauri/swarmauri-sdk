![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_parser_textblob)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_parser_textblob)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_parser_textblob)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_parser_textblob?label=swarmauri_parser_textblob&color=green)

</div>

---

# Swarmauri Parser TextBlob

A parser package that leverages TextBlob for natural language processing tasks such as sentence parsing and noun phrase extraction.

## Installation

```bash
pip install swarmauri_parser_textblob
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.parsers.TextBlobSentenceParser import TextBlobSentenceParser
from swarmauri.parsers.TextBlobNounParser import TextBlobNounParser

# Example usage of TextBlobSentenceParser
sentence_parser = TextBlobSentenceParser()
sentences = sentence_parser.parse("One more large chapula please.")
for doc in sentences:
    print(doc.content)

# Example usage of TextBlobNounParser
noun_parser = TextBlobNounParser()
documents = noun_parser.parse("One more large chapula please.")
for doc in documents:
    print(doc.content)
    print(doc.metadata["noun_phrases"])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
