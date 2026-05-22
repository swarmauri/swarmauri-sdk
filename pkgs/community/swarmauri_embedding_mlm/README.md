![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_embedding_mlm/">
        <img src="https://static.pepy.tech/badge/swarmauri_embedding_mlm/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_embedding_mlm/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_embedding_mlm.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_mlm" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_mlm?label=swarmauri_embedding_mlm&color=green" alt="PyPI - swarmauri_embedding_mlm"/></a>
</p>

# Swarmauri MLM Embedding

`swarmauri_embedding_mlm` provides `MlmEmbedding`, a Swarmauri embedding component built on Hugging Face `transformers` and PyTorch masked language models. It can fine-tune a masked language model on local text, optionally expand the tokenizer vocabulary, and return Swarmauri `Vector` objects for retrieval, clustering, similarity search, and downstream agent memory workflows.

## Why Swarmauri MLM Embedding?

Use this package when you want a trainable embedding adapter inside the Swarmauri component system instead of a fixed API-only embedding provider. `MlmEmbedding` keeps model loading, masking, fine-tuning, pooling, vector wrapping, and save/load behavior behind the shared `EmbeddingBase` interface so it can plug into Swarmauri vector stores and retrieval pipelines.

## FAQ

### Q: Which models can this package load?

A: `MlmEmbedding` uses `AutoTokenizer.from_pretrained()` and `AutoModelForMaskedLM.from_pretrained()`, so use a Hugging Face model compatible with masked language modeling, such as BERT-style or DistilBERT-style models.

### Q: Does `fit()` train a complete embedding model from scratch?

A: No. It fine-tunes an existing masked language model for one pass per `fit()` call using masked-token loss, AdamW, and the configured batch size and learning rate.

### Q: What does `transform()` return?

A: It returns a list of Swarmauri `Vector` objects. The current implementation mean-pools model outputs and falls back to mean-pooled logits when the masked-language-model output does not expose `last_hidden_state`.

### Q: Can I persist a tuned model?

A: Yes. Use `save_model(path)` to write the model and tokenizer, then `load_model(path)` to restore them later.

## Features

- `MlmEmbedding` registered under the `swarmauri.embeddings` entry point.
- Hugging Face masked-language-model loading through `AutoTokenizer` and `AutoModelForMaskedLM`.
- PyTorch training loop with automatic CUDA or CPU selection.
- Configurable `embedding_name`, `batch_size`, `learning_rate`, `masking_ratio`, and `randomness_ratio`.
- Optional tokenizer vocabulary expansion with `add_new_tokens=True`.
- `fit()`, `transform()`, `fit_transform()`, and `infer_vector()` workflows.
- `save_model()` and `load_model()` helpers for model reuse.
- Swarmauri `Vector` outputs for vector stores and retrieval pipelines.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- PyTorch installed for your target CPU or GPU environment.
- Network access or a local Hugging Face cache for the selected model.
- Enough disk and memory for the selected masked language model.
- Training data as a list of text strings.

## Installation

Install with `uv`:

```bash
uv add swarmauri_embedding_mlm
```

Install with `pip`:

```bash
pip install swarmauri_embedding_mlm
```

## Usage

Fine-tune a masked language model and embed documents:

```python
from swarmauri_embedding_mlm import MlmEmbedding

documents = [
    "Swarmauri components compose agents, memory, and tools.",
    "Masked language models can adapt to domain terminology.",
]

embedder = MlmEmbedding(
    embedding_name="distilbert-base-uncased",
    batch_size=8,
    learning_rate=3e-5,
)

embedder.fit(documents)
vectors = embedder.transform(
    [
        "Agents retrieve context from vector stores.",
        "Domain adaptation improves local vocabulary coverage.",
    ]
)

print(len(vectors))
print(vectors[0].value[:5])
```

Expand the tokenizer vocabulary before fine-tuning:

```python
from swarmauri_embedding_mlm import MlmEmbedding

corpus = [
    "Swarmauri pipelines use composable intelligence infrastructure.",
    "Qdrant and Redis vector stores support retrieval workflows.",
]

embedder = MlmEmbedding(add_new_tokens=True)
embedder.fit(corpus)

print(embedder.epochs)
print(len(embedder.extract_features()))
```

Save and reload a tuned model:

```python
from pathlib import Path

from swarmauri_embedding_mlm import MlmEmbedding

model_dir = Path("models/domain-mlm")

embedder = MlmEmbedding(embedding_name="distilbert-base-uncased")
embedder.fit(["short adaptation corpus"])
embedder.save_model(model_dir.as_posix())

restored = MlmEmbedding(embedding_name=model_dir.as_posix())
vector = restored.infer_vector("reuse the tuned model")

print(len(vector.value))
```

## Related Packages

Embedding and vector packages:

- [swarmauri_embedding_doc2vec](https://pypi.org/project/swarmauri_embedding_doc2vec/)
- [swarmauri_embedding_nmf](https://pypi.org/project/swarmauri_embedding_nmf/)
- [swarmauri_vectorstore_mlm](https://pypi.org/project/swarmauri_vectorstore_mlm/)
- [swarmauri_vectorstore_qdrant](https://pypi.org/project/swarmauri_vectorstore_qdrant/)
- [swarmauri_vectorstore_redis](https://pypi.org/project/swarmauri_vectorstore_redis/)
- [swarmauri_vectorstore_pinecone](https://pypi.org/project/swarmauri_vectorstore_pinecone/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines embedding interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `EmbeddingBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides `Vector`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Pin `embedding_name` to a model you have tested in your deployment environment.
- Pre-download or cache Hugging Face model weights for offline or repeatable builds.
- Use smaller models and smaller batches on memory-constrained machines.
- Save tuned models after adaptation so workers do not repeat fine-tuning.
- Pair generated vectors with a Swarmauri vector store for retrieval-augmented workflows.

## License

Apache-2.0
