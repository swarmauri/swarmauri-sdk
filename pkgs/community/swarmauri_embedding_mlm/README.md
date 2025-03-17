
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_mlm" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_embedding_mlm/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_embedding_mlm/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_mlm" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_mlm" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_mlm?label=swarmauri_embedding_mlm&color=green" alt="PyPI - swarmauri_embedding_mlm"/></a>
</p>

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

