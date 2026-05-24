![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_bertembedding/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_bertembedding/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_bertembedding/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_bertembedding.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_bertembedding" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_bertembedding?label=swarmauri_parser_bertembedding&color=green" alt="PyPI - swarmauri_parser_bertembedding"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser Bert Embedding

`swarmauri_parser_bertembedding` is the Swarmauri embedding parser for turning
text into dense vector representations with Hugging Face BERT models. It
returns Swarmauri `Document` objects whose `content` keeps the original text
and whose metadata stores the generated embedding vector.

## Why Use Swarmauri Parser Bert Embedding

- Generate dense semantic vectors inside a Swarmauri parser-style workflow.
- Keep original text and embedding output together in a single `Document`
  object.
- Swap BERT model names when you need a different encoder surface.
- Feed embeddings into retrieval, clustering, semantic search, reranking, or
  downstream vector store pipelines.

## FAQ

> **What does this parser output?**  
> Swarmauri `Document` objects containing the original text and an averaged BERT
> embedding stored in `metadata["embedding"]`.

> **What model does it use by default?**  
> `bert-base-uncased`.

> **Can it parse a batch of strings?**  
> Yes. The current implementation accepts a single string or a list of strings.

> **Does it download model weights?**  
> Yes. On first use, Hugging Face model and tokenizer assets are downloaded if
> they are not already cached locally.

## Features

- Dense embedding generation using `BertTokenizer` and `BertModel`.
- Supports single-string and batch-text parsing.
- Stores the original text alongside the embedding vector in each document.
- Uses inference mode with `torch.no_grad()` and mean token pooling.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_bertembedding
```

```bash
pip install swarmauri_parser_bertembedding
```

Notes:

- First-run model downloads come from Hugging Face.
- Install a CUDA-enabled PyTorch build separately if GPU execution is required.

## Usage

```python
from swarmauri_parser_bertembedding import BERTEmbeddingParser

parser = BERTEmbeddingParser(parser_model_name="bert-base-uncased")
documents = parser.parse(
    [
        "Swarmauri agents cooperate over shared memory.",
        "Dense embeddings power semantic search.",
    ]
)

for document in documents:
    embedding = document.metadata["embedding"]
    print(document.content)
    print(len(embedding), embedding[:5])
```

## Examples

### Embed a single sentence

```python
from swarmauri_parser_bertembedding import BERTEmbeddingParser

parser = BERTEmbeddingParser()
documents = parser.parse("Composable intelligence infrastructure")

print(documents[0].id)
print(documents[0].metadata["source"])
print(documents[0].metadata["embedding"].shape)
```

### Embed a batch for downstream storage

```python
from swarmauri_parser_bertembedding import BERTEmbeddingParser

texts = [
    "Customer support workflows need retrieval.",
    "Embeddings support semantic matching.",
    "Vector stores preserve nearest-neighbor search state.",
]

parser = BERTEmbeddingParser()
documents = parser.parse(texts)

for document in documents:
    vector = document.metadata["embedding"]
    print(document.id, len(vector))
```

### Use an alternate BERT model name

```python
from swarmauri_parser_bertembedding import BERTEmbeddingParser

parser = BERTEmbeddingParser(parser_model_name="bert-base-multilingual-cased")
docs = parser.parse("Bonjour tout le monde")
print(docs[0].metadata["embedding"][:5])
```

## Related Packages

- [swarmauri_embedding_mlm](https://pypi.org/project/swarmauri_embedding_mlm/)
- [swarmauri_vectorstore_mlm](https://pypi.org/project/swarmauri_vectorstore_mlm/)
- [swarmauri_vectorstore_qdrant](https://pypi.org/project/swarmauri_vectorstore_qdrant/)
- [swarmauri_vectorstore_pinecone](https://pypi.org/project/swarmauri_vectorstore_pinecone/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Hugging Face Transformers BERT docs](https://huggingface.co/docs/transformers/model_doc/bert)
- [Transformers AutoTokenizer and tokenization docs](https://huggingface.co/docs/transformers/main_classes/tokenizer)
- [PyTorch documentation](https://pytorch.org/docs/stable/index.html)

## Best Practices

- Chunk very long texts before parsing so they stay within the BERT token limit.
- Cache Hugging Face assets in CI and deployment environments to avoid repeated
  model downloads.
- Use a model variant aligned to your language and domain.
- Persist vectors into a Swarmauri vector store if you plan to search or reuse
  them beyond a single process.

## License

This project is licensed under the Apache-2.0 License.


