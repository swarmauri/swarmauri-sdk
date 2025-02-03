![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri-embedding-mlm)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri-embedding-mlm)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri-embedding-mlm)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri-embedding-mlm?label=swarmauri-embedding-mlm&color=green)

</div>

---

# Swarmauri Embedding MLM

This package provides an implementation of an embedding model that fine-tunes a Masked Language Model (MLM) for generating embeddings.

## Installation

```bash
pip install swarmauri_embedding_mlm
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.embeddings.MlmEmbedding import MlmEmbedding

# Initialize the embedder
embedder = MlmEmbedding()

# Fit the model on a list of documents
documents = ["This is a test document.", "Another document for embedding."]
embedder.fit(documents)

# Transform documents to embeddings
embeddings = embedder.transform(documents)

# Save the model
embedder.save_model("path/to/save/model")

# Load the model
embedder.load_model("path/to/save/model")

# Infer vector for a single document
vector = embedder.infer_vector("This is a new document.")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

