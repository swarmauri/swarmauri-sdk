
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_mlm" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_embedding_mlm/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_embedding_mlm.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_mlm" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_mlm" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_mlm?label=swarmauri_embedding_mlm&color=green" alt="PyPI - swarmauri_embedding_mlm"/></a>
</p>

---

# Swarmauri Embedding MLM

Trainable embedding provider that fine-tunes a Hugging Face masked language model (MLM) end-to-end so Swarmauri agents can produce contextual document vectors without leaving the framework.

## Features

- Wraps any Hugging Face masked language model (`embedding_name`) behind the Swarmauri `EmbeddingBase` interface.
- Supports optional vocabulary expansion via `add_new_tokens` before fine-tuning to capture domain-specific terminology.
- Handles end-to-end fine-tuning with masking, AdamW optimization, and GPU/CPU selection based on availability.
- Exposes pooling utilities (`transform`, `infer_vector`) that average the last hidden state to yield dense vectors ready for downstream retrieval or clustering.
- Provides `save_model`/`load_model` helpers so trained weights and tokenizers can be persisted and reloaded across workers.

## Prerequisites

- Python 3.10 or newer.
- PyTorch with CUDA support if you plan to train on GPU (the class falls back to CPU automatically).
- Access to the Hugging Face model hub for downloading `embedding_name`. Set `HF_HOME`, proxies, or tokens if your environment requires authentication.
- Enough disk space to cache the chosen MLM (e.g., `bert-base-uncased` ~420 MB).

## Installation

```bash
# pip
pip install swarmauri_embedding_mlm

# poetry
poetry add swarmauri_embedding_mlm

# uv (pyproject-based projects)
uv add swarmauri_embedding_mlm
```

## Quickstart: Fine-tune and Embed Documents

```python
from swarmauri_embedding_mlm import MlmEmbedding

docs = [
    "Swarmauri SDK ships modular agents.",
    "Masked language models produce contextual embeddings.",
]

embedder = MlmEmbedding(
    embedding_name="distilbert-base-uncased",
    batch_size=16,
    learning_rate=3e-5,
)

# One epoch of MLM fine-tuning on your corpus
embedder.fit(docs)

# Generate vectors for downstream tasks
vectors = embedder.transform([
    "Agents coordinate through shared memory",
    "Fine-tuning improves domain recall",
])

for v in vectors:
    print(len(v.value), v.value[:4])  # dimension and preview

# Single-text inference helper
query_vector = embedder.infer_vector("How do masked models compute embeddings?")
```

## Expanding the Vocabulary

Set `add_new_tokens=True` to capture domain-specific terms before training. New tokens are identified via simple whitespace tokenization and appended to the tokenizer before the first epoch.

```python
from swarmauri_embedding_mlm import MlmEmbedding

domain_docs = [
    "Neo4j graph embeddings power fraud detection",
    "Qdrant supports hybrid sparse-dense search",
]

embedder = MlmEmbedding(add_new_tokens=True)
embedder.fit(domain_docs)

# Inspect the tokenizer to confirm additions
print(f"Vocabulary size: {len(embedder.extract_features())}")
```

## Persisting and Reloading Models

```python
from pathlib import Path
from swarmauri_embedding_mlm import MlmEmbedding

save_dir = Path("models/mlm-distilbert")

embedder = MlmEmbedding()
embedder.fit(["short corpus", "to warm up the model"])
embedder.save_model(save_dir.as_posix())

# Later or on another machine
restored = MlmEmbedding()
restored.load_model(save_dir.as_posix())

embedding = restored.infer_vector("Reuse the trained weights instantly")
```

## Operational Tips

- Batch and sequence length drive GPU memory usage; reduce `batch_size` or `max_length` in tokenizer calls when running on constrained hardware.
- `fit_transform` runs a full fine-tuning pass and immediately returns embeddings—useful for one-off adaptation jobs.
- When training on large corpora, stream documents from a generator, chunk them, or wrap the `.fit` call in your own epoch loop.
- Run `extract_features()` to audit the tokenizer vocabulary (helpful when debugging domain token coverage).
- Combine the generated vectors with Swarmauri vector stores (Redis, Qdrant, etc.) to build end-to-end retrieval pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
