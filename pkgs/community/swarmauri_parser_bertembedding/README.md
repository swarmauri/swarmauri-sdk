![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_bertembedding" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_bertembedding/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_bertembedding.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_bertembedding" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_bertembedding" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_bertembedding?label=swarmauri_parser_bertembedding&color=green" alt="PyPI - swarmauri_parser_bertembedding"/></a>
</p>

---

# Swarmauri Parser Bert Embedding

Parser that converts text into embeddings using a Hugging Face BERT encoder. Produces `Document` objects whose metadata carries the averaged token embedding so downstream Swarmauri pipelines can work with dense vectors.

## Features

- Uses `transformers.BertModel` + `BertTokenizer` (default `bert-base-uncased`).
- Accepts single strings or lists of strings and emits `Document` instances with original text and embedding metadata.
- Runs in inference (`eval`) mode with automatic `torch.no_grad()` handling.
- Works on CPU by default; configure PyTorch device settings to leverage GPU.

## Prerequisites

- Python 3.10 or newer.
- PyTorch compatible with your hardware (installed automatically via `transformers` if not present; install CUDA-enabled wheels manually when needed).
- Internet access on first run so Hugging Face downloads tokenizer/model weights (or warm the cache ahead of time).

## Installation

```bash
# pip
pip install swarmauri_parser_bertembedding

# poetry
poetry add swarmauri_parser_bertembedding

# uv (pyproject-based projects)
uv add swarmauri_parser_bertembedding
```

## Quickstart

```python
from swarmauri_parser_bertembedding import BERTEmbeddingParser

parser = BERTEmbeddingParser(parser_model_name="bert-base-uncased")

documents = parser.parse([
    "Swarmauri agents cooperate over shared memory.",
    "Dense embeddings power semantic search.",
])

for doc in documents:
    vector = doc.metadata["embedding"]
    print(doc.content)
    print(len(vector), vector[:5])
```

## Custom Models & Devices

```python
import torch
from swarmauri_parser_bertembedding import BERTEmbeddingParser
from transformers import BertModel

class GPUParser(BERTEmbeddingParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = BertModel.from_pretrained(self.parser_model_name).to("cuda")

parser = GPUParser(parser_model_name="bert-base-multilingual-cased")
parser._model.eval()
```

## Batch Embeddings at Scale

```python
from tqdm import tqdm
from swarmauri_parser_bertembedding import BERTEmbeddingParser

texts = [f"Paragraph {i}" for i in range(1000)]
parser = BERTEmbeddingParser()

batched_docs = []
batch_size = 32
for start in tqdm(range(0, len(texts), batch_size)):
    batch = texts[start:start + batch_size]
    batched_docs.extend(parser.parse(batch))
```

Persist the resulting vectors into Swarmauri vector stores (Redis, Qdrant, etc.) via the metadata field.

## Tips

- Preprocess text to match model expectations (lowercase for uncased BERT, language-specific cleanup for multilingual models).
- For extremely long documents, consider chunking before calling `parse` to respect the 512 token limit.
- Use PyTorch's `to("cuda")` or `to("mps")` to execute on GPUs or Apple silicon accelerators.
- Cache Hugging Face weights in CI/CD environments (`HF_HOME=/cache/hf`) to avoid repeated downloads.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
