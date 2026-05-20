![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_asn1/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_asn1/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_parser_asn1/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_parser_asn1.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_asn1/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_asn1/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_asn1" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_asn1/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_asn1?label=swarmauri_parser_asn1&color=green" alt="PyPI - swarmauri_parser_asn1"/></a>
</p>
---

# swarmauri-asn1

Grammar-driven ASN.1 schema parsing (X.680) + minimal DER decoding (X.690) for `swarmauri-sdk`.
- Parser uses **Lark Earley** (MIT-only path; no standalone LALR).
- Includes a minimal DER TLV decoder covering common UNIVERSAL types, SEQUENCE/SET[/OF], CHOICE, OPTIONAL/DEFAULT, and basic tagging.

## Layout

```
swarmauri_asn1/
  ├─ swarmauri_asn1/
  │  ├─ grammar/asn1.lark
  │  ├─ parser.py
  │  ├─ tool.py
  │  ├─ der_codec.py
  │  ├─ transformer.py
  │  ├─ ir.py
  │  └─ __init__.py
  ├─ specs/Example.asn
  ├─ examples/standalone_decode.py
  └─ examples/data/question.der
```

## Quick demo (standalone)

```bash
python examples/standalone_decode.py
```

Expected output:

```json
{"id": 42, "question": "Hello"}
```

## swarmauri integration

Install into the same environment as `swarmauri-sdk`, then instantiate the parser:

```python
from swarmauri.parsers import ASN1Parser

parser = ASN1Parser(asn1_files=["./specs/Example.asn"])
docs = parser.parse("examples/data/question.der", type_name="Question")
print(docs[0].content)
```

> Ensure you have `swarmauri-sdk` installed; this package registers via entry points.